import json

import pdfplumber

filepath = "data/textbooks.pdf"

pdf = pdfplumber.open(filepath)
tables = []
for i in pdf.pages:
    tables.extend(i.extract_tables())  # Extract all tables from the pdf

courses = json.load(open("data/courses.json"))

books = {}

for i in tables:
    for j in i:
        try:
            if j[0].startswith("COM COD"):  # Skip headers
                continue
            books[j[1]] = {"course_name": j[2], "books": j[3].split("\n")}
        except:
            print(f"Error in PDF format for row:\n{j}")

json.dump(books, open("data/books.json", "w"), indent=4)

print(len(books), len(courses))
