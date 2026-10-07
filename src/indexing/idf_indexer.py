import json
import os
from pathlib import Path
import requests
import sys
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.indexing.tokenize import prepare_for_indexing
class Indexer:

    def __init__(self, input_path:str, output_path:str):
        self.input_path = input_path
        self.output_path = output_path

        self.token_to_num = dict()
        self.num_to_token = []
        

        self.index_data = {}

    def _index_page(self, page_name:str, text:str):
        tokens = prepare_for_indexing(text)


        for token  in tokens:
            if token not in self.token_to_num:
                token_idx = len(self.num_to_token)
                self.token_to_num[token] = token_idx
                self.num_to_token.append(token)
            else:
                token_idx = self.token_to_num[token]

            if token_idx not in self.index_data:
                self.index_data[token_idx] = []

            if page_name not in self.index_data[token_idx]:
                self.index_data[token_idx].append(page_name)
            

    def _sort_index(self):
        pass
    def index(self):
        #10.11 and 17.11
        for idx, filename in enumerate(sorted(os.listdir(self.input_path))):
            with open(os.path.join(self.input_path, filename), 'r', encoding="utf-8") as f:
                try:
                    page = json.load(f)
                except UnicodeDecodeError:
                    print(f"Prolbem with {idx}")
                    continue

                if page["content_clear"] == "":
                    continue
                
                self._index_page(filename, page["content_clear"])
                
                print(f"Processed: {idx+1}")
                
        with open("data/indexed/index.json", "w") as file:
            json.dump(self.index_data, file, indent=2)

        with open("data/indexed/tokens_to_num.json", "w") as file:
            json.dump(self.token_to_num, file, indent=2)

if __name__ == "__main__":
    indexer = Indexer("data/parsed", "data/indexed")
    indexer.index()


        
            
