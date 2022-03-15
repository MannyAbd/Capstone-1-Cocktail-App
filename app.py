from json2html import *
from flask import Flask, request, redirect, render_template, flash
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hi'

api_key = 1
BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php"

def get_search(s):
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 's': s})
    search = res.json()
    name = search["drinks"][0]
    return {"name": name}

##################################ROUTES####################################

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/search')
def searched():
    drink = request.args['name']
    drink_name = get_search(drink)
    return render_template('index.html', drink_name=drink_name )
