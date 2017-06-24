import os, sys, random, csv
from flask import Flask, render_template, url_for, request, redirect, session, make_response
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

@app.route("/hauthenticate/")
def shelterlogin():
    return render_template("authenticate.html")

@app.route("/login/")
def login():
    return

if __name__ == '__main__':
    app.debug = True
    app.run()
