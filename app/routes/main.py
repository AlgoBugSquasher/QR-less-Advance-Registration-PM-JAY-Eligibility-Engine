"""
Main routes blueprint
Handles home page and general application routes
"""

from flask import Blueprint, render_template, session, redirect, url_for
from app.models.department import Department
from app.models.token import Token
from app.utils.auth import login_required, get_current_user_info
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """
    Home page route
    Shows hospital welcome page with department overview
    """
    user_info = get_current_user_info()
    departments = Department.get_all_departments()
    
    return render_template(
        'home.html',
        user=user_info,
        departments=departments,
        hospital_name=os.getenv('HOSPITAL_NAME', 'City Hospital & Diagnostic Center')
    )


@main_bp.route('/dashboard')
def dashboard():
    """
    User dashboard
    Shows user's tokens and history
    """
    user_info = get_current_user_info()
    
    if not user_info:
        return redirect(url_for('auth.login'))
    
    from app.models.token import Token
    user_tokens = Token.get_user_tokens(user_info['user_id'])
    
    return render_template(
        'dashboard.html',
        user=user_info,
        tokens=user_tokens
    )


@main_bp.route('/about')
def about():
    """About page"""
    user_info = get_current_user_info()
    return render_template(
        'about.html',
        user=user_info,
        hospital_name=os.getenv('HOSPITAL_NAME', 'City Hospital & Diagnostic Center')
    )


@main_bp.route('/voice-assistant')
@login_required
def voice_assistant():
    """Hindi Voice Assistant page"""
    user_info = get_current_user_info()
    return render_template(
        'voice_assistant.html',
        user=user_info
    )


@main_bp.route('/display')
def display():
    """Live queue display screen"""
    departments = Department.get_all_departments()
    has_active_queue = False

    for dept in departments:
        dept['current_token'] = Token.get_current_serving_token(dept['dept_code'])
        waiting_tokens = Token.get_waiting_tokens(dept['dept_code'])
        dept['next_tokens'] = waiting_tokens[:3]
        if dept['current_token'] or dept['next_tokens']:
            has_active_queue = True

    return render_template(
        'display.html',
        departments=departments,
        has_active_queue=has_active_queue
    )
