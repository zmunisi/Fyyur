import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Disable csrf protection
# WTF_CSRF_ENABLED = False

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgresql://zmunisi:@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
