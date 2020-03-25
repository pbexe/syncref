import re
import sys

import requests
from bibtexparser.bibdatabase import BibDatabase
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
    print("Loading website")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, timeout=10, headers=headers)
    print("Website loaded. We're in...")    
    print("Trying dublincore")
    # Try getting DOI using dublincore
    soup = BeautifulSoup(r.text, "html.parser")
    meta_tags = soup.find_all("meta")
    for tag in meta_tags:
        name = tag.get("name")
        if name and name.startswith("dc."):
            if name[3:] == "identifier":
                return tag.get("content")
    
    # Resort to regexing the results for a DOI
    print("Trying regex")
    pattern = r"10.\d{4,9}/[-._()/:A-Z0-9]+"
    matches = re.findall(pattern, r.text)
    # Assume the first DOI is the correct one because it is usually close to
    # the top in the metadata
    if matches:
        return matches[0]
    else:
        return None


def parse_meta(url):
    bibtex = {}
    extracted = False
    print("Loading website")
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
    url = sys.argv[1]

    try:
        doi = url2doi(url)
        if doi:
            print(doi)
            print(cn.content_negotiation(ids = doi, format = "bibentry"))
        else:
            print("No results found")
    except Exception as e:
        print(e)        
