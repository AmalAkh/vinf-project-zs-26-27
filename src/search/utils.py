import math
import os
import json
from pathlib import Path
from typing import Literal

TF_MODE = Literal["natural","norm_length", "log", "norm_max", "log_avg", "boolean"]
TF_NORM_MODE = Literal["none","norm_length", "norm_max"]


TF_IDF_NORM_MODE = Literal["none", "euclid"]

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



def compute_tf_idf_score(tfs:dict[int, float],idfs:list[int, float], document_length:int, tf_mode:TF_MODE, tf_norm_mode:TF_NORM_MODE):
    norm_tfs = {}
    if tf_mode == "norm_max":
        max_tf = max(tfs.values())
        for token in tfs:
            norm_tfs[token] = tf_norm_max(tfs[token], max_tf)

    elif tf_mode == "norm_length":
        for token in tfs:
            norm_tfs[token] = tf_norm_length(tfs[token], document_length)
    else:
        norm_tfs = tfs.copy()
        
    
    if tf_mode == "log":
        scores = {
            token: log_tf(tf) * idfs[token]
            for token, tf in norm_tfs.items()
        }

    elif tf_mode == "log_avg":
        avg = sum(tfs.values()) / len(tfs)

        scores = {
            token: log_avg_tf_idf(tf, avg) * idfs[token]
            for token, tf in norm_tfs.items()
        }

    elif tf_mode == "boolean":
        scores = {
            token: 1 * idfs[token]
            for token, tf in norm_tfs.items()
        }

    else:
        scores = {
            token: tf * idfs[token]
            for token, tf in norm_tfs.items()
        }
    return scores


def get_title_by_filename(filename:str, folder:str|Path):
    with open(os.path.join(folder, filename), 'r') as file:
        return json.load(file)["title"]



