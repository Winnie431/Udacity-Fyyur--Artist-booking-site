#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from forms import *
from model  import *
from flask_migrate import Migrate
from datetime import date
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

csrf = CSRFProtect()

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
csrf.init_app(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
#see the model.py file


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  state_cities = Venue.query.with_entities(Venue.state,Venue.city,Venue.id).distinct()
  for state_city in state_cities:
    cityState = {
      "city":state_city.city,
      "state": state_city.state
    }

    venues=Venue.query.filter_by(state = state_city.state).filter_by(city = state_city.city).all()
    #formating each venue
    format_venues=[]
    for venue in venues:
      format_venues.append({ 
        'id': venue.id,
        'name':venue.name,
        'num_upcomming_shows':len(list(filter(lambda x: x.start_time > datetime.now(),venue.shows)))
        })
    cityState["venues"] = format_venues
    data.append(cityState)   
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  
  venues = Venue.query.with_entities(Venue.name,Venue.id, Venue.genres,Venue.address,Venue.city,Venue.state,Venue.phone,Venue.website_link,Venue.facebook_link,Venue.image_link,Venue.description,Venue.looking_talent).filter(Venue.id==venue_id).all()
  
  
  for venue in venues:
    venueById = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_talent,
    "seeking_description": venue.description,
    "image_link": venue.image_link
    }
  upcoming_shows = db.session.query(Show.start_time,Artist.name,Artist.image_link,Show.artist_id).join(Artist, Artist.id == Show.artist_id).filter(Show.start_time>datetime.now()).all()

  upcoming_shows_count=len(upcoming_shows)

  past_shows = db.session.query(Show.start_time,Artist.name,Artist.image_link,Show.artist_id).join(Artist, Artist.id == Show.artist_id).filter(Show.start_time<datetime.now()).all()

  past_shows_count=len(past_shows)

  upcomingShow = []
  pastShows = []

  for upcoming_show in upcoming_shows:
    upcomingShow.append({
      "artist_id": upcoming_show.artist_id,
      "artist_name": upcoming_show.name,
      "start_time": upcoming_show.start_time.strftime('%m/%d/%Y'),
      "artist_image_link": upcoming_show.image_link
      })
  for past_show in past_shows:
    pastShows.append({
      "artist_id": past_show.artist_id,
      "artist_name": past_show.name,
      "start_time": past_show.start_time.strftime('%m/%d/%Y'),
      "artist_image_link":past_show.image_link
      })
 
  venueById['upcoming_shows'] = upcomingShow
  venueById['upcoming_shows_count'] = upcoming_shows_count
  venueById['past_shows'] = pastShows
  venueById['past_shows_count'] = past_shows_count
  data.append(venueById)  

  data = list(filter(lambda d: d['id'] == venue_id,data))[0]
  #print(f"Hello, { venues}!")
  print(f"Hello, {  upcoming_shows}!")
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
 
  try:

        venue =Venue(name =form.name.data,
              city=form.city.data,
              state=form.state.data,
              address=form.address.data,
              phone=form.phone.data,
              image_link=form.image_link.data,
              genres=form.genres.data,
              facebook_link=form.facebook_link.data,
              website_link=form.website_link.data,
              looking_talent=form.seeking_talent.data,
              description=form.seeking_description.data                  
                  )
        db.session.add(venue)
        db.session.commit()     
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
        db.session.rollback()
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ )
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  finally: 
          db.session.close()
        
  return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for artist in artists:
    artistList = {
      "name":artist.name,
      "id": artist.id
    }

  data.append(artistList)   
  # print(f'hello',artistList)
  # print(f'hello',data)
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = []
  
  artists = Artist.query.with_entities(Artist.name,Artist.id, Artist.genres,Artist.city,Artist.state,Artist.phone,Artist.website_link,Artist.facebook_link,Artist.image_link,Artist.description,Artist.looking_venus).filter(Artist.id==artist_id).all()
   
  for artist in artists:
    artistById = {
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    'genres':artist.genres,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_venus,
    "seeking_description": artist.description,
    "image_link": artist.image_link
    }
  upcoming_shows = db.session.query(Show.start_time,Venue.name,Venue.image_link,Show.venue_id).join(Venue, Venue.id == Show.venue_id).filter(Show.start_time>datetime.now()).all()

  upcoming_shows_count=len(upcoming_shows)

  past_shows = db.session.query(Show.start_time,Venue.name,Venue.image_link,Show.venue_id).join(Venue, Venue.id == Show.venue_id).filter(Show.start_time<datetime.now()).all()

  past_shows_count=len(past_shows)

  upcomingShow = []
  pastShows = []

  for upcoming_show in upcoming_shows:
    upcomingShow.append({
      "venue_id": upcoming_show.venue_id,
      "venue_name": upcoming_show.name,
      "start_time": upcoming_show.start_time.strftime('%m/%d/%Y'),
      "venue_image_link": upcoming_show.image_link
      })
  for past_show in past_shows:
    pastShows.append({
      "venue_id": past_show.venue_id,
      "venue_name": past_show.name,
      "start_time": past_show.start_time.strftime('%m/%d/%Y'),
      "venue_image_link":past_show.image_link
      })
 
  artistById['upcoming_shows'] = upcomingShow
  artistById['upcoming_shows_count'] = upcoming_shows_count
  artistById['past_shows'] = pastShows
  artistById['past_shows_count'] = past_shows_count
  data.append(artistById)  

  data = list(filter(lambda d: d['id'] == artist_id,data))[0]
  
  print(f"Hello, {artistById}")
 
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
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

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
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
      artist =Artist(name =form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            looking_venus=form.seeking_venue.data,
            description=form.seeking_description.data                  
                )
      db.session.add(artist)
      db.session.commit()        
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
       db.session.rollback()
       print(sys.exc_info())
       # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ )
       flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  finally: 
        db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  #shows = Show.query.with_entities(Artist.name,Artist.id).distinct()
  shows = db.session.query(Show.start_time,Venue.name,Show.venue_id,Show.artist_id,Artist.name,Artist.image_link).join(Venue, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id).all()
  for show in shows:
    showList = {
    "venue_id": show.venue_id,
    "venue_name": show.name,
    "artist_id": show.artist_id,
    "artist_name": show.name,
    "artist_image_link": show.image_link,
    "start_time": show.start_time.strftime('%m/%d/%Y')
    }
  data.append(showList) 
  #print(f"hello",showList)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try:
      show =Show(
              artist_id=form.artist_id.data,
              venue_id=form.venue_id.data,
              start_time=form.start_time.data                           
                )
      db.session.add(show)
      db.session.commit()        
      flash('Show was successfully listed!')
  except:
       db.session.rollback()
       print(sys.exc_info())
       # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ )
       flash('Show was not successfully listed!')

  finally: 
        db.session.close()
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
