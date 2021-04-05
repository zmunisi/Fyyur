#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
from flask_migrate import Migrate
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'

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
  venues = Venue.query.all()
  cities = Venue.query.distinct(Venue.city).all()
  venues_data = []

  for city in cities:
    venues_in_city = []
    for venue in venues:
      if(venue.city == city.city):
        shows = Show.query.filter_by(venue_id=venue.id).all()
        venues_in_city.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': upcomingShowsVenue(shows)
          })
    venues_data.append({
      'city': city.city,
      'state': city.state,
      'venues': venues_in_city
    })

  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/venues.html', areas=venues_data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')

  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  shows = Show.query.filter_by(venue_id=venue_id).all()
  
  venue_data = []

  for venue in venues:
    venue_data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(upcomingShowsVenue(shows))
    })

  response = {
    "count": len(venues),
    "data": venue_data
  }



  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue_data = []

  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()

  venue_data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'image_link': venue.image_link,
    'past_shows': pastShowsVenue(shows),
    'upcoming_shows': upcomingShowsVenue(shows),
    'past_shows_count': len(pastShowsVenue(shows)),
    'upcoming_shows_count': len(upcomingShowsVenue(shows))
  }

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = VenueForm()

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website_link']
    image_link = request.form['image_link']

    seeking_talent = request.form.get('seeking_talent')

    if seeking_talent == 'y':
      seeking_talent = True
    else:
      seeking_talent = False
    seeking_description = request.form['seeking_description']

    venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link,
      website=website,
      image_link=image_link,
      seeking_talent=seeking_talent,
      seeking_description=seeking_description)

    db.session.add(venue)
    db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)

    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + Venue.query.get(venue_id) + ' was successfully deleted.')
  except:
    flash('An error occurred. Venue ' + Venue.query.get(venue_id) + ' could not be deleted.')
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('venues'))
# TODO: Complete this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
# clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists_data = []

  artists = Artist.query.all()

  for artist in artists:
    artists_data.append({
      "id": artist.id,
      "name": artist.name
    })
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=artists_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  artist_data = []

  for artist in artists:
    shows = Show.query.filter_by(artist_id=artist.id).all()
    artist_data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(upcomingShowsArtist(shows))
    })

  response = {
    "count": len(artists),
    "data": artist_data
  }
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_data = []

  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()

  artist_data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': pastShowsArtist(shows),
    'past_shows_count': len(pastShowsArtist(shows)),
    'upcoming_shows': upcomingShowsArtist(shows),
    'upcoming_shows_count': len(upcomingShowsArtist(shows))
  }

  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.filter_by(id=artist_id).first()

  artist_data={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    form = ArtistForm()

    artist_data = Artist.query.filter_by(id=artist_id).first()

    artist_data.name = request.form['name']
    artist_data.city = request.form['city']
    artist_data.state = request.form['state']
    artist_data.phone = request.form['phone']
    artist_data.genres = request.form.getlist('genres')
    artist_data.facebook_link = request.form['facebook_link']
    artist_data.website = request.form['website_link']
    artist_data.image_link = request.form['image_link']
    seeking_venue = request.form.get('seeking_venue')

    if seeking_venue == 'y':
      artist_data.seeking_venue = True
    else:
      artist_data.seeking_venue = False

    artist_data.seeking_description = request.form['seeking_description']

    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()


  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()

  venue_data = {
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    form = VenueForm()

    venue_data = Venue.query.filter_by(id=venue_id).first()

    venue_data.name = request.form['name']
    venue_data.city = request.form['city']
    venue_data.state = request.form['state']
    venue_data.address = request.form['address']
    venue_data.phone = request.form['phone']
    venue_data.genres = request.form.getlist('genres')
    venue_data.facebook_link = request.form['facebook_link']
    venue_data.website = request.form['website_link']
    venue_data.image_link = request.form['image_link']
    seeking_talent = request.form['seeking_talent']
    
    if seeking_talent == 'y':
      venue_data.seeking_talent = True
    else:
      venue_data.seeking_talent = True

    venue_data.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

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
  try:
    form = VenueForm()
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website_link']
    image_link = request.form['image_link']
    seeking_venue = request.form.get('seeking_venue')

    if seeking_venue == 'y':
      seeking_venue = True
    else:
      seeking_venue = False

    seeking_description = request.form['seeking_description']

    artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link,
      website=website,
      image_link=image_link,
      seeking_venue=seeking_venue,
      seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows_data = []
  shows = Show.query.all()

  for show in shows:
    shows_data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
      "start_time": str(show.start_time)
    })
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    db.session.add(show)
    db.session.commit()

    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # TODO: on unsuccessful db insert, flash an error instead.
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
# Shows Functions.
#----------------------------------------------------------------------------#

def pastShowsVenue(shows):
  past_shows = []
  for show in shows:
    if show.start_time <= datetime.now():
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": str(show.start_time)
      })
  return past_shows

def pastShowsArtist(shows):
  past_shows = []
  for show in shows:
    if show.start_time <= datetime.now():
      past_shows.append({
        'venue_id' : show.venue_id,
        'venue_name' : Venue.query.filter_by(id=show.venue_id).first().name,
        'venue_image_link': Venue.query.filter_by(id=show.venue_id).first().image_link,
        'start_time': str(show.start_time)
      })
  return past_shows

def upcomingShowsVenue(shows):
  upcoming_shows = []
  for show in shows:
    if show.start_time > datetime.now():
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": str(show.start_time)
      })
  return upcoming_shows

def upcomingShowsArtist(shows):
  upcoming_shows = []
  for show in shows:
    if show.start_time > datetime.now():
      upcoming_shows.append({
        'venue_id' : show.venue_id,
        'venue_name' : Venue.query.filter_by(id=show.venue_id).first().name,
        'venue_image_link': Venue.query.filter_by(id=show.venue_id).first().image_link,
        'start_time': str(show.start_time)
      })
  return upcoming_shows

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
