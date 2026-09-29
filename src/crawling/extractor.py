import re



def extract_links(source:str)->list[str]:
    pattern1 = r'<(a|div)\b[^>]*\s(?:href|data-url)="([^"]*)"[^>]*>([^<]*)</\1>'
    matches = re.findall(pattern1, source)

    pattern2 = r'<(a|div)\b[^>]*\s(?:href|data-url)="([^"]*)"\s[^>]*title="([^>"]+)"\s*[^>]*>[\s\S]*?</\1>'
    matches2 = re.findall(pattern2, source, re.DOTALL)
    matches.extend(matches2)
    return {match[2]:match[1] for match in matches}

def extract_title(source:str)->str:
    pattern = r'<h1 class="textJumbo"><span class="textBold">(.+)</span></h1>'
    match = re.search(pattern, source)
    if match is None:
        return ""
    return match.group(1)


def extract_description(source:str)->str:
    pattern = r'<div class="contentStripOuter stripBGcolor3">.*?<span class="textLarge textDkGray">\s*(.*?)\s*</span>'
    
    match = re.search(pattern, source, re.DOTALL)
    if match is None:
        return ""
    return match.group(1)

def extract_variants(source: str):
    pattern = (
        r'<button[^>]*class="[^"]*collapsible[^"]*picTrans[^"]*"[^>]*>.*?Variants.*?</button>\s*'
        r'<div[^>]*class="[^"]*dropdownContent[^"]*"[^>]*>\s*'
        r'<div[^>]*>\s*'
        r'<span[^>]*class="[^"]*textDkGray[^"]*textNormal"[^>]*>(.*?)</span>'
    )

    match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
    
    if match is None:
        return ""
    clearing_pattern = r'</?[^>]+>'
    cleared = re.sub(clearing_pattern,"", match.group(1), 0, re.DOTALL | re.IGNORECASE)
    split_variants = cleared.split("\n")
    return split_variants

def extract_performance_parameters(source:str):
    pattern = (
        r'<div[^>]*class="specContainerMain[^"]*">\s*'
        r'<span[^>]*class="textNormal[^">]*">([^<]+)</span>\s*'
        r'<br\s*/?>\s*'
        r'<span[^>]*class="textBold[^">]*">[^<]+</span>\s*'
        r'<br\s*/?>\s*'
        r'<span[^>]*class="textNormal[^">]*">\(([^<]+)\)</span>\s*'
        r'</div>'
    )
    matches = re.findall(pattern, source, re.DOTALL | re.IGNORECASE)
    print(matches)

    return {match[0]:match[1] for match in matches}


def extract_unit_produced(source:str):
    pattern = (
            r'Total Production:.+ (\d+?) Units'
        )
    
    match = re.search(pattern, source, re.DOTALL | re.IGNORECASE)
    
    if match is None:
        return ""
    return match[1]

def extract_data(source:str)->dict[str, any]:
    result = dict()
    result["title"] = extract_title(source)
    result["description"] = extract_description(source)
    result["links"] = extract_links(source)
    result["variants"] = extract_variants(source)
    result["paramaters"] = extract_performance_parameters(source)


    return result



if __name__ == "__main__":
    import json
    
    with open('/Users/amalakhmadinurov/Downloads/WWI Aircraft (1914-1918).html', "r") as file:
        page_src = file.read()
        data = extract_data(page_src)
        with open("./tmp/result.json", "w+") as result_file:
            json.dump(data, result_file, indent=2)
    
    with open('/Users/amalakhmadinurov/Downloads/WWI Aircraft (1914-1918).html', "r") as file:
            page_src = file.read()
            print(extract_links(page_src))

    
