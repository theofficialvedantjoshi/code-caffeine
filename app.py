from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    send_file,
)
import pdfplumber
from werkzeug.utils import secure_filename
import os
from src.quiz_generator import gen_quiz
import json

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        pdf = request.files["file"]
        # parsefile
        path = "files/" + secure_filename(pdf.filename)
        pdf.save(path)
        pdf = pdfplumber.open(path)
        raw_text = ""
        for page in pdf.pages:
            raw_text += page.extract_text()

        topic = request.form["topic"]
        number_of_questions = request.form["number_of_q"]
        question_type = request.form["type"]
        data = gen_quiz(raw_text, topic, number_of_questions, question_type)
        print(data)
        questions = "test"
        answers = "test"
        return render_template(
            "answers.html",
            questions=questions,
            answers=answers,
        )
    question_types = [
        "mcq",
        "True/False",
        "Fill in the Blank",
        "Short Answer",
        "Long Answer",
    ]
    return render_template("quiz.html", question_types=question_types)


if __name__ == "__main__":
    app.run(debug=True)
