"""
Authentication utilities
Session and token management helpers
"""

from flask import session
from functools import wraps
from flask import redirect, url_for, flash
import os


def login_required(f):
    """
    Decorator to require user login
    Redirects to login page if user is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Get currently logged-in user ID from session
    
    Returns:
        str: User ID if logged in, None otherwise
    """
    return session.get('user_id')


def get_current_user_info():
    """
    Get currently logged-in user information from session
    
    Returns:
        dict: User info if logged in, None otherwise
    """
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    return {
        'user_id': user_id,
        'mobile_number': session.get('mobile_number'),
        'email': session.get('email'),
        'full_name': session.get('full_name')
    }


def set_user_session(user):
    """
    Set user information in session after successful login
    
    Args:
        user (dict): User document from database
    """
    session['user_id'] = str(user['_id'])
    session['mobile_number'] = user.get('mobile_number')
    session['email'] = user.get('email')
    session['full_name'] = user.get('full_name')
    session.permanent = True


def clear_user_session():
    """
    Clear user session on logout
    """
    session.pop('user_id', None)
    session.pop('mobile_number', None)
    session.pop('email', None)
    session.pop('full_name', None)


def set_admin_session(admin_name):
    """
    Set admin information in session after successful login
    """
    session['admin'] = True
    session['admin_name'] = admin_name
    session.permanent = True


def clear_admin_session():
    """
    Clear admin session on logout
    """
    session.pop('admin', None)
    session.pop('admin_name', None)


def is_admin_logged_in():
    """
    Check whether an admin is currently logged in.
    """
    return session.get('admin', False) is True


def get_current_admin_info():
    """
    Get currently logged-in admin information from session.
    """
    if not is_admin_logged_in():
        return None
    return {
        'admin_name': session.get('admin_name')
    }


def admin_login_required(f):
    """
    Decorator to require admin login
    Redirects to admin login page if admin is not authenticated
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            flash('Please log in as admin first', 'warning')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def is_valid_mobile_number(mobile_number):
    """
    Validate mobile number format
    
    Args:
        mobile_number (str): Mobile number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove common separators
    cleaned = mobile_number.replace('-', '').replace(' ', '').replace('+', '')
    
    # Check if it's 10 digits (Indian phone numbers)
    if len(cleaned) == 10 and cleaned.isdigit():
        return True
    
    # Check if it's 12 digits with country code (91 for India)
    if cleaned.startswith('91') and len(cleaned) == 12 and cleaned.isdigit():
        return True
    
    return False


def is_valid_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_password(password):
    """
    Validate password strength
    Minimum 6 characters
    
    Args:
        password (str): Password to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return len(password) >= 6
