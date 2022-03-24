from flask import Flask, request, redirect, render_template, flash, session
import requests
import json
from models import connect_db, db, User, Favorite, Favoritelist, Drink
from forms import UserForm, LoginForm, AddToFavorites,FavlistForm, DrinkForm

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
@app.route('/search/ingredient',methods = ['POST'])
def searched_ingredient():
    if request.method == 'POST':
        ingredient = request.form['search-ingredient']
        res = requests.get(f'{BASE_URL}?i={ingredient}')
        val = res.json()
        all_i = val["ingredients"]
        return render_template("cocktail_data.html",all_i=all_i,ingredient=ingredient)

@app.route('/search/ingredient/<type>',methods=['GET', 'POST'])
def get_ingredient(type):
    ingredient = type
    res = requests.get(f'{BASE_URL}?f={ingredient}')
    val = res.json()   
    ingre_list = val["ingredients"]
    return render_template("search_ingredient.html", ingre_list=ingre_list,type=type)

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


@app.route("/favorites")
def show_all_favlists():
    
    favlist = Favoritelist.query.all()
    return render_template("favorites.html", favlist=favlist)


@app.route("/favlists/<int:favlist_id>")
def show_favlist(favlist_id):

    favlist = Favoritelist.query.get_or_404(favlist_id)
    return render_template("favorite.html", favlist=favlist)
 
@app.route("/favlists/add", methods=["GET", "POST"])
def add_favlist():
 
    form = FavlistForm()

    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        new_favlist = Favoritelist(name=name,description=description)
        db.session.add(new_favlist)
        db.session.commit()
        flash(f"Added favlist: {name}")
        return redirect('/favlists/add')
    else:
        return render_template("new_favlist.html", form=form)


@app.route("/drinks")
def show_all_drink():
    """Show list of drink."""

    drinks = Drink.query.all()
    return render_template("drinks.html", drinks=drinks)


@app.route("/drinks/<int:drink_id>")
def show_drink(drink_id):

    drink = Drink.query.get_or_404(drink_id)
    return render_template("drink.html", drink=drink)


@app.route("/drinks/add", methods=["GET", "POST"])
def add_drink():

    form = DrinkForm()

    if form.validate_on_submit():
        name = form.name.data
        category = form.category.data
        drink = Drink(name=name,category=category)
        db.session.add(drink)
        db.session.commit()
        flash(f"Added '{name}' category: {category}")
        return redirect('/drinks/add')
    else:
        return render_template("add_drink.html", form=form)

@app.route("/favlists/<int:favlist_id>/add-drink", methods=["GET", "POST"])
def add_drink_to_favlist(favlist_id):

    favlist = Favoritelist.query.get_or_404(favlist_id)
    form = AddToFavorites()
    curr_on_favlist = [d.id for d in favlist]
    form.song.choices = (db.session.query(Drink.id, Drink.name).filter(Drink.id.notin_(curr_on_favlist)).all())

    if form.validate_on_submit():

        favlist_drink = Favorite(song_id=form.song.data, favlist_id=favlist_id)
        db.session.add(favlist_drink)
        db.session.commit()
        return redirect(f"/favlists/{favlist_id}")

    return render_template("add_drink_list.html",
                             favlist=favlist,
                             form=form)

# @app.route('/favorites')
# def show_favorites(fav_id):
#     if "user_id" not in session:
#         flash("Please login first!", "danger")
#         return redirect('/login')
