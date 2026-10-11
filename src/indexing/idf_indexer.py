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

        with open(os.path.join(path, "index.json"), "r") as file:
            self.index = json.load(file)
                
        with open(os.path.join(path, "tokens_to_num.json"), "r") as file:
            self.tokens_to_num = json.load(file)

        with open(os.path.join(path,"num_to_token.json"), "r") as file:
            self.num_to_token = json.load(file)

        with open(os.path.join(path,"document_mapping.json"), "r") as file:
            self.document_mapping = json.load(file)

        with open(os.path.join(path,"reverse_document_mapping.json"), "r") as file:
            self.reverse_document_mapping = json.load(file)

        with open(os.path.join(path,"tokenized.json"), "r") as file:
            self.tokenized_documents = json.load(file)

    def get_documents_with_term(self, token:int)->list[int]:
        try:
            return self.index[str(token)]["pages"]
        except KeyError:
            return []

    def get_document(self, document_id:int)->list[int]:
        return self.tokenized_documents[str(document_id)] 
    
    def get_documents_count(self)->int:
        return len(self.document_mapping.keys())
    
    def get_document_filename(self, id:int)->str:
        return self.reverse_document_mapping[id]

class Indexer:

    def __init__(self, input_path:str, output_path:str):
        self.input_path = input_path
        self.output_path = output_path

        self._token_to_num = dict()
        self._num_to_token = []
        self._document_mapping = []
        self.r_everse_document_mapping = []

        self._tokenized_documents = {}


        self._index_data = {}

    def _index_page(self, page_id:int, text:str):

        tokens = prepare_for_indexing(text)
        num_tokens = []
        for token  in tokens:
            if token not in self._token_to_num:
                token_idx = len(self._num_to_token)
                self._token_to_num[token] = token_idx
                self._num_to_token.append(token)
            else:
                token_idx = self._token_to_num[token]
                
            num_tokens.append(token_idx)

            if token_idx not in self._index_data:
                self._index_data[token_idx] = {"freq":0, "pages":set()}

            if page_id not in self._index_data[token_idx]:
                self._index_data[token_idx]["pages"].add(page_id)
                self._index_data[token_idx]["freq"]+=tokens.count(token)

        self._tokenized_documents[page_id] = num_tokens

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
                
                self._index_page(idx, self._generate_full_text_for_indexing(page))
                
                print(f"Processed: {idx+1}")
        if save_index:
            self.save_index()
    def _generate_full_text_for_indexing(self, record:dict[str,any]):
        return f"{record["title"]} {record["content_clear"]} {'\n'.join(record["variants"])}"
    def save_index(self):
       
        with open(os.path.join(self.output_path,"index.json"), "w") as file:
            json.dump(self._index_data, file, indent=2, default=set_default)
        
        with open(os.path.join(self.output_path, "tokens_to_num.json"), "w") as file:
            json.dump(self._token_to_num, file, indent=2)

        with open(os.path.join(self.output_path, "num_to_token.json"), "w") as file:
            json.dump(self._num_to_token, file, indent=2)

        with open(os.path.join(self.output_path, "document_mapping.json"), "w") as file:
            json.dump(self._document_mapping, file, indent=2)

        with open(os.path.join(self.output_path, "reverse_document_mapping.json"), "w") as file:
            json.dump(self._reverse_document_mapping, file, indent=2)

        with open(os.path.join(self.output_path, "tokenized.json"), "w") as file:
            json.dump(self._tokenized_documents, file, indent=2)
        
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError
if __name__ == "__main__":
    indexer = Indexer("./data/parsed", "./data/index")
    indexer.index()

    index = TextIndex("./data/index")

