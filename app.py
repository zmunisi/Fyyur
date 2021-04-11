# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import dateutil.parser
import babel
import sys
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from forms import (
    VenueForm,
    ArtistForm,
    ShowForm
)
from flask_wtf.csrf import CSRFProtect
from models import db, Venue, Artist, Show

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    locals = []
    venues = Venue.query.all()

    places = Venue.query.distinct(Venue.city, Venue.state).all()

    for place in places:
        locals.append({
            'city': place.city,
            'state': place.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len([show for show in venue.shows if
                                          show.start_time > datetime.now()])
            } for venue in venues if
                venue.city == place.city and venue.state == place.state]
        })
    return render_template('pages/venues.html', areas=locals)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')

    venues = Venue.query.filter(
             Venue.name.like('%' + search_term + '%')).all()

    venue_data = []

    for venue in venues:
        venue_data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len([show for show in venue.shows if
                                       show.start_time > datetime.now()])
        })

    search = {
        "count": len(venues),
        "data": venue_data
    }
    return render_template('pages/search_venues.html', results=search,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue_data = []

    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    shows = db.session.query(Show, Artist, Venue).join(Artist).join(Venue). \
        filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id
    ). \
        all()

    past_shows = []
    upcoming_shows = []

    for show in shows:
        temp_show = {
            'artist_id': show.Artist.id,
            'artist_name': show.Artist.name,
            'artist_image_link': show.Artist.image_link,
            'start_time': show.Show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.Show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    # object class to dict
    data = vars(venue)

    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    venue_data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link
    }

    venue_data.update(data)
    return render_template('pages/show_venue.html',
                           venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form, meta={'csrf': True})
    if form.validate():
        try:
            venue = Venue()
            form.populate_obj(venue)

            db.session.add(venue)
            db.session.commit()

            flash('Venue ' + form.name.data + ' was successfully listed!')
        except venue:
            flash('An error occurred. Venue ' +
                  form.name.data + ' could not be listed.')
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + Venue.query.get(venue_id) +
              ' was successfully deleted.')
    except Venue:
        flash('An error occurred. Venue ' +
              Venue.query.get(venue_id) + ' could not be deleted.')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('venues'))

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

    return render_template('pages/artists.html',
                           artists=artists_data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form.get('search_term', '')

    artists = Artist.query.filter(
        Artist.name.like('%' + search_term + '%')).all()

    artist_data = []

    for artist in artists:
        artist_data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len([show for show in artist.shows if
                                       show.start_time > datetime.now()])
        })

    search = {
        "count": len(artists),
        "data": artist_data
    }

    return render_template('pages/search_artists.html',
                           results=search, search_term=request.form.get
                           ('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_data = []

    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    shows = db.session.query(Show, Venue).join(Venue). \
        filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id
    ). \
        all()

    past_shows = []
    upcoming_shows = []

    for show in shows:
        temp_show = {
            'venue_id': show.Venue.id,
            'venue_name': show.Venue.name,
            'venue_image_link': show.Venue.image_link,
            'start_time': show.Show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.Show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    # object class to dict
    data = vars(artist)

    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    artist_data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website_link': artist.website_link,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link
    }

    artist_data.update(data)
    return render_template('pages/show_artist.html',
                           artist=artist_data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first_or_404()

    form = ArtistForm(obj=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    form = ArtistForm(request.form, meta={'csrf': True})
    form.populate_obj(artist)
    if form.validate():
        try:
            db.session.commit()

            flash('Artist ' + form.name.data + ' was successfully updated!')
        except artist:
            flash('An error occurred. Artist ' +
                  form.name.data + ' could not be updated.')
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first_or_404()

    form = VenueForm(obj=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    form = VenueForm(request.form, meta={'csrf': True})
    form.populate_obj(venue)
    if form.validate():
        try:
            db.session.commit()

            flash('Venue ' + form.name.data + ' was successfully updated!')
        except venue:
            flash('An error occurred. Venue ' +
                  form.name.data + ' could not be ppdated.')
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form, meta={'csrf': True})
    if form.validate():
        try:
            artist = Artist()
            form.populate_obj(artist)

            db.session.add(artist)
            db.session.commit()

            flash('Artist ' + form.name.data + ' was successfully listed!')
        except artist:
            flash('An error occurred. Artist ' +
                  form.name.data + ' could not be listed.')
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

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
            "venue_name": Venue.query.filter_by
            (id=show.venue_id).first().name,
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by
            (id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by
            (id=show.artist_id).first().image_link,
            "start_time": str(show.start_time)
        })

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

        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)

        db.session.add(show)
        db.session.commit()

        flash('Show was successfully listed!')
    except show:
        db.session.rollback()
        print(sys.exc_info())
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
            + '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
