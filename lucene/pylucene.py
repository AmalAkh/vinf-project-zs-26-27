
import sys
import json
import os
from pathlib import Path

import lucene
from java.lang import Double
from java.nio.file import Paths
from java.text import NumberFormat
from java.util import HashMap, Locale
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import (
    Document,
    TextField,
    StringField,
    IntField,
    LongField,
    DoublePoint,
    StoredField,
    Field,
)
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause, BoostQuery
from org.apache.lucene.queryparser.flexible.standard import StandardQueryParser
from org.apache.lucene.queryparser.flexible.standard.config import PointsConfig



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
INTEGER_FIELDS = {"year", "info.number_built", ""}
DOUBLE_FIELDS = {
    "maximum_speed_kph",
    "service_ceiling_m",
    "operational_range_km",
    "rate_of_climb_m_per_min",
    "length_m",
    "width_m",
    "height_m",
    "empty_weight_kg",
    "mtow_kg",
}

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

        elif name in DOUBLE_FIELDS:
            try:
                numeric_value = float(value)
                doc.add(DoublePoint(name, numeric_value))
                doc.add(StoredField(name, numeric_value))
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


def create_query_parser(analyzer):
    parser = StandardQueryParser(analyzer)

    number_format = NumberFormat.getInstance(Locale.US)
    points_config_map = HashMap()
    for name in DOUBLE_FIELDS:
        points_config_map.put(name, PointsConfig(number_format, Double.class_))
    parser.setPointsConfigMap(points_config_map)

    return parser


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
    analyzer = EnglishAnalyzer()
    parser = create_query_parser(analyzer)

    field_boosts = {
        "title": 3.0,
        "content": 0.5,
        "armament": 2.0,
        "categories": 3.0,
        "categories_not_exact": 1.5,
        "country": 2.0,
        "info.type": 2.0,
    }
    query_builder = BooleanQuery.Builder()
    for field_name, boost in field_boosts.items():
        field_query = parser.parse(query_text, field_name)
        query_builder.add(
            BoostQuery(field_query, boost),
            BooleanClause.Occur.SHOULD,
        )
    query = query_builder.build()

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
