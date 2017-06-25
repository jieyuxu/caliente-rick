from flask import Flask, render_template, url_for, request, redirect, session, make_response
from utils import db_manager
import hashlib
import os, sys, random, uuid
import datetime
from httplib2 import Http # The http library to issue REST calls to the oauth api
import json # Json library to handle replies

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    else:
        return render_template("home.html")

@app.route("/authenticate/")
def auth():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("authenticate.html", donor=True)

@app.route("/login/", methods=["POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    else:
        if "login" in request.form:
            email = request.form["email"]
            passw = hashlib.sha512(request.form["password"]).hexdigest()
            result, msg = db_manager.authenticate_user(email, passw)
            if result == True:
                session["user"] = email
                print session["user"]
                return redirect(url_for("dashboard"))
        return render_template("authenticate.html", msg = msg)


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
    if "user" in session:
        session.pop("user")
    return redirect(url_for("home"))

@app.route("/dashboard/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth"))
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

@app.route("/add/", methods=["POST"])
def add():
#       Shelter Name: <input class="form-control" type="text" name="name" required> <br>
# Description: <input class="form-control" type="text" name="des" required> <br>
# Street Address: <input class="form-control" type="text" name="street" required> <br>
# City:  <input class="form-control" type="text" name="city" required> <br>
# State: <input class="form-control" type="text" name="state" required> <br>
# Zip Code: <input class="form-control" type="text" name="zip" required> <br>
# Phone Number: <input class="form-control" type="text" name="num"><br/>

# shelter_info: dictionary
# {"name" : "Example Shelter",
#  "description" : "We are a shelter",
#  "id" : 12345,
#  "address_zip_code" : "10282",
#  "address_state" : "NY",
#  "address_city" : "New York"
#  "address_street" : "345 Chambers St.",
#  "phone number" : "2123123800"
#  "directors" : ["dir1@gmail.com", "dir2@gmail.com"],   //email of users
#  "population" : 50,
#  "needs" : {"tampons" : 50,
#             "pads" : 25,
#             "diapers" : 10}
#  "last_updated" : 2017-06-24 12:55     //datetime object
    if "submit" in request.form:
        shelter = {}
        shelter.update({"name" : request.form["name"]})
        shelter.update({"description" : request.form["des"]})
        shelter.update({"address_zip_code" : request.form["zip"]})
        shelter.update({"address_city" : request.form["city"]})
        shelter.update({"address_state": request.form["state"]})
        shelter.update({"address_street": request.form["street"]})
        shelter.update({"phone_number" : request.form["num"]})
        shelter.update({"population" : request.form["pop"]})
        shelter.update({"directors" : session["user"]})
        shelter.update({"needs" : {}})
        # shelter.update({"last_updated" : db_manager.get_time()})
        # shelter.update({"id" : uuid.uuid4().int})
        sid = db_manager.add_shelter(shelter)
        print sid
        print db_manager.get_shelter(sid)
    return redirect(url_for("dashboard"))

if __name__ == '__main__':
    app.debug = True
    app.run()
