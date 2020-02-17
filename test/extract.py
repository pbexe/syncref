from pdfminer.high_level import extract_text_to_fp
from io import StringIO

output_string = StringIO()

with open("better.pdf", "rb") as fp:
    extract_text_to_fp(fp, output_string)

print(output_string.getvalue().strip())
