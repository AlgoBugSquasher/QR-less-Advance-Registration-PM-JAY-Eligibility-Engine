"""
Authentication routes blueprint
Handles user registration, login, and logout
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.models.user import User
from app.utils.auth import (
    login_required, set_user_session, clear_user_session,
    set_admin_session, clear_admin_session,
    is_valid_mobile_number, is_valid_email, is_valid_password,
    get_current_user_info, is_admin_logged_in
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route
    Handles GET (show form) and POST (process registration)
    """
    # Redirect if already logged in
    if get_current_user_info():
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Get form data
        mobile_number = request.form.get('mobile_number', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not mobile_number:
            errors.append('Mobile number is required')
        elif not is_valid_mobile_number(mobile_number):
            errors.append('Invalid mobile number format')
        
        if not email:
            errors.append('Email is required')
        elif not is_valid_email(email):
            errors.append('Invalid email format')
        
        if not full_name or len(full_name) < 2:
            errors.append('Full name is required')
        
        if not password:
            errors.append('Password is required')
        elif not is_valid_password(password):
            errors.append('Password must be at least 6 characters')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # If validation failed, show errors
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')
        
        # Try to create user
        user = User.create_user(mobile_number, email, password, full_name)
        
        if not user:
            flash('Mobile number or email already registered', 'danger')
            return render_template('register.html')
        
        # Successful registration
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route
    Handles GET (show form) and POST (process login)
    """
    # Redirect if already logged in
    if get_current_user_info():
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Get form data
        login_input = request.form.get('login_input', '').strip()  # Can be mobile or email
        password = request.form.get('password', '')
        
        # Validation
        if not login_input:
            flash('Mobile number or email is required', 'danger')
            return render_template('login.html')
        
        if not password:
            flash('Password is required', 'danger')
            return render_template('login.html')
        
        # Find user by mobile number or email
        user = None
        if is_valid_mobile_number(login_input):
            user = User.get_user_by_mobile(login_input)
        elif is_valid_email(login_input):
            user = User.get_user_by_email(login_input)
        
        # Verify user and password
        if not user or not User.verify_password(user, password):
            flash('Invalid mobile/email or password', 'danger')
            return render_template('login.html')
        
        # Set session and redirect
        set_user_session(user)
        flash(f'Welcome back, {user.get("full_name", "User")}!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('login.html')


@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """
    Admin login route
    Hardcoded local credentials are used for demo admin access.
    """
    if is_admin_logged_in():
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin_username = 'admin'
        admin_password = 'admin123'

        if username == admin_username and password == admin_password:
            set_admin_session(username)
            flash('Admin login successful', 'success')
            return redirect(url_for('admin.dashboard'))

        flash('Invalid admin username or password', 'danger')

    return render_template('admin_login.html')


@auth_bp.route('/admin-logout')
def admin_logout():
    """
    Admin logout route
    """
    clear_admin_session()
    flash('Admin logged out successfully', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route
    Clears session and redirects to home
    """
    user_name = get_current_user_info().get('full_name', 'User')
    clear_user_session()
    flash(f'Goodbye, {user_name}! You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/check-mobile', methods=['POST'])
def check_mobile():
    """
    AJAX route to check if mobile number is already registered
    Returns JSON response
    """
    mobile_number = request.form.get('mobile_number', '').strip()
    
    if not mobile_number:
        return jsonify({'exists': False})
    
    user = User.get_user_by_mobile(mobile_number)
    return jsonify({'exists': user is not None})


@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    AJAX route to check if email is already registered
    Returns JSON response
    """
    email = request.form.get('email', '').strip()
    
    if not email:
        return jsonify({'exists': False})
    
    user = User.get_user_by_email(email)
    return jsonify({'exists': user is not None})
