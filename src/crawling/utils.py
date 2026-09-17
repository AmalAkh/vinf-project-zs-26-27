import requests

def download_page_source(url):
    
    res = requests.get(url) 
    source = res.text
    return source