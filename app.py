import json
import os
import webbrowser

import pdfplumber
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename

from src.quiz_generator import gen_quiz
from src.courses_gpt import chat_bot

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


history = ""


@app.route("/courseGPT", methods=["GET", "POST"])
def courseGPT():
    global history
    if request.method == "POST":
        data = request.json
        data = data["message"]
        reply = chat_bot(data, history)
        history += "\n" + "user input: " + data + "\n" + "answer " + reply
        return jsonify({"message": reply})

    return render_template("courseGPT.html")


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        pdf = request.files["file"]
        path = "files/" + secure_filename(pdf.filename)
        pdf.save(path)
        pdf = pdfplumber.open(path)
        raw_text = ""
        for page in pdf.pages:
            raw_text += page.extract_text()

        topic = request.form["topic"]
        number_of_questions = request.form["number_of_q"]
        question_type = request.form["type"]
        data = gen_quiz(
            raw_text,
            topic,
            number_of_questions,
            "mcq" if question_type == "Multiple Choice" else question_type,
        )
        return render_template(
            "quiz.html",
            topic=topic,
            question_type=question_type,
            data=data,
        )
    question_types = [
        "Multiple Choice",
        "True/False",
        "Fill in the Blank",
        "Short Answer",
        "Long Answer",
    ]
    return render_template("generate_quiz.html", question_types=question_types)


if __name__ == "__main__":
    webbrowser.open("http://localhost:5000")
    app.run()
