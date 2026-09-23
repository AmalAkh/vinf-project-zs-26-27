import requests
from extractor import extract_links
from utils import get_page_source, filter_links

class Crawler:
    def __init__(self, timeout:int=10):
        self.timeout = timeout

    def parse(resume:bool=True):

        for link in []:
            requests.get(link)

    def crawl(self,start_link:str)->list[str]:

        start_page_source = get_page_source(start_link)
        links = extract_links(start_page_source)

        filtered_links = filter_links(links, start_link)

        result_links = [*filtered_links]
        return result_links

if __name__ == "__main__":
    crawler = Crawler()
    print(crawler.crawl("https://www.militaryfactory.com//aircraft/ww1-aircraft.php"))
        




    