# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from dotenv import load_dotenv

import os
import random
import string
import mysql.connector
from flaskext.mysql import MySQL


    # MySQL Configuration
DB_ENGINE   = os.getenv('DB_ENGINE')
DB_USERNAME = os.getenv('DB_USERNAME', 'root')
DB_PASS     = os.getenv('DB_PASS')
DB_HOST     = os.getenv('DB_HOST')
DB_PORT     = int(os.getenv('DB_PORT', 3306))
DB_NAME     = os.getenv('DB_NAME', 'db_plagiat')


def create_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USERNAME,
            password=DB_PASS,
            database=DB_NAME,
            port=DB_PORT
        )
        return conn
    except mysql.connector.Error as err:
        print("Error: {}".format(err))


def get_db_connection():
    conn = create_db_connection()
    return conn
