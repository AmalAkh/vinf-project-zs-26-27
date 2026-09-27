import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path
import urllib
import uuid
import os
import re

def get_page_source(url):
    '''
    res = requests.get(url) 
    print(res.status_code)
    source = res.text
    return source
    '''
    driver = webdriver.Chrome()

    driver.get(url)
    return driver.page_source


def _filter_link(link:str, current_link:str):
    clear_link = link.strip()

    return "aircraft" in clear_link and clear_link != "" and clear_link != "#" and not(current_link in clear_link)
        
def filter_links(links:list[str], current_link:str):
    return filter(lambda link: _filter_link(link, current_link), links)

BASE_URL = "https://www.militaryfactory.com"
def _format_link(link:str):
    if link.startswith("/"):
        return urllib.parse.urljoin(BASE_URL, link)
    else:
        return link
def format_links(links:list[str])->list[str]:
    return list(map(_format_link,links))

def save_list_to_txt(list:list[str]|set[str], path:str|Path):

    with open(path, "w+") as file:
        file.write("\n".join(list))

def read_txt_as_list(path:str|Path)->list[str]:
    with open(path, "a+") as file:
        file.seek(0)
        return file.readlines()



def save_source_to_html(folder:Path|str, source:str, link:str)->tuple[str,str]:
    id = link.replace(BASE_URL, "")
    id = re.sub(r"(\.php)|(\.html)", "", id)
    id = re.sub(r"[\W_]", "_", id)
    id = re.sub(r"^_", "", id)

    
    path = os.path.join(folder, id+".html")
    with open(path, "w+") as file:
        file.write(source)
    return id, path

def load_html_source(path:Path|str, source:str):
    with open(path, "w+") as file:
        return file.read(source)

