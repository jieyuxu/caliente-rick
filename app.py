import os, sys, random
from flask import Flask, render_template, url_for, request, redirect, session, make_response
from utils import db_manager
import hashlib
#oauth imports and stuff
from httplib2 import Http # The http library to issue REST calls to the oauth api
import json # Json library to handle replies

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config.update(dict( # Make sure the secret key is set for use of the session variable
    SECRET_KEY = 'secret'
    ))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/pauthenticate/")
def donorlogin():
    return render_template("authenticate.html", donor=True)

@app.route("/login/")
def login():
    if request.form["dlogin"]:
        email = request.form["email"]
        passw = hashlib.sha512(request.form["password"]).hexdigest()
        if authenticate_user(email, passw):
            session["donor"] = email
    elif request.form["slogin"]:
        email = request.form["email"]
        passw = hashlib.sha512(request.form["password"]).hexdigest()
        if authenticate_user(email, passw):
            session["shelter"] = email
    else:
        return redirect(url_for("home"))

# user_info: dictionary
# {"email" : "example@gmail.com",
#  "first_name" : "Ex",
#  "last_name" : "Ample"}
#  "password" : "a38jg38vno83oour"
#  "type" : "donor" // "director"
# }
@app.route("/register/")
def register():
    if request.form["register"]:
        user = {}
        user.update({"email" : request.form["email"]})
        user.update({"first_name" : request.form["first"]})
        user.update({"last_name" : request.form["last"]})
        user.update({"password" : request.form["password"]})
        user.update({"type" : request.form["type"]})
        db_manager.add_user(user)
        return url_for("dashboard")
    else:
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.debug = True
    app.run()
