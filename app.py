from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
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
    return render_template("register.html")

@app.route("/registerauth", methods=["GET", "POST"])
def register_auth_page():
    desired_username = request.form.get("username")
    desired_password = request.form.get("password")
    # check that username is not taken, right length, alphanumeric
    # hash the password
    # store in db
    username_valid, password_valid = False, False
    if 5 <= len(desired_username) <= 15:  # check username length
        if desired_username.isalnum():  # check if username is alphanumeric
            if Users.query.filter_by(username=desired_username).first() is None:  # check if username is unique
                username_valid = True
            else:
                print("username is not unique")
                return render_template("register.html", message="That username is not valid")
        else:
            print("username not alphanumeric")
            return render_template("register.html", message="That username is not valid")
    else:
        print("username wrong length")
        return render_template("register.html", message="That username is not valid")

    if 5 <= len(desired_password) <= 15:  # check password length
        password_valid = True
        password = b"desired_password"
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    else:
        print("password wrong length")
        return render_template("register.html", message="That password is not valid")

    # add the new user to the db
    new_user = Users(username=desired_username, password_hash=hashed_password, date_created=datetime.now())
    db.session.add(new_user)
    db.session.commit()

    return render_template("registerauth.html")


if LOCAL:
    app.debug = True
    app.run(port=5000)

"""
admin = Users(username="tester", password_hash="test", date_created=datetime.now())
db.session.add(admin)
db.session.commit()
"""