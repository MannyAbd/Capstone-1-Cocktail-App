
from unicodedata import category
from flask_wtf import FlaskForm
from models import Favorite
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, InputRequired, Optional


class UserForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class FavlistForm(FlaskForm):

    name = StringField("favlist Name", validators=[InputRequired()])
    description = StringField("Describe favlist", validators=[Optional()])

class DrinkForm(FlaskForm):
    
    name = StringField("Drink Name", validators=[InputRequired()])
    category = StringField("category:", validators=[Optional()])

class AddToFavorites(FlaskForm):
    favorite = SelectField('Add to Favorite', coerce=int)