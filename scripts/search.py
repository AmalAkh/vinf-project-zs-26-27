import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.search.engines import SearchEngine
from src.search.utils import  get_title_by_filename
if __name__ == "__main__":
    search_engine = SearchEngine() 
    while True:
        query = input("Search query:")
        results = search_engine.search(query, query_mode="or", tf_mode="log", use_cosine=True, normalize=False)
        parsed_files_folder = "../data/parsed"
        print()
        for idx, result in enumerate(results):
            print(f"{idx+1}. {result[1]:.8f} {get_title_by_filename(result[0], parsed_files_folder)}")
        print()
    
