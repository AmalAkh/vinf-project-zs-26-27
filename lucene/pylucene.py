
import sys
import json
import os
from pathlib import Path

import lucene
from java.nio.file import Paths

from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, TextField, StringField, IntField, LongField, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.search import (
    IndexSearcher,
    BooleanQuery,
    BooleanClause,
    BoostQuery
)
from org.apache.lucene.queryparser.classic import QueryParser



DATA_DIR = Path("/input/joined_data")
INDEX_DIR = Path("/output/index")

# Start Java Virtual Machine
lucene.initVM(vmargs=["-Djava.awt.headless=true"])

# Fields requiring exact matching
EXACT_FIELDS = {
    "id", "country", "categories",
    "info.manufacturer",
    "info.primary_user", "info.status", 
    "info.first_flight", "info.introduction", "info.status"
}

# Numeric fields
INTEGER_FIELDS = {"year", "info.number_built"}

# Text field
TEXT_FIELDS = {
    "info.propulsion", "armament",
    "content_clear"
}

def flatten(data, prefix=""):
    """Convert nested JSON fields into dotted names."""
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            yield from flatten(value, name)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield from flatten(item, name)
                else:
                    yield name, item
        else:
            yield name, value


def create_document(record):
    doc = Document()

    for name, value in flatten(record):
        if value is None or value == "":
            continue

        # Keep compatibility with your original index
        name = {
            "title_key": "id",
            "content_clear": "content"
        }.get(name, name)

        if name in INTEGER_FIELDS:
            try:
                doc.add(IntField(name, int(value), Field.Store.YES))
            except (ValueError, TypeError):
                continue

        elif name == "categories":
            for category in str(value).split("|"):
                category = category.strip()
                if category:
                    doc.add(StringField(
                        name, category, Field.Store.YES
                    ))
                    doc.add(TextField(
                        name+"_not_exact", category, Field.Store.NO
                    ))



        elif name in EXACT_FIELDS:
            doc.add(StringField(name, str(value), Field.Store.YES))

        else:
            doc.add(TextField(name, str(value), Field.Store.YES))

    return doc


def index_documents():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    directory = FSDirectory.open(Paths.get(str(INDEX_DIR)))
    config = IndexWriterConfig(StandardAnalyzer())
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

    writer = IndexWriter(directory, config)
    count = 0

    try:
        for file_path in DATA_DIR.glob("*.json"):
            with file_path.open(encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue

                    record = json.loads(line)
                    writer.addDocument(create_document(record))
                    count += 1

        writer.commit()
    finally:
        writer.close()
        directory.close()

    print(f"Indexed {count} documents.")


def search_documents(query_text):
    directory = FSDirectory.open(Paths.get(str(INDEX_DIR)))
    reader = DirectoryReader.open(directory)

    searcher = IndexSearcher(reader)
    analyzer = StandardAnalyzer()

    title_query = QueryParser("title", analyzer).parse(query_text)
    content_query = QueryParser("content", analyzer).parse(query_text)
    armament_query = QueryParser("armament", analyzer).parse(query_text)
    categories_query = QueryParser("categories", analyzer).parse(query_text)
    categories_not_exact_query = QueryParser("categories_not_exact", analyzer).parse(query_text)

    country_query = QueryParser("country", analyzer).parse(query_text)
    type_query = QueryParser("info.type", analyzer).parse(query_text)




    # Boost title matches
    boosted_title_query = BoostQuery(title_query, 3.0)
    boosted_content_query = BoostQuery(content_query, 0.5)
    boosted_armament_query = BoostQuery(armament_query, 2.0)
    boosted_categories_query = BoostQuery(categories_query, 3.0)
    boosted_categories_not_exact_query = BoostQuery(categories_not_exact_query, 1.5)

    boosted_country_query = BoostQuery(country_query, 2.0)
    boosted_type_query = BoostQuery(type_query, 2.0)





    # Combine both fields
    builder = BooleanQuery.Builder()

    builder.add(
        boosted_title_query,
        BooleanClause.Occur.SHOULD
    )

    builder.add(
        boosted_content_query,
        BooleanClause.Occur.SHOULD
    )

    builder.add(
        boosted_armament_query,
        BooleanClause.Occur.SHOULD
    )

    builder.add(
        boosted_categories_query,
        BooleanClause.Occur.SHOULD
    )

    builder.add(
        boosted_country_query,
        BooleanClause.Occur.SHOULD
    )

    builder.add(
        boosted_type_query,
        BooleanClause.Occur.SHOULD
    )
    builder.add(
        boosted_categories_not_exact_query,
        BooleanClause.Occur.SHOULD
    )

    query = builder.build()

    results = searcher.search(query, 10)

    # Lucene 10 API
    stored_fields = searcher.storedFields()

    print(f"Returned {len(results.scoreDocs)} matching documents.")

    for hit in results.scoreDocs:
        doc = stored_fields.document(hit.doc)

        print("---")

        print("Title:", doc.get("title"))
        print("Categories:", doc.get("categories"))
        print("Country:", doc.get("country"))


        print("Score:", hit.score)
    

    reader.close()
    directory.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py index")
        print('   or: python search.py search "query"')
        sys.exit(1)

    if sys.argv[1] == "index":
        index_documents()
    elif sys.argv[1] == "search" and len(sys.argv) > 2:
        search_documents(" ".join(sys.argv[2:]))
    else:
        print("Invalid command")
        sys.exit(1)
