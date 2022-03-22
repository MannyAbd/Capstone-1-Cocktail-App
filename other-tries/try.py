from flask import Flask, request, redirect, render_template, flash, session, g
import requests
from models import connect_db, db, User, Ingredient, Filt, Drink, Favorite
from forms import UserForm, LoginForm

from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone1"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = 'hi'

connect_db(app)
CURR_USER_KEY = "curr_user"
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

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/register', methods=["GET", "POST"])
def signup():

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()
        except IntegrityError as e:
            flash('Username taken.  Please pick another', 'danger')
            return render_template('register.html', form=form)
        do_login(user)
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect("/")
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        if user:
            do_login(user)
            flash(f"Welcome Back, {user.username}!", "primary")
            return redirect("/")

        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have successfully logged out.", 'success')
    return redirect("/")

##############################loggedIn Route###############################

@app.route('/favorites')
def show_favorites():
    if not g.user:
        flash("Please login first!", "danger")
        return redirect('/login')
    
    return render_template("favorites.html")