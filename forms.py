from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, InputRequired, Optional
from wtforms.widgets import TextArea


class UserForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class DrinkForm(FlaskForm):
    
    name = StringField("Drink Name", validators=[InputRequired()])
    instructions = StringField("instructions:", validators=[Optional()],widget=TextArea())
    ingredient1 = StringField("ingredient1:", validators=[Optional()])
    ingredient2 = StringField("ingredient2:", validators=[Optional()])
    ingredient3 = StringField("ingredient3:", validators=[Optional()])
    ingredient4 = StringField("ingredient4:", validators=[Optional()])
    ingredient5 = StringField("ingredient5:", validators=[Optional()])
    ingredient6 = StringField("ingredient6:", validators=[Optional()])
    ingredient7 = StringField("ingredient7:", validators=[Optional()])
    ingredient8 = StringField("ingredient8:", validators=[Optional()])
    ingredient9 = StringField("ingredient9:", validators=[Optional()])
    ingredient10 = StringField("ingredient10:", validators=[Optional()])
