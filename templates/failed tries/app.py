
from flask import Flask, request, redirect, render_template, flash, session
import requests
from models import connect_db, db, User, Ingredient, Filt, Drink, Favorite
from forms import UserForm

from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone1"
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
    name = search["drinks"][0]
    return {"name": name}

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

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/search')
def search_name():
    return render_template('search_drink.html')

@app.route('/searched/name')
def searched_name():
    drink = request.args['name']
    drink_name = get_name(drink)
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
        new_user = User.register(username, password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect('/')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['user_id'] = user.id
            return redirect('/')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


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

    ###########################SEARCH BY FIRST LETTER##########################

# @app.route('/search/l/',methods = ['POST'])
# def searched_letter():
#     if request.method == 'POST':
#         letter = request.form['search-letter']
#         res = requests.get(f'{BASE_URL}?f={letter}')
#         val = res.json()
#         all_drinks = val["drinks"]
#         return render_template("cocktail_data.html",all_drinks=all_drinks,letter=letter)

# @app.route('/search/l/<l>',methods=['GET', 'POST'])
# def letter_list(l):
#     letter = l
#     res = requests.get(f'{BASE_URL}?f={letter}')
#     val = res.json()   
#     drinks = val["drinks"]
#     return render_template("list_drink.html", drinks=drinks,letter=letter)

###########################SEARCH BY INGREDIENT############################

# @app.route('/search/ingredient',methods = ['POST'])
# def searched_ingredient():
#     if request.method == 'POST':
#         ingredient = request.form['search-ingredient']
#         res = requests.get(f'{BASE_URL}?i={ingredient}')
#         val = res.json()
#         all_i = val["ingredients"]
#         return render_template("cocktail_data.html",all_i=all_i,ingredient=ingredient)

# @app.route('/search/ingredient/<type>',methods=['GET', 'POST'])
# def get_ingredient(type):
#     ingredient = type
#     res = requests.get(f'{BASE_URL}?f={ingredient}')
#     val = res.json()   
#     ingre_list = val["ingredients"]
#     return render_template("search_ingredient.html", ingre_list=ingre_list,type=type)