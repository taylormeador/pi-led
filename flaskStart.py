from flask import Flask, render_template
import os

LOCAL = False

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")


# test locally or deploy
if LOCAL:
    app.run(port=500)
else:
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
