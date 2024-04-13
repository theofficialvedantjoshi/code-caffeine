import os

import pdfplumber

pdf = pdfplumber.open("data/campbell.pdf")
raw_text = ""
for page in pdf.pages[112:115]:
    raw_text += page.extract_text()
with open("data/campbell.txt", "w", encoding="utf-8") as f:
    f.write(raw_text)
