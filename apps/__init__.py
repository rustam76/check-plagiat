# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flaskext.mysql import MySQL
from importlib import import_module



mysql = MySQL()
# login_manager = LoginManager()

def register_extensions(app):
    mysql.init_app(app)
    # login_manager.init_app(app)
   

def register_blueprints(app):
    for module_name in ('home', 'controller'):
        module = import_module('apps.{}.home'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')  # Example query to test connection
            print('> Connection to MySQL DBMS established successfully' + str(cursor.fetchone()))
        except Exception as e:
            print('> Error: DBMS Exception: ' + str(e))
            # Handle MySQL connection failure
            print('> Failed to connect to MySQL')

    @app.teardown_request
    def shutdown_session(exception=None):
        conn = mysql.connect()
        conn.close()



def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
