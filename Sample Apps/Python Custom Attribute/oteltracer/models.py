"""
Data models for the application
"""
import psycopg2
from psycopg2 import IntegrityError
from datetime import datetime
from database import get_db_connection, close_db_connection

class User:
    """User model for database operations"""

    def __init__(self, username=None, email=None, first_name=None,
                 last_name=None, age=None, phone=None, address=None,
                 created_at=None, updated_at=None):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.phone = phone
        self.address = address
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def get_all():
        """
        Get all users from database

        Returns:
            list: List of user dictionaries
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY username')
        users = cursor.fetchall()
        cursor.close()
        close_db_connection(conn)
        return users
    
    @staticmethod
    def get_by_username(username):
        """
        Get user by username

        Args:
            username (str): Username (primary key)

        Returns:
            dict: User dictionary or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        close_db_connection(conn)
        return user
    
    @staticmethod
    def create(data):
        """
        Create a new user

        Args:
            data (dict): User data

        Returns:
            tuple: (username, error_message)
        """
        required_fields = ['username', 'email', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data:
                return None, f"Missing required field: {field}"

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO users (username, email, first_name, last_name, age, phone, address)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING username''',
                (data['username'], data['email'], data['first_name'], data['last_name'],
                 data.get('age'), data.get('phone'), data.get('address'))
            )
            username = cursor.fetchone()['username']
            conn.commit()
            cursor.close()
            close_db_connection(conn)
            return username, None
        except IntegrityError as e:
            return None, f"Database error: {str(e)}"
    
    @staticmethod
    def update(username, data):
        """
        Update an existing user

        Args:
            username (str): Username (primary key)
            data (dict): Fields to update

        Returns:
            tuple: (success, error_message)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            close_db_connection(conn)
            return False, "User not found"

        # Build update query dynamically
        update_fields = []
        values = []

        # Note: username cannot be updated as it's the primary key
        allowed_fields = ['email', 'first_name', 'last_name', 'age', 'phone', 'address']
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])

        if not update_fields:
            cursor.close()
            close_db_connection(conn)
            return False, "No fields to update"

        # Add updated_at timestamp
        update_fields.append("updated_at = %s")
        values.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        values.append(username)

        try:
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE username = %s"
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            close_db_connection(conn)
            return True, None
        except IntegrityError as e:
            cursor.close()
            close_db_connection(conn)
            return False, f"Database error: {str(e)}"
    
    @staticmethod
    def delete(username):
        """
        Delete a user

        Args:
            username (str): Username (primary key)

        Returns:
            tuple: (success, error_message)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            close_db_connection(conn)
            return False, "User not found"

        cursor.execute('DELETE FROM users WHERE username = %s', (username,))
        conn.commit()
        cursor.close()
        close_db_connection(conn)
        return True, None

