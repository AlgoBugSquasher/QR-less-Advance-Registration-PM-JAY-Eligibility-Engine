"""
User model and operations
Handles user data and authentication operations with SQLite storage.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models.database import get_db_connection


def _row_to_user(row):
    if not row:
        return None
    return {
        '_id': str(row['id']),
        'full_name': row['full_name'],
        'email': row['email'],
        'mobile_number': row['mobile_number'],
        'password_hash': row['password'],
        'created_at': datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
        'updated_at': datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
    }


class User:
    """User model for hospital token system"""
    
    @staticmethod
    def create_user(mobile_number, email, password, full_name):
        """
        Create a new user in SQLite storage.
        
        Args:
            mobile_number (str): User's mobile number
            email (str): User's email address
            password (str): User's password (will be hashed)
            full_name (str): User's full name
            
        Returns:
            dict: User data if successful, None if user already exists
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE mobile_number = ? OR email = ?",
            (mobile_number, email)
        )
        if cursor.fetchone():
            conn.close()
            return None

        now = datetime.now().isoformat()
        password_hash = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (full_name, email, mobile_number, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (full_name, email, mobile_number, password_hash, now, now)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        return User.get_user_by_id(user_id)
    
    @staticmethod
    def get_user_by_mobile(mobile_number):
        """
        Get user by mobile number from SQLite storage.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE mobile_number = ?",
            (mobile_number,)
        )
        row = cursor.fetchone()
        conn.close()
        return _row_to_user(row)
    
    @staticmethod
    def get_user_by_email(email):
        """
        Get user by email from SQLite storage.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        conn.close()
        return _row_to_user(row)
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID from SQLite storage.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE id = ?",
            (int(user_id),)
        )
        row = cursor.fetchone()
        conn.close()
        return _row_to_user(row)
    
    @staticmethod
    def verify_password(user, password):
        """
        Verify user's password
        """
        if not user:
            return False
        return check_password_hash(user.get('password_hash', ''), password)
    
    @staticmethod
    def update_user(user_id, update_data):
        """
        Update user information in SQLite storage.
        """
        if not update_data:
            return None

        update_data['updated_at'] = datetime.now().isoformat()
        fields = []
        values = []
        for key, value in update_data.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(int(user_id))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id = ?",
            tuple(values)
        )
        conn.commit()
        conn.close()
        return User.get_user_by_id(user_id)
