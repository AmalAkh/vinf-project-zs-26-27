import re
from pathlib import Path
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.utils import save_parsed_as_json
from src.utils.logging import log
from src.crawling.utils import filter_links
class Extractor:

    def __init__(self, input_dir:str|Path, output_dir:str|Path):
        self.input_dir = input_dir
        self.output_dir = output_dir

        
    def _extract_links(self, source:str)->list[str]:
        return extract_links(source)

    def _extract_original_link(self, source:str)->str:
        for link_tag in re.finditer(r'<link\b[^>]*>', source, re.IGNORECASE):
            attributes = dict(
                (name.lower(), value)
                for name, value in re.findall(
                    r'([\w:-]+)\s*=\s*["\']([^"\']*)["\']',
                    link_tag.group(0),
                )
            )
            if "canonical" in attributes.get("rel", "").lower().split():
                return attributes.get("href", "")
        return ""

    def _extract_title(self, source:str)->str:
        main_pattern = r'<h1[^>]*class="[^">]*"[^>]*><span[^">]*class="[^">]*"[^">]*>(.+)</span></h1>'
        match = re.search(main_pattern, source)
        if match is None:
            fallback_pattern = r'<title[^>]*>(.+?)</title>'
            match = re.search(fallback_pattern, source, re.DOTALL | re.IGNORECASE)
            if match is None:
                return ""
            
        return match.group(1)


    def _extract_description(self,source: str) -> tuple[str, str]:
        pattern = (
            r'<!--BODYTEXT\d+-->\s*'
            r'<div[^>]*class="[^"]*contentStripOuter[^>]*"[^"]*>.*?'
            r'<span[^>]*class="[^"]*"[^>]*>\s*(.*?)\s*</span>.*?'
            r'<!--BODYTEXT\d+-->\s*'
        )

        

        matches = re.findall(pattern, source, re.DOTALL)

        if not matches:
            return "", ""

        raw_content = " ".join(matches)
        raw_content = re.split(r"<br\s?/>\n<br\s?/>", raw_content)[0]

        clear_content = raw_content.replace("\n", " ")
        clear_content = re.sub(r'</?[^>]+\s*/?>', " ", clear_content)
        clear_content = re.sub(r'\s{2,}', ' ', clear_content).strip()

        return clear_content, raw_content

    def _extract_variants(self,source: str):
        pattern = (
            r'<button[^>]*class="[^"]*collapsible[^"]*picTrans[^"]*"[^>]*>.*?Variants.*?</button>\s*'
            r'<div[^>]*class="[^"]*dropdownContent[^"]*"[^>]*>\s*'
            r'<div[^>]*>\s*'
            r'<span[^>]*class="[^"]*textDkGray[^"]*textNormal"[^>]*>(.*?)</span>'
        )

        match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
        
        if match is None:
            return []
        clearing_pattern = r'</?[^>]+>'
        cleared = re.sub(clearing_pattern,"", match.group(1), 0, re.DOTALL | re.IGNORECASE)
        split_variants = cleared.split("\n")
        return split_variants

    def _extract_performance_parameters(self,source:str):
        pattern = (
            r'<div[^>]*class="specContainerMain[^"]*">\s*'
            r'<span[^>]*class="[^">]*textNormal[^">]*">([^<]+)</span>\s*'
            r'<br\s*/?>\s*'
            r'<span[^>]*class="[^">]*textBold[^">]*">[^<]+</span>\s*'
            r'<br\s*/?>\s*'
            r'<span[^>]*class="[^">]*textNormal[^">]*">\(([^<]+)\)</span>\s*'
            r'</div>'
        )
        matches = re.findall(pattern, source, re.DOTALL | re.IGNORECASE)


        return {match[0]:match[1] for match in matches}


    def _extract_unit_produced(self,source:str):
        pattern = (
                r'Total Production:.+ (\d+?) Units'
            )
        
        match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
        
        if match is None:
            return ""
        return match[1]

    def _extract_operators(self, source:str):
        pattern = (
            r'<a\s[^>]*'
            r'class="picTrans"[^>]*'
            r'title="[^"]*nation of (?:the )?([^"]+)"'
            r'[^>]*>'
        )
            
        matches = re.findall(pattern, source, re.DOTALL | re.IGNORECASE)
        
        return matches

    def _extract_roles(self, source:str):
        pattern = (
            r'<div[^>"]+class="roleContainers[^>"]*">([^>]+)'
            r'</div>'
        )

        matches = re.findall(pattern, source, re.DOTALL | re.IGNORECASE)
            
        return [match.strip() for match in matches]

        
    def _extract_country_and_year(self,source:str):
        pattern = (
            r'<h3[^>]*class="[^"]*">\s*([^|>]+?) \| ([^|>]+?)</h3>'
        )
            
        match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
        
        if match is None:
            return "", ""
        return match[1], match[2]

    def _extract_armament(self, source:str):
        pattern = (
            r'<button[^>]*class="[^"]*collapsible[^"]*picTrans[^"]*"[^>]*>.*?Armament.*?</button>\s*'
            r'<div[^>]*class="[^"]*dropdownContent[^"]*"[^>]*>\s*'
            r'<div[^>]*>\s*'
            r'<span[^>]*class="[^"]*textDkGray[^"]*textNormal"[^>]*>(.*?)</span>'
        )

        match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
        
        if match is None:
            return ""
        clearing_pattern = r'</?[^>]+>'
        cleared = re.sub(clearing_pattern,"", match.group(1), 0, re.DOTALL | re.IGNORECASE)
        return cleared

    def _extract_propulsion(self, source:str):
        pattern = (
                r'<div[^>]*class="[^"]*specContainerMain[^"]*">\s*'
                r'<span[^>]*class="[^">]*">.*?Propulsion.*?</span>\s*'
                r'<br\s*/?>\s*'
                r'<span[^>]*class="[^">]*">\s*([^>]*)\s*</span>'
            )

        match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
        
        if match is None:
            return ""
        clearing_pattern = r'</?[^>]+>'
        cleared = re.sub(clearing_pattern,"", match.group(1), 0, re.DOTALL | re.IGNORECASE)
        return cleared

    def extract_data_from_page(self, page_source:str)->dict[str,any]:
        result = dict()
        result["title"] = self._extract_title(page_source)
    
        country, year = self._extract_country_and_year(page_source)
        result["year"] = year
        result["country"] = country
    
        clear_text, raw_desc_content = self._extract_description(page_source)
        result["content_clear"] = clear_text
        result["content_raw"] = raw_desc_content
    
        result["original_link"] = self._extract_original_link(page_source)
    
        result["links"] = filter_links(self._extract_links(page_source), result["original_link"])
        result["variants"] = self._extract_variants(page_source)
        result["paramaters"] = self._extract_performance_parameters(page_source)
        result["operators"] = self._extract_operators(page_source)
        result["role"] = self._extract_roles(page_source)
        result["armament"] = self._extract_armament(page_source)
        result["propulsion"] = self._extract_propulsion(page_source)

        return result

    def extract_from_source(self):

        log(f"Extracting from {self.input_dir}", "EXTRACTOR")

        for filename in os.listdir(self.input_dir):
            if not filename.startswith("."):
                with open(os.path.join(self.input_dir, filename), 'r') as file:
                    source = file.read()
                    log(f"Extracting from {filename}", "EXTRACTOR")
                    extracted_data = self.extract_data_from_page(source)
                    save_parsed_as_json(self.output_dir, filename.replace(".html", ".json"), extracted_data)
        

def extract_links(source:str)->list[str]:
    pattern1 = r'<(a|div)\b[^>]*\s(?:href|data-url)="([^"]*)"[^>]*>([^<]*)</\1>'
    matches1 = re.findall(pattern1, source)

    pattern2 = r'<(a|div)\b[^>]*\s(?:href|data-url)="([^"]*)"\s[^>]*title="([^>"]+)"\s*[^>]*>[\s\S]*?</\1>'
    matches2 = re.findall(pattern2, source, re.DOTALL)
    matches1.extend(matches2)
    return {match[2]:match[1] for match in matches1}


if __name__ == "__main__":
    import json
    extractor = Extractor("data/raw_data", "data/")
    with open('/Users/amalakhmadinurov/Downloads/Albatros D.II Biplane Fighter.html', "r") as file:
        page_src = file.read()
        data = extractor.extract_data_from_page(page_src)
        with open("./tmp/result.json", "w+") as result_file:
            json.dump(data, result_file, indent=2)
    
  
