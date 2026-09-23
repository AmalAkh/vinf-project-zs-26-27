import re



def extract_links(source:str)->list[str]:
    pattern = r'<(?:a|div).*?(?:href|data-url)="([^"]*)"'
    matches = re.findall(pattern, source)
   
    return matches


if __name__ == "__main__":
    
    print(extract_links("t<a href=\"test\" data-test=\"123\">t</a>t"))
