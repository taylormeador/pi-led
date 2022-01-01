from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

LOCAL = False

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime)

    def __repr__(self):
        return '<User %r>' % self.username


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    admin = Users(username="tester", password_hash="test", date_created=datetime.now())
    print("starting db.session.add")
    db.session.add(admin)
    print("starting db.session.commit")
    db.session.commit()
    return render_template("register.html")


if LOCAL:
    app.debug = True
    app.run(port=5000)
