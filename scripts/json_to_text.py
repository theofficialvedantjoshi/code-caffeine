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
    course = data[course_code]
    course_units.append(course["units"])
    course_names.append(course["course_name"].strip("\n"))
    temp = []
    for section, details in course["sections"].items():
        temp.append(
            section.strip("\n")
            .replace("L", "Lecture Section L")
            .replace("T", "Tutorial Section T")
            .replace("P", "Practical Section P")
            + "\n\tInstructors: "
            + ", ".join(details["instructor"]).replace("\n", " ")
        )
        day_to_name = {
            "M": "Mon",
            "T": "Tue",
            "W": "Wed",
            "Th": "Thu",
            "F": "Fri",
            "S": "Sat",
            "Su": "Sun",
        }
        for i, schedule in enumerate(details["schedule"]):
            start = schedule["hours"][0] + 7
            end = schedule["hours"][-1] + 7
            time = f"{start:02d}:00 - {end:02d}:50"
            temp.append(
                "\tRoom: "
                + schedule["room"]
                + "; Days: "
                + ", ".join([day_to_name[day] for day in schedule["days"]])
                + "; Time: "
                + time
            )

    course_sections.append(temp)
    course_exams.append(
        [
            "Midsemester Exam: " + str(course["exams"][0]["midsem"]).strip("\n"),
            "Comprehensive Exam: " + str(course["exams"][0]["compre"]).strip("\n"),
        ]
    )
    course_descs.append(course["desc"])
    course_books.append(
        [i.replace("\n", " ") for i in course.get("books", "No books mentioned")]
    )
course_codes = list(course_codes)
with open("data/courses.txt", "w", encoding="utf-8") as file:
    for i in range(len(course_codes)):
        file.write("Course Code: " + course_codes[i] + "\n")
        file.write("Course Name: " + course_names[i].replace("\n", " ") + "\n")
        file.write("Units: " + str(course_units[i]) + "\n")
        file.write("\n".join(course_sections[i]) + "\n")
        file.write("\n".join(course_exams[i]) + "\n")
        file.write("Description: " + course_descs[i] + "\n")
        file.write("Books:\n\t" + "\n\t".join(course_books[i]) + "\n")
        file.write("-" * 50 + "\n\n")
