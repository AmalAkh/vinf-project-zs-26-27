"""Run the custom search engine against the queries in data/test_queries.txt."""

from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.search.engines import SearchEngine
from src.search.utils import get_title_by_filename


QUERY_FILE = PROJECT_ROOT / "data" / "test_queries.txt"
OUTPUT_FILE = PROJECT_ROOT / "data" / "search_results.txt"
PARSED_DATA_DIR = PROJECT_ROOT / "data" / "parsed"

CONFIGURATIONS = (
    ("natural", False),
    ("log", False),
    ("log_avg", False),
    ("log", True),
    ("log_avg", True),
)
QUERY_MODES = ("and", "or")


def read_queries(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    os.chdir(PROJECT_ROOT)
    engine = SearchEngine()
    queries = read_queries(QUERY_FILE)

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for query_number, query in enumerate(queries, start=1):
            for query_mode in QUERY_MODES:
                for tf_mode, use_euclidean in CONFIGURATIONS:
                    results = engine.search(
                        query,
                        query_mode=query_mode,
                        tf_mode=tf_mode,
                        use_cosine=use_euclidean,
                        normalize=False,
                    )

                    normalization = "Euclidean" if use_euclidean else "none"
                    output.write(
                        f"Query {query_number}: {query}\n"
                        f"Mode: {query_mode.upper()} | TF: {tf_mode} | "
                        f"Normalization: {normalization}\n"
                    )

                    if not results:
                        output.write("No results.\n\n")
                        continue

                    for rank, (filename, score) in enumerate(results, start=1):
                        title = get_title_by_filename(filename, PARSED_DATA_DIR)
                        output.write(f"{rank}. {score:.8f} {title}\n")
                    output.write("\n")

    print(f"Search results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
