import requests
import sys
import os
from pathlib import Path
import uuid
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.crawling.extractor import extract_links
from src.crawling.utils import get_page_source, filter_links, save_list_to_txt, read_txt_as_list, format_links, save_source_to_html

CRAWLER_READ_LINKS_PATH="data/read_links.txt"
CRAWLER_UNREAD_LINKS_PATH="data/unread_links.txt"
CRAWLER_ALL_LINKS_PATH="data/links.txt"
CRAWLER_RAW_DATA_PATH="data/raw_data/"


class Crawler:
    def __init__(self, timeout:int=20):
        self.timeout = timeout

        self._read_links = set(read_txt_as_list(CRAWLER_READ_LINKS_PATH))
        self._unread_links = set(read_txt_as_list(CRAWLER_UNREAD_LINKS_PATH))
        self._all_links = set(read_txt_as_list(CRAWLER_ALL_LINKS_PATH))

    def _save_read_link(self, target_link:str):
        
        self._read_links.add(target_link)
        if target_link in self._unread_links:
            self._unread_links.remove(target_link)

        save_list_to_txt(self._read_links, CRAWLER_READ_LINKS_PATH)
        save_list_to_txt(self._unread_links, CRAWLER_UNREAD_LINKS_PATH)
        save_list_to_txt(self._unread_links | self._read_links, CRAWLER_ALL_LINKS_PATH)

    def _save_unread_links(self, links:list[str]):
        for link in links:
            self._unread_links.add(link)
        save_list_to_txt(self._unread_links, CRAWLER_UNREAD_LINKS_PATH)
        save_list_to_txt(self._unread_links | self._read_links, CRAWLER_ALL_LINKS_PATH)
        


    def _crawl_link(self,target_link:str)->list[str]:

        page_source = get_page_source(target_link)
        path = save_source_to_html(CRAWLER_RAW_DATA_PATH, page_source)
        
        links = extract_links(page_source)
        
        filtered_links = filter_links(links, target_link)
        formatted_links = format_links(filtered_links)

        self._save_read_link(target_link)
        self._save_unread_links(formatted_links)

        return formatted_links
    
    def _crawl_links(self, start_links:list[str]):
        result_links = []
        for link in start_links:
            extracted_links = self._crawl_link(link)
            result_links.extend(extracted_links)

        return result_links

    def crawl_source(self, source_links:list[str], depth:int=3):
        self._crawl_links(source_links)


        
    

if __name__ == "__main__":
    crawler = Crawler()
    print(crawler.crawl_source(["https://www.militaryfactory.com/aircraft/ww1-aircraft.php"]))
        




    