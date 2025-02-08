from apps.config import get_db_connection
from apps.model.users import User
import hashlib
from flask import flash

class AuthModel:
    def login(self, username, password):
        connection = get_db_connection()
        cursor = connection.cursor()

        # Hash the password with MD5
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # Use parameterized query to prevent SQL injection
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed_password))

        user = cursor.fetchone()
        connection.close()
        
        if user:
            return User(id=user[0], username=user[1])
        return None

    def update_user(self, username, new_username=None, new_password=None):
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Retrieve current user data to check if the username exists
            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()

            if user_data:
                user_id = user_data[0]
                current_password = user_data[1]

                # If a new password is provided, hash and update it
                if new_password:
                    hashed_password = hashlib.md5(new_password.encode()).hexdigest()
                    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))

                # If a new username is provided, update it
                if new_username and new_username != username:  
                    cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, user_id))

                # Commit changes to the database
                connection.commit()
                return True  # Indicate success
            else:
                # User not found
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False  # Indicate failure
        finally:
            cursor.close()
            connection.close()