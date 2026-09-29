import requests
import sys
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.crawling.extraction import extract_data
from src.crawling.utils import get_page_source, filter_links, save_list_to_txt, read_txt_as_list, format_links, save_source_to_html, save_parsed_as_json
from src.utils.logging import log

CRAWLER_READ_LINKS_PATH="data/read_links.txt"
CRAWLER_UNREAD_LINKS_PATH="data/unread_links.txt"
CRAWLER_ALL_LINKS_PATH="data/links.txt"
CRAWLER_RAW_DATA_PATH="data/raw_data/"
CRAWLER_PARSED_DATA_PATH="data/parsed/"


class Crawler:
    def __init__(self, timeout:int=15):
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

        
        try:
            page_source = get_page_source(target_link)
            
        except requests.Timeout:
            log("Failed to retrieve source of the page.Request timed out after retries.", "[CRAWLER]", type="warning")
            return []
        
        extracted_data = extract_data(page_source)
        path = save_source_to_html(CRAWLER_RAW_DATA_PATH, page_source, target_link)
        extracted_data["links"] = filter_links(extracted_data["links"], target_link)
        extracted_data["links"] = format_links(extracted_data["links"])

        extract_data["source_link"] = target_link
        
        save_parsed_as_json(CRAWLER_PARSED_DATA_PATH, target_link, extracted_data)

        self._save_read_link(target_link)
        self._save_unread_links(extracted_data["links"].values())

        return extracted_data["links"]
    
    def _crawl_links(self, start_links:list[str]):
        result_links = []
        for link in start_links:
            if not(link in self._read_links):
                log(f"Links read: {len(self._read_links)}", "CRAWLER", type="info")
                log(f"Links left: {len(self._unread_links)}", "CRAWLER", type="info")

                extracted_links = self._crawl_link(link)
                result_links.extend(extracted_links)
                log(f"Delay: {self.timeout}", "CRAWLER", type="info")
                time.sleep(self.timeout)
        return result_links

    def crawl_source(self, source_links:list[str], depth:int=2):
        self._crawl_links(source_links)
        for i in range(1,depth):
            self._crawl_links(self._unread_links.copy())


        
    

if __name__ == "__main__":
    crawler = Crawler()
    print(crawler.crawl_source(["https://www.militaryfactory.com/aircraft/ww1-aircraft.php"]))
        




    