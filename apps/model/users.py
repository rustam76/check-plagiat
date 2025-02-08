from flask import Flask
from apps.config import get_db_connection
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from apps import app




# Konfigurasi Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        connection = get_db_connection()
        cur= connection.cursor()
        cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        
        if user:
            return User(id=user[0], username=user[1])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
