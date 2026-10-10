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

class TextIndex:
    def __init__(self, path:str|Path):

        with open(os.path.join(path, "index.json"), "w") as file:
            self.index = json.load(file)
                
        with open(os.path.join(path, "tokens_to_num"), "r") as file:
            self.tokens_to_num = json.load(file)

        with open(os.path.join(path,"num_to_token.json"), "r") as file:
            self.num_to_token = json.load(file)

        with open(os.path.join("document_mapping.json"), "r") as file:
            self.document_mapping = json.load(file)

        with open(os.path.join("reverse_document_mapping.json"), "r") as file:
            self.reverse_document_mapping = json.load(file)
                  

class Indexer:

    def __init__(self, input_path:str, output_path:str):
        self.input_path = input_path
        self.output_path = output_path

        self.token_to_num = dict()
        self.num_to_token = []
        self.document_mapping = []
        self.reverse_document_mapping = []


        self.index_data = {}

    def _index_page(self, page_id:int, text:str):

        tokens = prepare_for_indexing(text)

        for token  in tokens:
            if token not in self.token_to_num:
                token_idx = len(self.num_to_token)
                self.token_to_num[token] = token_idx
                self.num_to_token.append(token)
            else:
                token_idx = self.token_to_num[token]

            if token_idx not in self.index_data:
                self.index_data[token_idx] = {"freq":0, "pages":set()}

            if page_id not in self.index_data[token_idx]:
                self.index_data[token_idx]["pages"].add(page_id)
                self.index_data[token_idx]["freq"]+=tokens.count(token)


    def _sort_index(self):
        pass

    def _create_document_mapping(self, filenames_ids:list[str]):
        sorted_ids = sorted(filenames_ids)
        self._document_mapping = {id:idx for idx, id in enumerate(sorted_ids)}
        self._reverse_document_mapping = [id for _, id in enumerate(sorted_ids)]

    def index(self, save_index:bool=True):
        self._create_document_mapping(os.listdir(self.input_path))
       
        for idx, filename in enumerate(self._reverse_document_mapping):
            with open(os.path.join(self.input_path, filename), 'r', encoding="utf-8") as f:
                try:
                    page = json.load(f)
                except UnicodeDecodeError:
                    print(f"Problem with {idx}")
                    continue

                if page["content_clear"] == "":
                    continue
                
                self._index_page(idx, page["content_clear"])
                
                print(f"Processed: {idx+1}")
        if save_index:
            self.save_index()

    def save_index(self):
       
        with open(os.path.join(self.output_path,"index.json"), "w") as file:
            json.dump(self.index_data, file, indent=2, default=set_default)
        
        with open(os.path.join(self.output_path, "tokens_to_num.json"), "w") as file:
            json.dump(self.token_to_num, file, indent=2)

        with open(os.path.join(self.output_path, "num_to_token.json"), "w") as file:
            json.dump(self.num_to_token, file, indent=2)

        with open(os.path.join(self.output_path,"document_mapping.json"), "w") as file:
            json.dump(self._document_mapping, file, indent=2)

        with open(os.path.join(self.output_path,"reverse_document_mapping.json"), "w") as file:
            json.dump(self._reverse_document_mapping, file, indent=2)
        
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError
if __name__ == "__main__":
    indexer = Indexer("./data/parsed", "./data/index")
    indexer.index()

