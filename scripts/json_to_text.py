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
            "Section "
            + section.strip("\n")
            + "\n\tInstructors: "
            + ", ".join(details["instructor"]).replace("\n", " ")
        )
        hour_to_time = {
            1: "08:00 - 08:50",
            2: "09:00 - 09:50",
            3: "10:00 - 10:50",
            4: "11:00 - 11:50",
            5: "12:00 - 12:50",
            6: "13:00 - 13:50",
            7: "14:00 - 14:50",
            8: "15:00 - 15:50",
            9: "16:00 - 16:50",
            10: "17:00 - 17:50",
            11: "18:00 - 18:50",
            12: "19:00 - 19:50",
        }
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
            temp.append(
                "\tRoom: "
                + schedule["room"]
                + "; Days: "
                + ", ".join([day_to_name[day] for day in schedule["days"]])
                + "; Hours: "
                + ", ".join([hour_to_time[hour] for hour in schedule["hours"]])
            )
    course_sections.append(temp)
    course_exams.append(
        [
            "Midsemester Exam: " + str(course["exams"][0]["midsem"]).strip("\n"),
            "Comprehensive Exam: " + str(course["exams"][0]["compre"]).strip("\n"),
        ]
    )
    course_descs.append(course["desc"])
    course_books.append(course.get("books", "No books mentioned"))
course_codes = list(course_codes)
with open("data/courses.txt", "w", encoding="utf-8") as file:
    for i in range(len(course_codes)):
        file.write("Code: " + course_codes[i] + "\n")
        file.write("Name: " + course_names[i] + "\n")
        file.write("Units: " + str(course_units[i]) + "\n")
        file.write("\n".join(course_sections[i]) + "\n")
        file.write("\n".join(course_exams[i]) + "\n")
        file.write("Description: " + course_descs[i] + "\n")
        file.write(
            "Books:\n\t" + "\n".join(course_books[i]).replace("\n", "\n\t") + "\n"
        )
        file.write("-" * 50 + "\n")
