from crypt import methods
from urllib import response
from json2html import *
from flask import Flask, request, redirect, render_template, flash
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hi'

api_key = 1
# BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}"
BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php"

def get_search(s):
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 's': s})
    # res = requests.get(BASE_URL)
    search = res.json()
    name = search["drinks"][0]
    return {"name": name}


# res = requests.get("https://www.thecocktaildb.com/api/json/v1/1/search.php", params={'api_key': api_key, 's': 'margarita'})
     ####################routes####################   
@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/search')
def searched():
    #prints json into a html table
    # t = get_search()
    # search = json2html.convert(json=t)
    # term = request.args["drink"]
    # search = get_search()
    drink = request.args['name']
    drink_name = get_search(drink)

    return render_template('index.html', drink_name=drink_name )
