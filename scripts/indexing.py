import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indexing.idf_indexer import Indexer
if __name__ == "__main__":
    indexer = Indexer("data/raw_data/", "data/parsed/") 

    indexer.index()
