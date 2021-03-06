from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import datetime
import bcrypt
import redis
import os

# toggle for local development vs deployment
LOCAL = False

# Flask, db setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.secret_key = "secret"
db = SQLAlchemy(app)

# Configure Redis for storing the session data on the server-side
redis_url = os.getenv("REDISTOGO_URL", "")  # TODO is this right?
redis = redis.from_url(redis_url)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis

# Create and initialize the Flask-Session and Flask-Sockets object AFTER `app` has been configured
server_session = Session(app)

# user db model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime)

    def __repr__(self):
        return f"<User {self.username}>"

# chat app model
class ChatMessages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    message = db.Column(db.String(250))
    date_created = db.Column(db.DateTime, default=datetime)

    def __repr__(self):
        return f"<User {self.username}> <Message {self.message}> <Time {self.time}>"

# raspberry pi db model
class Pis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45))
    requestedChannel = db.Column(db.String(45))

@app.route("/")
def index():
    if "username" not in session:
        redirect(url_for("login"))
    return render_template("index.html")

@app.route("/header")
def header():
    return render_template("header.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:  # if they are already logged in
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
def user():  # this page basically just allows us to see who is currently logged in, if anyone
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
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/draw", methods=["GET", "POST"])
def draw():
    return render_template("draw.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    for i in range(1, 11):  # TODO fix me
        result = db.session.execute(f"SELECT * FROM chat_messages WHERE id = {i}")
        username = result.first()["username"] if not None else ""
        message = result.first()["message"]
        date_time = result.first()["date_created"]
        print(f"{date_time} {username} > {message}")
    return render_template("chat.html")

@app.route("/chatprocess", methods=["GET", "POST"])
def chat_process():
    message = request.form.get("textinput")
    username = ""
    if "username" in session:
        username = session["username"]

    # add the new message to the db
    new_message = ChatMessages(username=username, message=message, date_created=datetime.now())
    db.session.add(new_message)
    db.session.commit()

    return redirect(url_for("chat"))

@app.route("/mypiled", methods=["GET", "POST"])
def my_pi_led():
    return render_template("mypiled.html")

@app.route("/mypiledsubmit", methods=["POST"])
def my_pi_led_submit():
    requested_channel = request.form['channels_dropdown']
    username = request.form['users_dropdown']

    current_user = Pis.query.filter_by(username=username).first()
    current_user.requestedChannel = requested_channel
    db.session.commit()

    return requested_channel + " " + username

@app.route("/mypiledrequest", methods=["GET"])
def my_pi_led_request():
    # incoming request will include username
    # server will look up username in table and return str indicating requestedChannel
    username = request.args['username']
    current_user = Pis.query.filter_by(username=username).first()
    return current_user.requestedChannel

@app.route("/testing", methods=["GET", "POST"])
def testing():
    if request.method == "GET":
        return "Hello, world"


if LOCAL:  # TODO figure out how to do this with environment variables
    app.debug = True
    app.run(port=5000)
