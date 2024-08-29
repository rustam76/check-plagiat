# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import random
import string
from flaskext.mysql import MySQL

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    # Set up the App SECRET_KEY
    SECRET_KEY  = os.getenv('SECRET_KEY', None)
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))

    # MySQL Configuration
    DB_ENGINE   = os.getenv('DB_ENGINE')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASS     = os.getenv('DB_PASS')
    DB_HOST     = os.getenv('DB_HOST')
    DB_PORT     = int(os.getenv('DB_PORT', 3306))
    DB_NAME     = os.getenv('DB_NAME')

    # Configure MySQL
    MYSQL_DATABASE_USER = DB_USERNAME
    MYSQL_DATABASE_PASSWORD = DB_PASS
    MYSQL_DATABASE_DB = DB_NAME
    MYSQL_DATABASE_HOST = DB_HOST
    MYSQL_DATABASE_PORT = DB_PORT


    MYSQL_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        DB_ENGINE,
        DB_USERNAME,
        DB_PASS,
        DB_HOST,
        DB_PORT,
        DB_NAME
    )

    # Ensure all necessary environment variables are set
    if not DB_USERNAME or not DB_PASS or not DB_NAME:
        raise Exception("Database configuration is incomplete. Please set DB_USERNAME, DB_PASS, and DB_NAME.")

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
