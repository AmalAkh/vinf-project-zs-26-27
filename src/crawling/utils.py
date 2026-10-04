import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path
import urllib
import uuid
import os
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.utils.logging import log
import json 
from urllib import parse

def get_page_source(url)->str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }
  
    with requests.Session() as session:

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        session.mount("https://", adapter)
        session.mount("http://", adapter)


        response = session.get(
            url=url,
            timeout=(5, 10),
            headers=headers
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if "text/html" not in content_type:
            raise ValueError(f"Unexpected content type: {content_type}")

        return response.text


        
    '''

    driver = webdriver.Chrome()

    driver.get(url)
    return driver.page_source
    '''



BASE_URL = "https://www.militaryfactory.com"


def _filter_link(link: str, current_link: str) -> bool:
    clear_link = link.strip()

    return (
        "aircraft" in clear_link
        and clear_link != ""
        and clear_link != "#"
        and current_link not in clear_link
        and " " not in current_link
    )


def filter_links(links: dict[str, str], current_link: str) -> dict[str, str]:
    return {
        text: link
        for text, link in links.items()
        if _filter_link(link, current_link)
    }


def _format_link(link: str) -> str:
    if link.startswith("/"):
        return parse.urljoin(BASE_URL, link)
    return link


def format_links(links: dict[str, str]) -> dict[str, str]:
    return {
        text: _format_link(link)
        for text, link in links.items()
    }

def save_list_to_txt(list:list[str]|set[str], path:str|Path):

    with open(path, "w+") as file:
        file.write("\n".join(list).replace("\n\n", "\n"))

def read_txt_as_list(path:str|Path)->list[str]:
    with open(path, "a+") as file:
        file.seek(0)
        lines = []
        for line in file.readlines():
            lines.append(line.replace("\n", ""))
        return lines

def build_filename_from_link(link:str):
    id = link.replace(BASE_URL, "")
    id = re.sub(r"(\.php)|(\.html)", "", id)
    id = re.sub(r"[\W_]", "_", id)
    id = re.sub(r"^_", "", id)
    return id

def save_source_to_html(folder:Path|str, source:str, link:str)->tuple[str,str]:
    id = build_filename_from_link(link)
    path = os.path.join(folder, id+".html")
    with open(path, "w+") as file:
        file.write(source)
    return id, path

def load_html_source(path:Path|str, source:str):
    with open(path, "w+") as file:
        return file.read(source)

def save_parsed_as_json(folder:Path|str,original_link:str, data:dict[str,any]):
    id = build_filename_from_link(original_link)
    path = os.path.join(folder, id+".json")
    with open(path, "w+") as file:
        json.dump(data, file, indent=2)
    return id

