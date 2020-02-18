import sys
from difflib import SequenceMatcher

import requests
from bs4 import BeautifulSoup
from habanero import Crossref, cn


def extract(fp):
    files = {"input": fp,
             "consolidateHeader": "1"}
    r = requests.post("http://localhost:8080/api/processHeaderDocument", files=files, data={
        "consolidateHeader": "1"
    })
    title = ""
    
    try:
        soup = BeautifulSoup(r.text, "xml")
        # print("Title:", soup.find("title").string)
        title = soup.find("title").string
    except AttributeError:
        # print("Title not found")
        ...

    a = []
    try:
        authors = soup.find_all("author")
        for author in authors:
            try:
                a.append(author.persName.forename.string + " " + author.persName.surname.string)
            except AttributeError:
                # print("Not valid author")
                ...
    except AttributeError:
        # print("No authors found")
        ...


    cr = Crossref(mailto="miles@budden.net")
    if a:
        r = cr.works(query=title + " " + a[0])
    else:
        r = cr.works(query=title)
    BibTeX = ""
    if r["status"] == "ok":
        for result in r["message"]["items"]:
            # If the titles are similar enough
            if SequenceMatcher(None, result["title"][0].upper(), title.upper()).ratio() > 0.9:
                # print("Result Title:", result["title"][0])
                # print("\n=========================\n")
                # print(cn.content_negotiation(ids = result["DOI"], format = "bibentry"))
                BibTeX = cn.content_negotiation(ids = result["DOI"], format = "bibentry")
                break
        else:
            raise ExtractionError("No matches found")

    else:
        raise ExtractionError("Error with Crossref API")
    return BibTeX

class ExtractionError(Exception):
    pass


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as fp:
        data = extract(fp)
        print(data)
