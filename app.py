from json2html import *
from flask import Flask, request, redirect, render_template, flash
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hi'

api_key = 1
BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php"

# res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 's': 'margarita'})

# res = requests.get("https://www.thecocktaildb.com/api/json/v1/1/search.php", params={'api_key': api_key, 's': 'margarita'})
s = 'margarita'

def get_search():
  
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 's': s})
    r = res.json()
    return r
    

@app.route('/')
def homepage():

    return render_template('index.html')

@app.route('/search')
def searched():
    #prints json into a html table
    # t = get_search()
    # search = json2html.convert(json=t)
    search = get_search()

    return render_template('search-drink.html', search=search)
    
    