import re



def extract_links(source:str)->list[str]:
    pattern1 = r'<(a|div)\b[^>]*\s(?:href|data-url)="([^"]*)"[^>]*>([^<]*)</\1>'
    matches1 = re.findall(pattern1, source)

    pattern2 = r'<(a|div)\b[^>]*\s(?:href|data-url)="([^"]*)"\s[^>]*title="([^>"]+)"\s*[^>]*>[\s\S]*?</\1>'
    matches2 = re.findall(pattern2, source, re.DOTALL)
    matches1.extend(matches2)
    return {match[2]:match[1] for match in matches1}

def extract_title(source:str)->str:
    main_pattern = r'<h1[^>]*class="[^">]*"[^>]*><span[^">]*class="[^">]*"[^">]*>(.+)</span></h1>'
    match = re.search(main_pattern, source)
    if match is None:
        fallback_pattern = r'<title[^>]*>(.+?)</title>'
        match = re.search(fallback_pattern, source, re.DOTALL | re.IGNORECASE)
        if match is None:
            return ""
        
    return match.group(1)


def extract_description(source: str) -> tuple[str, str]:
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

    cleaned_parts = []
    for content in matches:
        text = content.replace("\n", " ")
        text = re.sub(r'</?[^>]+\s*/?>', " ", text)
        text = re.sub(r'\s{2,}', ' ', text)
        cleaned_parts.append(text.strip())

    clear_content = " ".join(cleaned_parts)

    return clear_content, raw_content

def extract_variants(source: str):
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

def extract_performance_parameters(source:str):
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


def extract_unit_produced(source:str):
    pattern = (
            r'Total Production:.+ (\d+?) Units'
        )
    
    match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
    
    if match is None:
        return ""
    return match[1]

def extract_operators(source:str):
    pattern = (
        r'<a\s[^>]*'
        r'class="picTrans"[^>]*'
        r'title="[^"]*nation of (?:the )?([^"]+)"'
        r'[^>]*>'
    )
        
    matches = re.findall(pattern, source, re.DOTALL | re.IGNORECASE)
    
    return matches

def extract_roles(source:str):
    pattern = (
        r'<div[^>"]+class="roleContainers[^>"]*">([^>]+)'
        r'</div>'
    )

    matches = re.findall(pattern, source, re.DOTALL | re.IGNORECASE)
        
    return [match.strip() for match in matches]

    
def extract_country_and_year(source:str):
    pattern = (
        r'<h3[^>]*class="[^"]*">\s*([^|>]+?) \| ([^|>]+?)</h3>'
    )
        
    match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
    
    if match is None:
        return "", ""
    return match[1], match[2]

def extract_armament(source:str):
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

def extract_propulsion(source:str):
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


def extract_data(source:str)->dict[str, any]:
    result = dict()
    result["title"] = extract_title(source)

    country, year = extract_country_and_year(source)
    result["year"] = year
    result["country"] = country

    clear_text, raw_desc_content = extract_description(source)
    result["content_clear"] = clear_text
    result["content_raw"] = raw_desc_content


    result["links"] = extract_links(source)
    result["variants"] = extract_variants(source)
    result["paramaters"] = extract_performance_parameters(source)
    result["operators"] = extract_operators(source)
    result["role"] = extract_roles(source)
    result["armament"] = extract_armament(source)
    result["propulsion"] = extract_propulsion(source)


    

    return result


if __name__ == "__main__":
    import json
    
    with open('/Users/amalakhmadinurov/Downloads/Albatros D.II Biplane Fighter.html', "r") as file:
        page_src = file.read()
        data = extract_data(page_src)
        with open("./tmp/result.json", "w+") as result_file:
            json.dump(data, result_file, indent=2)
    
    with open('/Users/amalakhmadinurov/Downloads/Albatros D.II Biplane Fighter.html', "r") as file:
            page_src = file.read()
            print(extract_propulsion(page_src))
            print(extract_links("<a href=\"https://www.militaryfactory.com/aircraft/ww1-airplanes-1918.asp\" title=\"WW1 Aircraft of 1918\">1918</a>"))

    
