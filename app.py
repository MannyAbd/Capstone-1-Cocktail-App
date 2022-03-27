from flask import Flask, request, redirect, render_template, flash, session, jsonify

import requests
from models import connect_db, db, User, Drink
from forms import UserForm, LoginForm, DrinkForm

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

##############################letter route##############################
alph = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','v','w','y','z']

@app.route('/letters')
def nav_letters():
    return render_template('nav_letters.html',alph=alph)

@app.route('/letters/<l>')
def drink_a(l):
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 'f': {l}})
    val = res.json()
    drinks = val["drinks"]
    return render_template("by_letter.html",drinks=drinks, alph=alph)

##############################login/register###############################
"""Following Springboard tutorial"""

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    
    form = UserForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            email=form.email.data
            new_user = User.register(username, password, email=email)

            db.session.add(new_user)
            db.session.commit()

        except IntegrityError:
            form.username.errors.append('Username or email already in use.  Please pick another')
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

        form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')

##############################loggedIn Route###############################

@app.route("/drinks")
def show_all_drink():
    """Show list of drink."""
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    drinks = Drink.query.filter(Drink.user).all()
    return render_template("drinks.html", drinks=drinks)

@app.route("/drinks/<int:drink_id>")
def show_drink(drink_id):

    drink = Drink.query.get_or_404(drink_id)
    return render_template("drink.html", drink=drink)

@app.route("/drinks/add", methods=["GET", "POST"])
def add_drink():

    form = DrinkForm()
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')

    if form.validate_on_submit():
        name = form.name.data
        category = form.category.data
        instructions = form.instructions.data
        ingredient1 = form.ingredient1.data
        ingredient2 = form.ingredient2.data
        ingredient3 = form.ingredient3.data
        ingredient4 = form.ingredient4.data
        ingredient5 = form.ingredient5.data
        ingredient6 = form.ingredient6.data
        ingredient7 = form.ingredient7.data
        ingredient8 = form.ingredient8.data
        ingredient9 = form.ingredient9.data
        ingredient10 = form.ingredient10.data

        drink = Drink(name=name,category=category, instructions=instructions, ingredient1 = ingredient1,
        ingredient2 = ingredient2,
        ingredient3 = ingredient3,
        ingredient4 = ingredient4,
        ingredient5 = ingredient5,
        ingredient6 = ingredient6,
        ingredient7 = ingredient7,
        ingredient8 = ingredient8,
        ingredient9 = ingredient9,
        ingredient10 = ingredient10,

user_id=session['user_id'])
        db.session.add(drink)
        db.session.commit()
        flash(f"Added '{name}'")
        return redirect('/drinks')
    else:
        return render_template("add_drink.html", form=form)

@app.route('/drinks/<int:drink_id>/delete', methods=["POST"])
def remove_drink(drink_id):
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    drink = Drink.query.get_or_404(drink_id)
    db.session.delete(drink)
    db.session.commit()
    flash(f"Deleted {drink.name}")
    return redirect("/drinks")

###############################JSON################################
@app.route('/api/drinks')
def list_drinks():
    all_drinks = [drink.serialize() for drink in Drink.query.all()]
    return jsonify(drinks=all_drinks)

@app.route('/api/drinks/<int:id>')
def get_drink(id):
    drink = Drink.query.get_or_404(id)
    return jsonify(drink=drink.serialize())

@app.route('/api/drinks', methods=["POST"])
def create_drink():
    new_drink = Drink(name=request.json["name"])
    db.session.add(new_drink)
    db.session.commit()
    response_json = jsonify(drink=new_drink.serialize())
    return (response_json, 201)

@app.route('/api/drinks/<int:id>', methods=["PATCH"])
def update_drink(id):
    drink = Drink.query.get_or_404(id)
    drink.name = request.json.get('name', drink.name)
    drink.instructions = request.json.get('instructions', drink.instructions)
    drink.ingredient1 = request.json.get('ingredient1', drink.ingredient1)
    drink.ingredient2 = request.json.get('ingredient2', drink.ingredient2)
    drink.ingredient3 = request.json.get('ingredient3', drink.ingredient3)
    drink.ingredient4 = request.json.get('ingredient4', drink.ingredient4)
    drink.ingredient5 = request.json.get('ingredient5', drink.ingredient5)
    drink.ingredient6 = request.json.get('ingredient6', drink.ingredient6)
    drink.ingredient7 = request.json.get('ingredient7', drink.ingredient7)
    drink.ingredient8 = request.json.get('ingredient8', drink.ingredient8)
    drink.ingredient9 = request.json.get('ingredient9', drink.ingredient9)
    drink.ingredient10 = request.json.get('ingredient10', drink.ingredient10)
    drink.ingredient11 = request.json.get('ingredient11', drink.ingredient11)
    drink.ingredient12 = request.json.get('ingredient12', drink.ingredient12)
    drink.ingredient13 = request.json.get('ingredient13', drink.ingredient13)
    drink.ingredient14 = request.json.get('ingredient14', drink.ingredient14)
    drink.ingredient15 = request.json.get('ingredient15', drink.ingredient15)
    db.session.commit()
    return jsonify(drink=drink.serialize())

@app.route('/api/drinks/<int:id>', methods=["DELETE"])
def delete_todo(id):
    
    drink = Drink.query.get_or_404(id)
    db.session.delete(drink)
    db.session.commit()
    return jsonify(message="deleted")
