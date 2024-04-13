from flask import Flask, request, jsonify, render_template,url_for,redirect,flash


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')