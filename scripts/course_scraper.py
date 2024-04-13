import requests
import pandas as pd
import pdfplumber
import regex as re
from pprint import pprint


courses={}
pdf = pdfplumber.open("data/bulletin.pdf")
for page in pdf.pages[0:2]:
    text = page.extract_text()
    
    course_names= []
    desc_indexs = []
    course_descriptions =[]
    #get element ending with a number
    i=0
    for line in text.split("\n"):
        if re.search(r"\d$", line):
            course_names.append(line)
            desc_indexs.append(i)
        i+=1
    course_names.pop()
    course_codes = []
    course_text =[]
    for name in course_names:
        course_codes.append(name.split(" ")[0]+" "+name.split(" ")[1])
        course_text.append(" ".join(name.split(" ")[2:]))
    #get course description between two desc_indexs
    for i in range(len(desc_indexs)-1):
        course_descriptions.append(" ".join(text.split("\n")[desc_indexs[i]+1:desc_indexs[i+1]]))

courses['course_codes'] = course_codes
courses['course_names'] = course_text
courses['course_descriptions'] = course_descriptions