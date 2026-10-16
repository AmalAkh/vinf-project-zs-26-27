import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.extractors import Extractor
if __name__ == "__main__":
    extractor = Extractor("data/raw_data/", "data/parsed/") 

    extractor.extract_from_source()
