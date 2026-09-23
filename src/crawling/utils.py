import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
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

    return "aircraft" in clear_link and clear_link != "#" and not(current_link in clear_link)
        
def filter_links(links:list[str], current_link:str):
    return filter(lambda link: _filter_link(link, current_link), links)