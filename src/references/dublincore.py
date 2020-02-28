import re
import sys

import requests
from bs4 import BeautifulSoup
from habanero import cn


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
        print(matches[0])
        return matches[0]
    else:
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
