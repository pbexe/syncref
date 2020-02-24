import sys
from difflib import SequenceMatcher
import json

import arxiv
import requests
from bs4 import BeautifulSoup
from habanero import Crossref, cn


def extract(fp):
    """Extracts the BibTex entry for a given PDF file
    
    Arguments:
        fp {File} -- A handle to the PDF file to extract
    
    Raises:
        ExtractionError: An error has occurred when extracting the BibTeX entry
    
    Returns:
        str -- The BibTeX entry
    """
    
    # Prepare the PDF for multipart upload to the server
    files = {"input": fp}
    
    # Upload the file to the server
    r = requests.post("http://localhost:8080/api/processHeaderDocument",
                      files=files)
    title = ""
    print(r.text, file=open("recent.xml", "w"))
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
                a.append(author.persName.forename.string
                         + " " +
                         author.persName.surname.string)
            except AttributeError:
                # print("Not valid author")
                ...
    except AttributeError:
        # print("No authors found")
        ...

    return (title, a)


def query_crossref(title, author):
    """Query Crossref for extracted data
    
    Args:
        title (str): The title of the paper
        author (List(str)): A list of the authors of the paper
    
    Raises:
        ExtractionError: No suitable search criteria extracted
        ExtractionError: No suitable Crossref candidates
        ExtractionError: Crossref returned an error
    
    Returns:
        str: A BibTeX entry for the queried data
    """
    # Search for the paper on Crossref
    cr = Crossref(mailto="miles@budden.net")
    print("Querying Crossref")
    if author and title:
        r = cr.works(query=title + " " + author[0])
    elif title:
        r = cr.works(query=title)
    else:
        raise ExtractionError("No suitable search criteria extracted")
    BibTeX = ""
    print(json.dumps(r), file=open("cn.json", "w"))
    if r["status"] == "ok":
        for result in r["message"]["items"]:
            # If the titles are similar enough
            if "title" in result:
                if SequenceMatcher(None,
                                result["title"][0].upper(),
                                title.upper()).ratio() > 0.9:
                    # If the title is similar enough, perform content negotiaiton
                    BibTeX = cn.content_negotiation(ids = result["DOI"],
                                                    format = "bibentry")
                    return BibTeX
        else:
            raise ExtractionError("No suitable Crossref candidates")
    else:
        raise ExtractionError("Crossref returned an error")


def query_arXiv(title, author):
    """Query arXiv for the extracted data
    
    Args:
        title (str): The title of the paper
        author (List(str)): A list of the authors of the paper
    
    Raises:
        ExtractionError: No suitable search criteria extracted
        ExtractionError: Entry found but no DOI
        ExtractionError: No matches found
    
    Returns:
        str: A BibTeX entry for the queried data
    """
    if author and title:
        results = arxiv.query(title + " " + author[0])
    elif title:
        results = arxiv.query(title)
    else:
        raise ExtractionError("No suitable search criteria extracted")
    for result in results:
        # pprint(result)
        if SequenceMatcher(None,
                        result["title"].upper(),
                        title.upper()).ratio() > 0.9:
            if result["doi"]:
                BibTeX = cn.content_negotiation(ids = result["doi"],
                                                format = "bibentry")
                return BibTeX
            else:
                raise ExtractionError("Entry found but no DOI")
            
    else:
        raise ExtractionError("No matches found")


def content_negotiation(title, author):
    """Attempts to perform contant negotiation on the extracted data
    
    Args:
        title (str): The title of the paper
        author (List(str)): The list of authors of the paper
    
    Raises:
        ExtractionError: No sources returned results
    
    Returns:
        str: A BibTeX entry for the queried data
    """
    try:
        return query_crossref(title, author)
    except ExtractionError:
        try:
            return query_arXiv(title, author)
        except ExtractionError:
            raise ExtractionError("No sources returned results")


class ExtractionError(Exception):
    """Thrown when there is an error extracting
    
    Arguments:
        Exception {Exception} -- The base Python exception
    """
    pass


def pdf2bib(fp):
    """Converts a PDF to a dictionary
    
    Args:
        fp (File): A handle to the PDF
    
    Returns:
        dict: A dictionary as specified at
    https://bibtexparser.readthedocs.io/en/master/tutorial.html#step-2-parse-it
    """
    bib_data = extract(fp)
    return bib2py(data)


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as fp:
        import parser
        from pprint import pprint
        info = extract(fp)
        try:
            data = content_negotiation(*info)
            print(data)
            print("\n\n")
            pprint(parser.bib2py(data))
            print("\n\n")
            print(parser.py2bib(parser.bib2py(data)))
        except ExtractionError as e:
            print(e)
            if info[0] or info[1]:
                print("Extracted info:", info)
            else:
                print("No info extracted")
