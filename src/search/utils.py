import math
import os
import json
from pathlib import Path
def standard_tf_idf(t_in_d:int, words_in_d:int, document_num:int, document_with_t_num:int):
    return (t_in_d/words_in_d)*math.log10(document_num/document_with_t_num)



def get_title_by_filename(filename:str, folder:str|Path):
    with open(os.path.join(folder, filename), 'r') as file:
        return json.load(file)["title"]



