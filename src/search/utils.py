import math
import os
import json
from pathlib import Path


def tf_norm_length(tf:int, document_length:int):
    return (tf/document_length)
def tf_norm_max(tf:int, max:int|float):
    return (tf/max)

def idf(document_num:int, document_with_t_num:int):
    return math.log10(document_num/document_with_t_num)

def tf_idf(tf:float, idf:float):
    return tf*idf

def augmented_tf_idf(tf:float|int, idf:float, a:float=0.5):
    return (a+ (1-a)*tf)*idf

def log_tf(tf:float|int):
    wf = 1+math.log10(tf) if tf > 0 else 0
    return wf

def log_avg_tf_idf(tf:float|int, avg_tf:float):
    return (1+math.log10(tf))/(1+math.log10(avg_tf))






def get_title_by_filename(filename:str, folder:str|Path):
    with open(os.path.join(folder, filename), 'r') as file:
        return json.load(file)["title"]



