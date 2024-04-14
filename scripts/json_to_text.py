import json

path = "data/courses.json"
with open(path, "r") as file:
    data = json.load(file)
course_codes = data.keys()
course_units = []
course_names = []
course_sections = []
course_exams = []
course_descs = []
course_books = []
for course_code in course_codes:
    # print(course_code)
    course = data[course_code]
    course_units.append(course["units"])
    course_names.append(course["course_name"])
    temp = []
    for section, details in course["sections"].items():
        temp.append(
            "Section "
            + section
            + " Instructor: "
            + " ".join(details["instructor"])
            + " Room: "
            + str(details["schedule"])
        )
    course_sections.append(temp)
    course_exams.append(
        [
            "mid semester exams " + str(course["exams"][0]["midsem"]),
            "end semester exams " + str(course["exams"][0]["compre"]),
        ]
    )
    course_descs.append(course["desc"])
    course_books.append(course.get("books", "No books mentioned"))
course_codes = list(course_codes)
with open("data/course.txt", "w", encoding="utf-8") as file:
    for i in range(len(course_codes)):
        file.write("Code: " + course_codes[i] + "\n")
        file.write("Name: " + course_names[i] + "\n")
        file.write("Course Units " + str(course_units[i]) + "\n")
        file.write("\n".join(course_sections[i]) + "\n")
        file.write("\n".join(course_exams[i]) + "\n")
        file.write("Course Description: " + course_descs[i] + "\n")
        file.write("Course Books:" + "\n" + "\n".join(course_books[i]) + "\n")
        file.write("\n\n")
