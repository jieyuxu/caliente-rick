from flask import Flask, render_template, url_for, request, redirect, session, make_response
from utils import db_manager
import hashlib
import os, sys, random
from httplib2 import Http # The http library to issue REST calls to the oauth api
import json # Json library to handle replies

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/authenticate/")
def auth():
    return render_template("authenticate.html", donor=True)

@app.route("/login/", methods=["POST"])
def login():
    if request.form["login"]:
        email = request.form["email"]
        passw = hashlib.sha512(request.form["password"]).hexdigest()
        print email
        print passw
        result, msg = db_manager.authenticate_user(email, passw)
        print result
        print msg
        if result == True:
            session["user"] = email
            print session["user"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("authenticate.html", msg = msg)
    else:
        return redirect(url_for("home"))

# user_info: dictionary
# {"email" : "example@gmail.com",
#  "first_name" : "Ex",
#  "last_name" : "Ample"}
#  "password" : "a38jg38vno83oour"
#  "type" : "donor" // "director"
# }
@app.route("/register/", methods=["POST"])
def register():
    if request.form["register"]:
        if hashlib.sha512(request.form["password"]).hexdigest() != hashlib.sha512(request.form["cpassword"]).hexdigest():
            return redirect(url_for("auth"), msg = "Passwords don't match.")
        user = {}
        user.update({"email" : request.form["email"]})
        user.update({"first_name" : request.form["first"]})
        user.update({"last_name" : request.form["last"]})
        user.update({"password" : hashlib.sha512(request.form["password"]).hexdigest()})
        user.update({"type" : request.form["type"]})
        db_manager.add_user(user)
        return redirect(url_for("auth"))
    else:
        return redirect(url_for("auth"), msg = "Register failed.")

@app.route("/logout/")
def logout():
    if session["user"]:
        session.pop("user")
    return redirect(url_for("home"))

@app.route("/dashboard/")
def dashboard():
    print db_manager.get_user(session["user"])
    print db_manager.get_user(session["user"])["type"]
    if db_manager.get_user(session["user"])["type"] == None:
        return redirect(url_for("auth"))
    if db_manager.get_user(session["user"])["type"] == "donor":
        return render_template("dashboard.html", donor=True)
    elif db_manager.get_user(session["user"])["type"] == "director":
        return render_template("dashboard.html", director = True)
    else:
        return redirect(url_for("auth"))
if __name__ == '__main__':
    app.debug = True
    app.run()
