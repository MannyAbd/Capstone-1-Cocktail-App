
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

###############################SEARCH ROUTES################################

@app.route('/')
def homepage():
    return render_template('index.html')

##############################SEARCH BY NAME################################
 
@app.route('/search',methods = ['POST'])
def searched_name():
    """
    referenced Cocktail-Dictionary
    Takes data from form to search for drink lists.

    """
    if request.method == 'POST':
        drink = request.form['search-name']
        res = requests.get(f'{BASE_URL}?s={drink}')
        val = res.json()
        all_drinks = val["drinks"]
        return render_template("cocktail_data.html",all_drinks=all_drinks,drink=drink)

@app.route('/search/<type>',methods=['GET', 'POST'])
def drink_list(type):
    drink = type
    res = requests.get(f'{BASE_URL}?s={drink}')
    val = res.json()   
    drinks = val["drinks"]
    return render_template("list_drink.html", drinks=drinks,drink=drink)


###########################SEARCH BY FIRST LETTER##########################

@app.route('/search/l/',methods = ['POST'])
def searched_letter():
    if request.method == 'POST':
        letter = request.form['search-letter']
        res = requests.get(f'{BASE_URL}?f={letter}')
        val = res.json()
        all_drinks = val["drinks"]
        return render_template("cocktail_data.html",all_drinks=all_drinks,letter=letter)

@app.route('/search/l/<l>',methods=['GET', 'POST'])
def letter_list(l):
    letter = l
    res = requests.get(f'{BASE_URL}?f={letter}')
    val = res.json()   
    drinks = val["drinks"]
    return render_template("list_drink.html", drinks=drinks,letter=letter)


###########################SEARCH BY INGREDIENT############################
@app.route('/search/i/',methods = ['POST'])
def searched_ingredient():
    if request.method == 'POST':
        ingredient = request.form['search-ingredient']
        res = requests.get(f'{BASE_URL}?i={ingredient}')
        val = res.json()
        all_i = val["ingredients"]
        return render_template("search_ingredient.html",all_i=all_i,ingredient=ingredient)

@app.route('/search/i/<type>',methods=['GET', 'POST'])
def get_ingredient(type):
    ingredient = type
    res = requests.get(f'{BASE_URL}?f={ingredient}')
    val = res.json()   
    ingre_list = val["ingredients"]
    return render_template("search_ingredient.html", ingre_list=ingre_list,ingredient=ingredient)

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


