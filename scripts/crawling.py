import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.crawling.crawler import Crawler

if __name__ == "__main__":
    crawler = Crawler() 

    crawler.crawl_source(["https://www.militaryfactory.com/aircraft/index.php"])

    
