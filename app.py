from flask import Flask, render_template
import os

LOCAL = False

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    return render_template("login.html")


if LOCAL:
    app.debug = True
    app.run(port=5000)
