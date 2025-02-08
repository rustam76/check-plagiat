from apps.model.auth_model import AuthModel

# from flask import render_template, request, redirect, url_for, flash

class AuthController:

    def login(self, username, password):
        if not username or not password:
            return False
        
        auth = AuthModel()
        return auth.login(username, password)
        
       
