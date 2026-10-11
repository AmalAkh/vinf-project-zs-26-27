import json
import os
from pathlib import Path
import requests
import sys
import os
import time
from pathlib import Path
from typing import Literal

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indexing.idf_indexer import TextIndex
from src.indexing.tokenize import prepare_for_indexing, convert_string_tokens_to_num
from src.search.utils import *

TF_IDF_MODE = Literal["standard", "augmented", "cosine"]

class SearchEngine:

    def __init__(self):
        self._index = TextIndex("./data/index")

    
    def search(self, query:str, mode:TF_IDF_MODE = "standard"):
        query_tokens = prepare_for_indexing(query)
        
        numerical_tokens = convert_string_tokens_to_num(query_tokens, self._index.tokens_to_num)
        
        scores = {}
        
        for token in numerical_tokens:
            relevant_documents_ids = self._index.get_documents_with_term(token)
            print(len(relevant_documents_ids))
            print(len(set(relevant_documents_ids)))


            if len(relevant_documents_ids) > 0:
                print(token)
            for id in relevant_documents_ids:
                document = self._index.get_document(id)
                occurances = document.count(token)

                if mode == "standard":
                    score = standard_tf_idf(occurances, len(document), self._index.get_documents_count(), len(relevant_documents_ids))
                elif mode == "augmented":
                    score = augmented_tf_idf(occurances, len(document), self._index.get_documents_count(), len(relevant_documents_ids))
                elif mode == "cosine":
                    score = augmented_tf_idf(occurances, len(document), self._index.get_documents_count(), len(relevant_documents_ids))

                scores[id] = scores.get(id, 0)+score
                
      
        sorted_scores = [(self._index.get_document_filename(id), value)  for id, value in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
        print(sorted_scores)
        return sorted_scores[:100]

if __name__ == "__main__":
    engine = SearchEngine()
    parsed_files_folder = "./data/parsed"
    results = engine.search("soviet aircraft for ground-attack cold war", mode="standard")

    for idx, result in enumerate(results):
        print(f"{idx+1}. {result[1]} {get_title_by_filename(result[0], parsed_files_folder)}")
    print()
