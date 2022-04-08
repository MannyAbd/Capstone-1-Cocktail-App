from flask import Flask, request, redirect, render_template, flash, session, jsonify, g
import requests
from models import connect_db, db, User, Drink, AddDrink
from forms import UserForm, LoginForm, DrinkForm, UpdateUserForm
import os
import re
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) or 'sqlite:///cocktail_db'
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Temp23333')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql:///cocktail_db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Temp23333')
connect_db(app)


CURR_USER_KEY = "curr_user"
api_key = 1
BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php"


##############################Helper Functions###############################

def get_name(name):
    res = requests.get(f"{BASE_URL}?s={name}")
    return res.json()['drinks']

def get_drink_id(idDrink):
    if idDrink:
        res = requests.get(f"http://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={idDrink}")
        return res.json()['drinks'][0]
    else:
        return None


def handle_add_drink(user_id, drink_id):
    try:
        added = AddDrink(
            user_id=user_id, drink_id=drink_id)
        db.session.add(added)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        pass

def add_fav(user_id):
    user = User.query.get_or_404(user_id)
    fav = AddDrink.query.filter(
        AddDrink.user_id == user.id).all()
    if len(fav) == 0:
        return None
    else:
        # lst = [drink.id for drink in user.fav]
        lst = []
        for drink in fav:
            resp = get_drink_id(drink.drink_id)
            lst.insert(0, resp)
        return lst
        

def generate_recs(added):
    """Following cocktail-curator: Takes dicts from user page and finds recently added"""
    lst = []
    if added != None:
        for i in added:
            lst.append(i['strIngredient1'])
    else:
        return None

###############################SEARCH ROUTES################################

@app.route('/')
def homepage():
    return render_template('index.html')

##############################SEARCH BY NAME################################

# @app.route('/search',methods = ['POST'])
# def searched_name():
#     """
#     referenced Cocktail-Dictionary
#     Takes data from form to search for drink lists.

#     """
#     if request.method == 'POST':
#         drink = request.form['search-name']
#         try:
#             res = requests.get(f'{BASE_URL}?s={drink}')
#             val = res.json()
#             all_drinks = val["drinks"]
#             return render_template("cocktail_data.html",all_drinks=all_drinks,drink=drink)
#         except:
#             return " <h1> Oops.. We don't have that cocktail </h1>"
@app.route('/search')
def search():
    term = request.args["search-name"]

    res = get_name(term)
    return render_template('/search.html',term=term,res=res)


###########################SEARCH BY FIRST LETTER##########################
alph = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','v','w','y','z']

@app.route('/letters')
def nav_letters():
    return render_template('/drinks/nav_letters.html',alph=alph)

@app.route('/letters/<l>')
def drink_a(l):
    res = requests.get(f"{BASE_URL}", params={'api_key': api_key, 'f': {l}})
    val = res.json()
    drinks = val["drinks"]
    return render_template("/drinks/by_letter.html",drinks=drinks, alph=alph)

@app.route('/searched/<type>',methods=['GET', 'POST'])
def drink_up(type):
    drink = type
    res = requests.get(f'{BASE_URL}?s={drink}')
    val = res.json()   
    drinks = val["drinks"]

    return render_template("/drinks/letter_drink.html", drinks=drinks,drink=drink)

##############################login/register###############################
"""Following Springboard tutorial"""

@app.before_request
def add_user_to_g():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    
    form = UserForm()
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            email=form.email.data
            user = User.register(username, password, email=email)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username or email already in use.  Please pick another')
            return render_template("/users/register.html", form=form)
        do_login(user)
        flash(f"Hello, {user.username}!", "success")
        return redirect("/")
    else:
        return render_template("/users/register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        form.username.errors = ['Invalid username/password.']

    return render_template('/users/login.html', form=form)

@app.route('/logout')
def logout_user():
    do_logout()
    flash("See you next time!", "success")
    return redirect('/')
##############################User Route###############################

@app.route('/users/<int:user_id>')
def show_user_page(user_id):
    if not g.user:
        flash("Please login to view your page", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    adds = add_fav(user_id)
    recs = generate_recs(adds)
    form = UpdateUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash(f"User {user_id} updated", "success")
        return redirect(f'/users/{user.id}')
    return render_template('/users/show.html',user=user, adds=adds,recs=recs, form=form)

@app.route('/users/<int:drink_id>/delete', methods=["POST"])
def remove_drink(drink_id):
    if not g.user:
        flash("Please login first!", "danger")
        return redirect("/")
    fav = AddDrink.query.get_or_404(drink_id)
    db.session.delete(fav)
    db.session.commit()
    flash(f"Deleted {fav.name}")
    return redirect("/")

@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def update_user(user_id):
    if not g.user:
        flash("Please login first!", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    form = UpdateUserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash(f"User {user_id} updated", "success")
        return redirect(f'/users/{user.id}')

    else:
        return render_template("/users/edit.html", form=form)

# @app.route('/users/fav/delete')
##############################loggedIn Route###############################

# @app.route("/drinks")
# def show_all_drink():
#     """Show list of drink."""
#     if not g.user:
#         flash("Please login first!", "danger")
#         return redirect("/")
#     drinks = Drink.query.filter(Drink.user).all()
#     return render_template("/drinks/drinks.html", drinks=drinks)

# @app.route("/drinks/<int:drink_id>")
# def show_drink(drink_id):
#     if not g.user:
#         flash("Please login first!", "danger")
#         return redirect("/")
#     handle_add_drink(g.user.id, drink_id)
#     drinks = get_drink_by_id(drink_id)
#     drink = Drink.query.get_or_404(drink_id)
#     return render_template("/drinks/drink.html", drink=drink, drinks=drinks)

@ app.route('/drinks/<int:drink_id>')
def show_drink_page(drink_id):
    if not g.user:
        flash("Please login first!", "danger")
        return redirect("/")
    handle_add_drink(g.user.id, drink_id)
    user = User.query.get_or_404(g.user.id)
    drink = get_drink_id(drink_id)
    return render_template('/drinks/show.html',user=user,drink=drink)
    
# @app.route("/drinks/add", methods=["GET", "POST"])
# def add_drink():

#     form = DrinkForm()
#     if not g.user:
#         flash("Please login first!", "danger")
#         return redirect("/")

#     if form.validate_on_submit():
#         name = form.name.data
#         instructions = form.instructions.data
#         ingredient1 = form.ingredient1.data
#         ingredient2 = form.ingredient2.data
#         ingredient3 = form.ingredient3.data
#         ingredient4 = form.ingredient4.data
#         ingredient5 = form.ingredient5.data
#         ingredient6 = form.ingredient6.data
#         ingredient7 = form.ingredient7.data
#         ingredient8 = form.ingredient8.data
#         ingredient9 = form.ingredient9.data
#         ingredient10 = form.ingredient10.data

#         drink = Drink(name=name, instructions=instructions, ingredient1 = ingredient1,
#         ingredient2 = ingredient2,
#         ingredient3 = ingredient3,
#         ingredient4 = ingredient4,
#         ingredient5 = ingredient5,
#         ingredient6 = ingredient6,
#         ingredient7 = ingredient7,
#         ingredient8 = ingredient8,
#         ingredient9 = ingredient9,
#         ingredient10 = ingredient10,
#         user_id=g.user.id)

#         db.session.add(drink)
#         db.session.commit()
#         flash(f"Added '{name}'")
#         return redirect('/drinks')
#     else:
#         return render_template("/drinks/add_drink.html", form=form)

# @app.route('/drinks/<int:drink_id>/delete', methods=["POST"])
# def remove_drink(drink_id):
#     if not g.user:
#         flash("Please login first!", "danger")
#         return redirect("/")
#     drink = Drink.query.get_or_404(drink_id)
    
#     db.session.delete(drink)
#     db.session.commit()
#     flash(f"Deleted {drink.name}")
#     return redirect("/drinks")

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

    db.session.commit()
    return jsonify(drink=drink.serialize())

@app.route('/api/drinks/<int:id>', methods=["DELETE"])
def delete_todo(id):
    
    drink = Drink.query.get_or_404(id)
    db.session.delete(drink)
    db.session.commit()
    return jsonify(message="deleted")

