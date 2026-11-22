"""Run basic and Boolean AND searches for each test query using PyLucene."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pylucene


QUERY_FILE = Path(
    os.environ.get("TEST_QUERIES_FILE", "/input/test_queries.txt")
)
OUTPUT_FILE = Path(
    os.environ.get("PYLUCENE_RESULTS_FILE", "/output/pylucene_search_results.txt")
)


def read_queries(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(
            f"Test query file not found: {path}. "
            "Mount data/test_queries.txt at /input/test_queries.txt, "
            "or set TEST_QUERIES_FILE to its container path."
        )
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_search(query: str) -> str:
    captured_output = StringIO()
    with redirect_stdout(captured_output):
        pylucene.search_documents(query)
    return captured_output.getvalue().strip() or "No results."


def and_query(query: str) -> str:
    return " AND ".join(query.split())


def main() -> None:
    queries = read_queries(QUERY_FILE)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    search_modes = (
        ("Basic (default OR)", lambda query: query),
        ("Boolean AND", and_query),
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for query_number, query in enumerate(queries, start=1):
            for mode_name, prepare_query in search_modes:
                lucene_query = prepare_query(query)
                output.write(
                    f"Query {query_number}: {query}\n"
                    f"Query type: {mode_name}\n"
                    f"Submitted query: {lucene_query}\n"
                )
                output.write(run_search(lucene_query))
                output.write("\n\n")

    print(f"PyLucene results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
