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

if __name__ == '__main__':
    app.debug = True
    app.run()
