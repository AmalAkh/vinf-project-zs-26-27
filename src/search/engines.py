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

TF_MODE = Literal["natural","norm_length", "log", "norm_max", "log_avg"]
TF_IDF_NORM_MODE = Literal["none", "euclid"]


class SearchEngine:

    def __init__(self):
        self._index = TextIndex("./data/index")

    
    def search(self, query:str, tf_mode:TF_MODE = "natural", normalize:bool=True):
        query_tokens = prepare_for_indexing(query)
        
        numerical_tokens = convert_string_tokens_to_num(query_tokens, self._index.tokens_to_num)
        
        tfs = {}
        idfs = {}
        doc_lenths = {}
        
        for token in numerical_tokens:
            relevant_documents_ids = self._index.get_documents_with_term(token)

            

           
            if len(relevant_documents_ids) > 0:
                print(token)
            for id in relevant_documents_ids:
                document = self._index.get_document(id)
                occurances = document.count(token)

                
                doc_tfs = tfs.get(id, []) 
                doc_tfs.append(occurances)
                tfs[id] = doc_tfs

                doc_idfs = idfs.get(id, []) 
                doc_idfs.append(idf(self._index.get_documents_count(), len(relevant_documents_ids)))
                idfs[id] = doc_idfs

                doc_lenths[id] = len(document)

                
              

        scores = {}
        for id in idfs:
            if tf_mode == "log":
                scores[id] = sum([log_tf(tf)*idf for tf, idf in zip(tfs[id], idfs[id])])
            if tf_mode == "log_avg":
                avg = sum(tfs[id])/len(tfs[id])
                scores[id] = sum([log_avg_tf_idf(tf,  avg)*idf for tf, idf in zip(tfs[id], idfs[id])])
            if tf_mode == "norm_max":
                scores[id] = sum([tf_norm_max(tf,  max(tfs[id]))*idf for tf, idf in zip(tfs[id], idfs[id])])
            if tf_mode == "norm_length":
                scores[id] = sum([tf_norm_length(tf, doc_lenths[id])*idf for tf, idf in zip(tfs[id], idfs[id])])
            else:
                scores[id] = sum([tf*idf for tf, idf in zip(tfs[id], idfs[id])])
    

        sorted_scores = [(self._index.get_document_filename(id), value)  for id, value in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
      
        result = self._remove_duplicated_pages(sorted_scores)
        return result[:10]
    
    def _remove_duplicated_pages(self, scores: list):
        deduplicated_result = []
        seen = set()

        for filename, score in scores:
            normalized = filename.replace("_asp", "")

            if normalized in seen:
                continue

            seen.add(normalized)
            deduplicated_result.append((filename, score))

        return deduplicated_result
    
if __name__ == "__main__":
    engine = SearchEngine()
    parsed_files_folder = "./data/parsed"
    results = engine.search("soviet Fighter jet with NATO codename Fulcrum", tf_mode="log_avg")
    print()
    for idx, result in enumerate(results):
        print(f"{idx+1}. {result[1]} {get_title_by_filename(result[0], parsed_files_folder)}")
    print()
