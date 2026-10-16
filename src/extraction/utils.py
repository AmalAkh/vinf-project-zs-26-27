import os 
import json
from pathlib import Path

def save_parsed_as_json(folder:Path|str,filename:str, data:dict[str,any]):
    path = os.path.join(folder, filename)
    with open(path, "w+") as file:
        json.dump(data, file, indent=2)
    return id
