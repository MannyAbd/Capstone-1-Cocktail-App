
import re
from flask import Flask, request, redirect, render_template, flash, session
import requests
import json
from models import connect_db, db, User, Favorite
from forms import UserForm, LoginForm

from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cocktail_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = 'hi'

connect_db(app)

api_key = 1
BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php"

##############################SEARCH BY NAME################################

def get_name(s):
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 's': s})
    search = res.json()
    name = search["drinks"]
    return {"name": name}
    
def getty(s):
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 's': s})
    tt = json.loads(res.text)
    return tt
        # print(i["strInstructions"], "\n")
        # print(i["strInstructionsDE"], "\n")
        
        # print(i["strIngredient1"])
        # print(i["strIngredient2"])
        # print(i["strIngredient3"])
        # print(i["strIngredient4"])

###########################SEARCH BY FIRST LETTER############################

def get_letter(f):
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 'f': f})
    search = res.json()
    name = search["drinks"][0]
    return {"name": name}

###########################SEARCH BY INGREDIENT############################

def get_ingredient(i):
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 'i': i})
    search = res.json()
    name = search["ingredients"][0]
    return {"name": name}

###############################SEARCH ROUTES##################################
# @app.route('/drinks')
# def list_drinks():
#     drink_name = getty('vodka')
#     return render_template('list_drink.html', drink_name=drink_name)
@app.route('/')
def homepage():
    return render_template('index.html')

# @app.route('/search')
# def search_name():
#     return render_template('search_drink.html')

@app.route('/search/<type>',methods=['GET', 'POST'])
def cocktail_select(type):
    """ https://github.com/durveshshah/Cocktail-Dictionary/blob/main/main.py#L45"""
    selected_cocktail = type
    if request.method == 'GET':
        new_url = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={selected_cocktail}'
        print('api_url 1', new_url)
        try:
            r = requests.get(new_url)
            data = r.json()
            print('data', data)
            array = data["drinks"]
            return render_template("list_drink.html", array=array,selected_cocktail=selected_cocktail,
                                   )
        except:
            return "Unexpected Error Occurred"

@app.route('/searched/name')
def searched_name():
    drink = request.args['name']
    drink_name = getty(drink)
    return render_template('search_drink.html', drink_name=drink_name)

# @app.route('/searched/letter')
# def searched_letter():
#     drink = request.args['letter']
#     drink_letter = get_letter(drink)
#     return render_template('search_by_letter.html', drink_letter=drink_letter)

@app.route('/searched/ingredient')
def searched_ingredient():
    drink = request.args['name']
    drink_ingredient = get_ingredient(drink)
    return render_template('search_drink.html', drink_ingredient=drink_ingredient)

##############################login/register###############################
"""Following Springboard tutorial"""

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email=form.email.data
        new_user = User.register(username, password, email=email)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            form.email.errors.append('Email already in use.  Use another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect('/')
    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            session["user_id"] = user.id
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('/login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')

##############################loggedIn Route###############################

@app.route('/favorites')
def show_favorites():
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    
    return render_template("favorites.html")


