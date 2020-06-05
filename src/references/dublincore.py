import re
import sys

import requests
from bs4 import BeautifulSoup
from habanero import cn

# from .parser import bib2py


def url2doi(url):
    """Converts from a URL to a DOI
    
    Arguments:
        url {str} -- The URL to convert
    
    Returns:
        str -- The DOI of the paper in the URL
    """
    # Pretend to be a browser because some sites don't like being scraped
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, timeout=10, headers=headers)
    # Try getting DOI using dublincore
    soup = BeautifulSoup(r.text, "html.parser")
    meta_tags = soup.find_all("meta")
    for tag in meta_tags:
        name = tag.get("name")
        if name and name.startswith("dc."):
            if name[3:] == "identifier":
                return tag.get("content")
    
    # Resort to regexing the results for a DOI
    pattern = r"10.\d{4,9}/[-._()/:A-Z0-9]+"
    matches = re.findall(pattern, r.text)
    # Assume the first DOI is the correct one because it is usually close to
    # the top in the metadata
    if matches:
        return matches[0]
    else:
        return None


def parse_meta(url):
    """Extracts metadata from a page's meta tags.

    Args:
        url (str): The URL to parse

    Returns:
        List: The BibTeX result
    """
    bibtex = {}
    extracted = False
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, timeout=10, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    meta_tags = soup.find_all("meta")
    for tag in meta_tags:
        name = tag.get("name")
        if name and ("title" in name):
            bibtex["title"] = tag.get("content")
            extracted = True
        elif name and ("date" in name):
            bibtex["year"] = tag.get("content")[:4]
            extracted = True
        elif name and ("url" in name):
            bibtex["url"] = tag.get("content")
            extracted = True
        elif name and ("arxiv_id" in name):
            bibtex["Eprint"] = "arXiv:" + tag.get("content")
            extracted = True
        elif name and ("author" in name):
            if "author" in bibtex:
                bibtex["author"] += " and " + tag.get("content")
            else:
                bibtex["author"] = tag.get("content")
            extracted = True
    if "title" in bibtex and "year" in bibtex:
        bibtex["ID"] = bibtex["author"].split().pop() + bibtex["year"]
    else:
        bibtex["ID"] = "UNKNOWN"
    bibtex["ENTRYTYPE"] = "misc"
    if extracted:
        return [bibtex]
    return None
    
    
if __name__ == "__main__":
    from bibparser import bib2py
    from pprint import pprint
    from selenium.webdriver.chrome.options import Options
    from selenium import webdriver
    from tqdm import tqdm
    
    file_name = sys.argv[1]
    with open(file_name, "r") as fp:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        db = bib2py(fp.read())
        s = 0
        err = 0
        bar = tqdm(db)
        for entry in bar:
            urls = None
            if "url" in entry:
                urls = entry["url"]
            elif "doi" in entry:
                urls = "https://doi.org/" + entry["doi"]
            else:
                continue
            urls = urls.split(" ")
            for url in urls:
                bar.set_description(f"S:{s} E:{err}")
                try:
                    driver.get(url)
                except Exception as e:
                    continue
                url = driver.current_url
                bibtex = None
                if url:
                    try:
                        # tqdm.write(url, " ", end="")
                        doi = url2doi(url)
                        if doi:
                            bibtex = cn.content_negotiation(ids = doi, format = "bibentry")
                        else:
                            bibtex = parse_meta(url)
                            if bibtex:
                                bibtex = bibtex[0]
                    except Exception as e:
                        # tqdm.write(e, end=" ")
                        pass
                if bibtex:
                    # tqdm.write("SUCCESS")
                    s+=1
                    tqdm.write(str(bibtex))
                else:
                    # tqdm.write("ERROR")
                    err+=1