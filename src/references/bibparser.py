import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

def bib2py(bib_string):
    """Converts BibTeX to a Python object

    Args:
        bib_string (str): The BibTeX string

    Returns:
        List: The BibTeX Python object
    """
    bib_database = bibtexparser.loads(bib_string)
    return bib_database.entries

def py2bib(entries):
    """Converts a Python object to BibTeX

    Args:
        entries (List): The BibTeX Python object

    Returns:
        str: The BibTeX
    """
    db = BibDatabase()
    db.entries = entries
    return bibtexparser.dumps(db)
