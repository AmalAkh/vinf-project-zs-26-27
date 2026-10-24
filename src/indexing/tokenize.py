
import re


def remove_stop_words(text:str):
    return re.sub(r'\b(?:the\s|a\s|to\s|with\s|as\s|out\s|of\s)\b', '', text, flags=re.IGNORECASE)

def remove_punctuations(text:str):
    return re.sub(r'[\.\,\;\:\?\!\`\'\"\(\)\[\]\{\}\~\_\-]', " ", text)

def remove_double_spaces(text:str):
    return re.sub(r'\s+', ' ', text).strip()


def tokenize(text:str)->list[str]:
    return re.split(r'[\s]', text)

def convert_string_tokens_to_num(string_tokens:list[str], mapping:dict[str,int])->list[int]:
    return [mapping[token] if token in mapping else "" for token in string_tokens]

def prepare_for_indexing(text:str):
    prepared = remove_punctuations(text.lower())
    prepared = remove_stop_words(prepared)
    prepared = remove_double_spaces(prepared)
    #print(prepared)
    return tokenize(prepared)

if __name__ == "__main__":
    print(prepare_for_indexing('Mikoyan MiG-35 (Fulcrum-F)'))
