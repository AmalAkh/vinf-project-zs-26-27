import json
import os
from pathlib import Path
import requests
import sys
import os
import time
from pathlib import Path
from typing import Literal
from collections import Counter
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indexing.idf_indexer import TextIndex
from src.indexing.tokenize import prepare_for_indexing, convert_string_tokens_to_num
from src.search.utils import *

QUERY_MODE = Literal["or", "and"]


class SearchEngine:

    def __init__(self):
        self._index = TextIndex("./data/index")

    
    def search(self, query:str, tf_mode:TF_MODE = "natural", tf_norm_mode:TF_NORM_MODE="none", query_mode:QUERY_MODE="or", use_cosine:bool=False, normalize:bool=True):
        query_tokens = list(set(prepare_for_indexing(query.lower())))
        
        numerical_tokens = convert_string_tokens_to_num(query_tokens, self._index.tokens_to_num)
      
        tfs = {}
        idfs = {}
        doc_lengths = {}

        query_tfs = dict(Counter(numerical_tokens))
        query_idfs = {}

        if query_mode == "and":
            relevant_documents_ids = self._index.get_documents_with_terms_and(numerical_tokens)
        elif query_mode == "or":
            relevant_documents_ids = self._index.get_documents_with_terms_and(numerical_tokens)
        else:
            relevant_documents_ids = self._index.get_documents_with_terms_and(numerical_tokens)


        for token in numerical_tokens:
            
            idf_val = idf(self._index.get_documents_count(), len(self._index.get_documents_with_term(token)))
            query_idfs[token] = idf_val

            for id in relevant_documents_ids:
                document = self._index.get_document(id)
                occurances = document.count(token)

                
                doc_tfs = tfs.get(id, {}) 
                doc_tfs[token] = occurances
                tfs[id] = doc_tfs

                doc_idfs = idfs.get(id, {}) 
                doc_idfs[token] = idf_val
                idfs[id] = doc_idfs

                doc_lengths[id] = len(document)
            
           

        scores = {}
        for doc_id in idfs:
            
            scores[doc_id] = compute_tf_idf_score(tfs[doc_id], idfs[doc_id], doc_lengths[doc_id], tf_mode, tf_norm_mode)

        final_scores = {}
        for id, doc_scores in scores.items():
            if use_cosine:

                query_scores = {
                    token: tf_val * query_idfs[token]
                    for token, tf_val in query_tfs.items()
                }
        
                query_norm = math.sqrt(
                    sum(weight ** 2 for weight in query_scores.values())
                )
                dot_product = sum(
                    query_weight * doc_scores.get(token, 0)
                    for token, query_weight in query_scores.items()
                )

                # Full document magnitude (precomputed during indexing)
                document_norm = math.sqrt(
                    sum(
                        weight**2 for weight in doc_scores
                    )
                )

                if query_norm == 0 or document_norm == 0:
                    final_scores[id] = 0.0
                else:
                    final_scores[id] = (
                        dot_product / (query_norm * document_norm)
                    )
                
            else:
                final_scores[id] = sum(scores[id].values())
                

        sorted_scores = [(self._index.get_document_filename(id), value)  for id, value in sorted(final_scores.items(), key=lambda x:x[1], reverse=True)]
      
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
    results = engine.search("Fighter and Fulcrum-D", tf_mode="log", tf_norm_mode="none", use_cosine=False)
    print()
    for idx, result in enumerate(results):
        print(f"{idx+1}. {result[1]} {get_title_by_filename(result[0], parsed_files_folder)}")
    print()
