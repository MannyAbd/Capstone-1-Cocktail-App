from flask import Flask, request, redirect, render_template, flash

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hi'

BASE_URL = 'www.thecocktaildb.com/api/json/v1/1/search.php?s='

@app.route('/')
def homepage():

    return render_template('index.html')