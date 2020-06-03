import bibtexparser
from bibtexparser.bibdatabase import BibDatabase

def bib2py(bib_string):
    bib_database = bibtexparser.loads(bib_string)
    return bib_database.entries

def py2bib(entries):
    db = BibDatabase()
    db.entries = entries
    return bibtexparser.dumps(db)
