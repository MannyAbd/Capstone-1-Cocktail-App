from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Drink(db.Model):
    __tablename__ = "drinks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    alcoholic = db.Column(db.Boolean)
    instructions= db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.Image)
    glass_type = db.Column(db.Text)
    ingredients_list = db.Column(db.Text, nullable=False)
    measurements_list = db.Column(db.Text, nullable=False)

class Filter(db.Model):
    __tablename__ = "filters"

    category = db.Column(db.Text, nullable=False)
    glass_type = db.Column(db.Text)
    ingredients_list = db.Column(db.Text, nullable=False)
    alcohol = db.Column(db.Text)

class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    alcoholic = db.Column(db.Boolean)


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)