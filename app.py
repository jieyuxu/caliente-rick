from flask import Flask, render_template, url_for, request, redirect, session, make_response
from utils import db_manager
import hashlib
import os, sys, random, uuid
import datetime
from httplib2 import Http # The http library to issue REST calls to the oauth api
import json # Json library to handle replies
import geocoder
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "secret"

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1000)

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
    if "user" in session:
        return redirect(url_for("dashboard"))
    if request.form["register"]:
        if hashlib.sha512(request.form["password"]).hexdigest() != hashlib.sha512(request.form["cpassword"]).hexdigest():
            return redirect(url_for("auth"), msg = "Passwords don't match.")
        user = {}
        user.update({"email" : request.form["email"]})
        user.update({"first_name" : request.form["first"]})
        user.update({"last_name" : request.form["last"]})
        user.update({"password" : hashlib.sha512(request.form["password"]).hexdigest()})
        user.update({"type" : request.form["type"]})
        user.update({"shelters" : []})
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
    usr = db_manager.get_user(session["user"])
    print usr
    if usr["type"] == None:
        return redirect(url_for("auth"))
    if usr["type"] == "donor":
        print "woooooooooooooooooooooooooooooooooo"
        locations = db_manager.get_all_shelters();
        print locations
        return render_template("dashboard.html", donor=True, locations=locations)
    elif usr["type"] == "director":
        print "im inside director"
        ret = []
        info = usr["shelters"]
        print info
        if info == None:
            return render_template("dashboard.html", director = True, msg="No shelters under your account")
        else:
            for code in info:
                print db_manager.get_shelter(code)
                ret.append(db_manager.get_shelter(code))
            print "return is below"
            print ret
            return render_template("dashboard.html", director = True, shelters = ret, geofxn = geocoder.google)
    else:
        return redirect(url_for("auth"))

@app.route("/add/", methods=["POST"])
def add():
    email = session["user"]
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
        addressText = "%s,%s,%s,%s" % (request.form["street"].strip(), request.form["city"].strip(), request.form["state"].strip(),request.form["zip"].strip())
        address = geocoder.google(addressText)
        address = address.latlng

        shelter = {}
        shelter.update({"name" : request.form["name"]})
        shelter.update({"description" : request.form["des"]})
        shelter.update({"address" : {"latitude": address[0], "longitude": address[1], "text" : addressText} })
        shelter.update({"phone_number" : request.form["num"]})
        shelter.update({"population" : request.form["pop"]})
        shelter.update({"directors" : session["user"]})
        shelter.update({"needs" : {}})
        print shelter
        # shelter.update({"last_updated" : db_manager.get_time()})
        # shelter.update({"id" : uuid.uuid4().int})
        db_manager.add_shelter(session["user"], shelter)

    return redirect(url_for("dashboard"))

@app.route("/results/<code>")
def results(code):
    data = db_manager.get_shelter(int(code))
    donations = db_manager.get_donations(int(code))
    print donations
    return render_template("results.html", shelter = data, donations=donations)

@app.route("/request/", methods=["POST"])
def handlerequest():
    if ("request_submit" in request.form) and ("request_name" in request.form) and ("request_amt" in request.form):
        name = request.form["request_name"]
        amt = request.form["request_amt"]
        d = {request.form["request_name"]: request.form["request_amt"]}
        shelter = db_manager.get_shelter(int(request.form["id"]))
        curr = shelter["needs"] #gets dict
        print curr
        if curr == None:
            curr = {}
        print curr
        if name not in curr:
            curr.update({name:amt})
        else:
            for key in curr:
                if key == name:
                    shelter["needs"][key] = amt
        print shelter["needs"]
        print curr
        db_manager.set_shelter_data(int(request.form["id"]), "needs", curr)
        print db_manager.get_shelter(int(request.form["id"]))
    return render_template("results.html", shelter = shelter)

@app.route("/updateinfo/", methods=["POST"])
def updateinfo():
    if "id" not in request.form:
        return redirect(url_for("dashboard"))
    else:
        sid = int(request.form["id"])
        print sid
        shelter = db_manager.get_shelter(sid)
        db_manager.set_shelter_data(sid,"name",request.form["name"])
        db_manager.set_shelter_data(sid,"phone_number",request.form["num"])
        address = request.form["address"]
        latitude, longitude = address.split(",")
        address = {"latitude": latitude, "longitude": longitude}
        # address = geocoder.google(address)
        # address = address.latlng
        db_manager.set_shelter_data(sid,"address",address)
        db_manager.set_shelter_data(sid,"population",request.form["pop"])
        db_manager.set_shelter_data(sid,"email",request.form["email"])
        shelter =  db_manager.get_shelter(int(request.form["id"]))
    return render_template("results.html", shelter = shelter)

@app.route("/seeinfo/", methods=["POST"])
def seeinfo():
    print "see info is running"
    if "id" not in request.form:
        return redirect(url_for("dashboard"))
    else:
        print "i got here"
        sid = int(request.form["id"])
        print sid
        shelter = db_manager.get_shelter(sid)
        usr = db_manager.get_user(session["user"])
    return render_template("view.html", shelter = shelter, usr = usr)

@app.route("/help/", methods=["POST"])
def help():
    sid = int(request.form["id"])
    item = request.form["item"]
    amt = int(request.form["amt"])
    usr = db_manager.get_user(session["user"])
    shelter = db_manager.get_shelter(sid)
    return render_template("help.html", item=item, amt=amt, usr=usr, shelter=shelter)

@app.route("/send/", methods=["POST"])
def send():
    #add_donation(email, shelter_id, product, amount):
    amt = request.form["damt"]
    first = request.form["fname"]
    last = request.form["lname"]
    email = request.form["email"]
    print amt,first,last,email,request.form["id"], request.form["item"]
    db_manager.add_donation(email, int(request.form["id"]), request.form["item"],amt)
    return redirect(url_for("dashboard"))
if __name__ == '__main__':
    app.debug = True
    app.run()
