from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class Favoritelist(db.Model):
    __tablename__ = "favlists"
# playlist
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Favorite name={self.name} description={self.description}>"

class Drink(db.Model):
    __tablename__ = "drinks"
    # song
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=True)
    # fav_id = db.Column(db.Integer, db.ForeignKey("favorites.id"))
    favlist = db.relationship("Favorite",  backref='drinks')

    # user_id = db.Column( db.Integer, db.ForeignKey('users.id',ondelete='CASCADE'), nullable=False,)
    def __repr__(self):
        return f"<Song name={self.name} category={self.category} >"

class Favorite(db.Model):
    __tablename__ = "favorites"
# playlistsong
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    favlist_id = db.Column(db.Integer, db.ForeignKey("favlists.id") )
    drink_id = db.Column(db.Integer, db.ForeignKey("drinks.id") )

    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # user = db.relationship('User', backref="favorites")

class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    alcoholic = db.Column(db.Boolean)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False,  unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    # favorites = db.relationship('favorite')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def register(cls, username, pwd, email):
        """Register user w/hashed password & return user."""

        hashed_pwd = bcrypt.generate_password_hash(pwd).decode('UTF-8')

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_pwd, email=email)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False