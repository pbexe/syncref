import sys
from difflib import SequenceMatcher

import requests
from bs4 import BeautifulSoup
from habanero import Crossref, cn


def extract(fp):
    """Extracts the BibTex entry for a given PDF file
    
    Arguments:
        fp {File} -- A hanfle to the PDF file to extract
    
    Raises:
        ExtractionError: An error has occured when extracting the BibTeX entry
    
    Returns:
        str -- The BibTeX entry
    """
    
    # Prepare the PDF for multipart upload to the server
    files = {"input": fp}
    
    # Upload the file to the server
    r = requests.post("http://localhost:8080/api/processHeaderDocument", files=files)
    title = ""
    
    # Try fetching the name and authors from the results
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

    # Search for the paper on Crossref
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
                # If the title is similar enough, perform content negotiaiton
                BibTeX = cn.content_negotiation(ids = result["DOI"], format = "bibentry")
                break
        else:
            raise ExtractionError("No matches found")
    else:
        raise ExtractionError("Error with Crossref API")
    return BibTeX


class ExtractionError(Exception):
    """Thrown when there is an error extracting
    
    Arguments:
        Exception {Exception} -- The base Python exception
    """
    pass


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as fp:
        data = extract(fp)
        print(data)
