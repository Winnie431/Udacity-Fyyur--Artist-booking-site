from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
db = SQLAlchemy(app)

class Show(db.Model):
        __tablename__='show'
        id = db.Column(db.Integer, primary_key=True)
        venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable = False)
        artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable = False)
        start_time = db.Column(db.DateTime, nullable= False)
  
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable = False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120),nullable=False)
    website_link = db.Column(db.String(120),nullable = True)
    looking_talent = db.Column(db.Boolean, default = False, nullable=False)
    description = db.Column(db.String(1000),nullable = True)
    shows= db.relationship('Show',backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120),nullable = True)
    looking_venus = db.Column(db.Boolean, default = False, nullable=False)
    description = db.Column(db.String(1000),nullable = True)
    shows= db.relationship('Show',backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate