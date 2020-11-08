from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


artist_genres = db.Table('artist_genres', 
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
    db.Column('genres_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
  )

venue_genres = db.Table('venue_genres', 
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
    db.Column('genres_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
  )  


class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120),nullable = True)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable = False, default = True)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.relationship('Genre', secondary = venue_genres, backref = db.backref('venues', lazy = True)) 

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=True)
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre', secondary = artist_genres, backref = db.backref('artists', lazy = True)) 
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable = False, default = True)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime) 
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable = False)
    venues = db.relationship('Venue', backref = 'city', lazy = True)
    artists = db.relationship('Artist', backref = 'city', lazy = True)

class State(db.Model):
    __tablename__ = 'states'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)  
    cities = db.relationship('City', backref='state', lazy = True)
    


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
