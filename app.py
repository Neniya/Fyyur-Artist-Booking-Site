#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show, City, State, Genre
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues') 
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.


    list_of_cities = db.session.query(
      City, 
      State
        ).filter(
          Venue.city_id == City.id).filter(
          City.state_id == State.id
          ).distinct(
            City.name, 
            State.name
            ).all()

    data = []        
    for city in list_of_cities:
      list_of_venues = db.session.query(Venue.city_id, Venue.name, Venue.id).filter_by(city_id = city.City.id).all()

      venues = []
      for venue in list_of_venues:
        venues.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows":  len(Show.query.filter_by(venue_id = venue.id).filter(Show.start_time > datetime.now()).all())
          })

      item = {
        "city": city.City.name,
        "state": city.State.name,
        "venues": venues 
        }
      data.append(item)  

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # V TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term=request.form.get('search_term', '')
  list_of_venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  data = []
  count = 0
  for venue in list_of_venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(Show.query.filter_by(venue_id = venue.id).filter(Show.start_time > datetime.now()).all())
    })
    count += 1

  response={
    "count": count,
    "data": data
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # V TODO: replace with real venue data from the venues table, using venue_id
  
  #genres
  venue_genres = []
  list_of_genres = Genre.query.filter(Genre.venues.any(id=1)).all()
  for genre in list_of_genres:
    venue_genres.append(genre.name) 
  
  # past and upcomming shows:
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
    all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()  
 


  #data
  finding_venue = Venue.query.get(venue_id)
  
  data = {
    "id": venue_id,
    "name": finding_venue.name,
    "genres": venue_genres,
    "address": finding_venue.address,
    "city": finding_venue.city.name,
    "state": finding_venue.city.state.name,
    "phone": finding_venue.phone,
    "website": finding_venue.website,
    "facebook_link": finding_venue.facebook_link,
    "seeking_talent": True,
    "seeking_description": finding_venue.seeking_description,
    "image_link": finding_venue.image_link,
    "past_shows":[{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
    "upcoming_shows":[{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission(): #
  # V TODO: insert form data as a new Venue record in the db, instead
  # V TODO: modify data to be the data object returned from db insertion
 
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      form_venue= request.form

      #city
      city_name = form_venue['city']
      state_name = form_venue['state']
      city_from_db = City.query.join(State).filter(City.name == city_name, State.name == state_name).all()
      if len(city_from_db) > 0:
        city_id = city_from_db[0].id
      else:
        state = State.query.filter_by(name = state_name).all()[0]
        new_city = City(name = city_name, state = state) 
        db.session.add(new_city)
        db.session.commit()
        city_id = new_city.id
    
      #data
      new_venue = Venue(
        name = form_venue['name'],
        address = form_venue['address'],
        phone = form_venue['phone'],
        website =  form_venue['website'],
        facebook_link = form_venue['facebook_link'],
        seeking_description =  form_venue['seeking_description'],
        image_link = form_venue['image_link']
      )

      if 'seeking_talent' not in form_venue:
        new_venue.seeking_talent = False
      else:
        new_venue.seeking_talent = True

      new_venue.city_id = city_id

      genres =Genre.query.filter(Genre.name.in_(form_venue.getlist('genres'))).all()
      for genre in genres:
        new_venue.genres.append(genre)

      #create
      db.session.add(new_venue)
      db.session.commit()
      #on successful db insert, flash success
      flash('Venue ' + form_venue['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + form_venue['name'] + ' could not be listed.')
    finally:
      db.session.close()     
  else:
    message = []

    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('The Venue data is not valid. Please try again! Errors: ' + str(message))


 
  
  # V TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue = Venue.query.get(venue_id)
      venue.query.filter_by(id = venue_id).delete()
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')#
def artists():
  # V TODO: replace with real data returned from querying the database
  list_of_artists = Artist.query.all()
  data = []
  for artist in list_of_artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])#
def search_artists():
  # V TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  list_of_artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  data = []
  count = 0
  for artist in list_of_artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(Show.query.filter_by(artist_id = artist.id).filter(Show.start_time > datetime.now()).all())
    })
    count += 1

  response={
    "count": count,
    "data": data
  }
 
  return render_template('pages/search_artists.html', results=response, search_term = search_term)

@app.route('/artists/<int:artist_id>')#
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # V TODO: replace with real venue data from the venues table, using venue_id
  
  #genres
  artist_genres = []
  list_of_genres = Genre.query.filter(Genre.artists.any(id=1)).all()
  for genre in list_of_genres:
    artist_genres.append(genre.name) 
  
  # past and upcomming shows:
  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id,
        Show.start_time < datetime.now()
    ).\
    all()

  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id,
        Show.start_time > datetime.now()
    ).\
    all()  

  #data
  finding_artist = Artist.query.get(artist_id)

  data={
    "id": finding_artist.id,
    "name": finding_artist.name,
    "genres": artist_genres,
    "city": finding_artist.city.name,
    "state": finding_artist.city.state.name,
    "phone": finding_artist.phone,
    "website": finding_artist.website,
    "facebook_link": finding_artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": finding_artist.seeking_description,
    "image_link": finding_artist.image_link,
     "past_shows":[{
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in past_shows],
    "upcoming_shows":[{
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  #*** how I have understood edit and the update are not required for this project.
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  #*** how I have understood edit and the update are not required for this project.
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  #*** how I have understood edit and the update are not required for this project.
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  #*** how I have understood edit and the update are not required for this project.
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # V TODO: insert form data as a new Venue record in the db, instead
  # V TODO: modify data to be the data object returned from db insertion
 
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():

    try:
      form_artist= request.form

      #city
      city_name = form_artist['city']
      state_name = form_artist['state']
      city_from_db = City.query.join(State).filter(City.name == city_name, State.name == state_name).all()
      if len(city_from_db) > 0:
        city_id = city_from_db[0].id
      else:
        state = State.query.filter_by(name = state_name).all()[0]
        new_city = City(name = city_name, state = state) 
        db.session.add(new_city)
        db.session.commit()
        city_id = new_city.id
      
      #data
      new_artist = Artist(
        name = form_artist['name'],
        phone =  form_artist['phone'],
        website = form_artist['website'],
        facebook_link = form_artist['facebook_link'],
        seeking_description = form_artist['seeking_description'],
        image_link = form_artist['image_link']
      )

      if 'seeking_venue' not in form_artist:
        new_artist.seeking_venue = False
      else:
        new_artist.seeking_venue = True

      new_artist.city_id = city_id

      genres =Genre.query.filter(Genre.name.in_(form_artist.getlist('genres'))).all()
      for genre in genres:
        new_artist.genres.append(genre)

      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + form_artist['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + form_artist['name'] + ' could not be listed.')
    finally:
      db.session.close()   
  else:
    message = []

    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('The Artist data is not valid. Please try again! Errors: ' + str(message))


  #V TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')#
def shows():
  # displays list of shows at /shows
  # V TODO: replace with real venues data.
  #  ?     num_shows should be aggregated based on number of upcoming shows per venue.

  list_of_shows = Show.query.join(Venue, Artist).order_by(Show.start_time.desc()).all()

  data = []
  for show in list_of_shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time) 
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # V TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    try: 
      form_show= request.form
      new_show = Show(
          venue_id = form_show['venue_id'],
          artist_id = form_show['artist_id'],
          start_time = str(form_show['start_time']) 
        )

      db.session.add(new_show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()  
  else:
    message = []

    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('The Show data is not valid. Please try again! Errors: ' + str(message))

    
 
  
  # V TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
