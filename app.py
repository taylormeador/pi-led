from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import datetime
import bcrypt
import redis
import os

LOCAL = True

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.secret_key = "secret"
db = SQLAlchemy(app)

# Configure Redis for storing the session data on the server-side
redis_url = os.getenv("REDISTOGO_URL", "redis://redistogo:f0f1515b7afac238d1c451f729388fc3@pearlfish.redistogo.com:10395/")
redis = redis.from_url(redis_url)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis

# Create and initialize the Flask-Session object AFTER `app` has been configured
server_session = Session(app)

# user db model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime)

    def __repr__(self):
        return '<User %r>' % self.username


# global messages
messages = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/header")
def header():
    return render_template("header.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:  # if they are already logged in
        username = session["username"]
        return redirect(url_for("user"))

    return render_template("login.html")

@app.route("/loginauth", methods=["GET", "POST"])
def login_auth():
    # get username/password from form and check against db
    username = request.form.get("username")
    password = request.form.get("password").encode("utf-8")
    username_match = Users.query.filter_by(username=username).first()
    if username_match:
        db_password = username_match.password_hash.encode("utf-8")
        if not bcrypt.checkpw(password, db_password):
            return render_template("login.html", message="wrong username or password, try again")
    else:
        return render_template("login.html", message="wrong username or password, try again")

    session["username"] = username   # store the session data

    return render_template("loginauth.html")

@app.route("/user", methods=["GET", "POST"])
def user():
    if "username" in session:
        username = session["username"]
        return f"<h1>{username}</h1>"
    else:
        return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/registerauth", methods=["GET", "POST"])
def register_auth():
    desired_username = request.form.get("username")
    desired_password = request.form.get("password")
    """
    1. check that username is not taken, right length, alphanumeric, and that the password is right length
    2. hash the password
    3. store in db
    4. if valid, user is redirected to page with a confirmation message
    """
    if 5 <= len(desired_username) <= 15:  # check username length
        if desired_username.isalnum():  # check if username is alphanumeric
            if not Users.query.filter_by(username=desired_username).first() is None:  # check if username is unique
                print("username is not unique")
                return render_template("register.html", message="That username is not valid")
        else:
            print("username not alphanumeric")
            return render_template("register.html", message="That username is not valid")
    else:
        print("username wrong length")
        return render_template("register.html", message="That username is not valid")

    if 5 <= len(desired_password) <= 15:  # check password length
        password = desired_password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    else:
        print("password wrong length")
        return render_template("register.html", message="That password is not valid")

    # add the new user to the db
    new_user = Users(username=desired_username, password_hash=hashed_password, date_created=datetime.now())
    db.session.add(new_user)
    db.session.commit()

    # redirect to new page
    return render_template("registerauth.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():  # TODO sessions won't work with heroku
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/draw", methods=["GET", "POST"])
def draw():
    return render_template("draw.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    return render_template("chat.html", messages=messages)

@app.route("/chatprocess", methods=["GET", "POST"])
def chat_process():
    global messages
    message = request.form.get("textinput")
    ip = request.environ['REMOTE_ADDR']
    formatted_message = f"{ip} > {message}"  # ip > this is the message they typed
    messages.append(formatted_message)
    return redirect(url_for("chat"))


if LOCAL:
    app.debug = True
    app.run(port=5000)
