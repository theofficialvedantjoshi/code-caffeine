import json

import pdfplumber
import regex as re

courses = json.load(open("data/timetable.json"))


def books():
    tables = []
    with pdfplumber.open("data/textbooks.pdf") as pdf:
        for i in pdf.pages:
            tables.extend(i.extract_tables())

    curr_course = None
    curr_books = []
    for i in tables:
        for j in i:
            if j[0].startswith("COM COD"):  # Skip headers
                continue
            if j[1] and j[1] != curr_course:
                curr_course = j[1]
                curr_books = []
                curr_books.append(j[3])
            else:
                curr_books.append(j[3])
            if curr_course:
                courses[curr_course].update({"books": curr_books})


def parse_course_info():
    x0 = 0  # Distance of left side of character from left side of page.
    x1 = 0.5  # Distance of right side of character from left side of page.
    y0 = 0  # Distance of bottom of character from bottom of page.
    y1 = 1  # Distance of top of character from bottom of page.

    all_content = []
    with pdfplumber.open("data/course_info.pdf") as pdf:
        for i, page in enumerate(pdf.pages):
            width = page.width
            height = page.height

            # Crop pages
            left_bbox = (
                x0 * float(width),
                y0 * float(height),
                x1 * float(width),
                y1 * float(height),
            )
            page_crop = page.crop(bbox=left_bbox)
            left_text = page_crop.extract_text()

            left_bbox = (
                0.5 * float(width),
                y0 * float(height),
                1 * float(width),
                y1 * float(height),
            )
            page_crop = page.crop(bbox=left_bbox)
            right_text = page_crop.extract_text()
            page_content = "\n".join([left_text, right_text])
            all_content.append(page_content)

    with open("data/course_info.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(all_content))


def desc():
    with open("data/course_info.txt", "r", encoding="utf-8") as f:
        content = f.read()
    index = 0
    for key in courses.keys():
        course_match = re.search(pattern=f"\n{key} ", string=content, pos=index)
        if not course_match:
            courses[key].update({"desc": ""})
            continue
        desc_start = re.search(pattern="\n", string=content, pos=course_match.end())
        next_course_match = re.search(
            pattern=r"\n[A-Z]{2,5} [A-Z][0-9]{3}",
            string=content,
            pos=course_match.end(),
        )
        desc = content[desc_start.end() : next_course_match.start()]
        index = next_course_match.start()
        courses[key].update({"desc": desc})


if __name__ == "__main__":
    books()
    desc()
    json.dump(courses, open("data/courses.json", "w"), indent=4)
