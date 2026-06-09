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
    Portal selection page
    Shows User Portal and Admin Portal options
    """
    user_info = get_current_user_info()
    
    # If user is already logged in, redirect to dashboard
    if user_info:
        return redirect(url_for('main.home_dashboard'))
    
    return render_template('portal_selection.html')


@main_bp.route('/home-dashboard')
@login_required
def home_dashboard():
    """
    Home dashboard after login
    Shows Voice Assistant and Manual Selection options
    """
    user_info = get_current_user_info()
    
    return render_template(
        'home_dashboard.html',
        user=user_info,
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


@main_bp.route('/my-tokens')
@login_required
def my_tokens():
    """
    My Tokens page
    Shows user's current and past tokens
    """
    user_info = get_current_user_info()
    tokens = Token.get_user_tokens(user_info['user_id'])

    formatted_tokens = []
    for token in tokens:
        arrival_info = None
        try:
            from app.utils.token_generator import calculate_estimated_arrival_time
            arrival_info = calculate_estimated_arrival_time(token.get('queue_position', 1))
        except Exception:
            arrival_info = {'arrival_time': 'N/A'}

        formatted_tokens.append({
            'token_id': token.get('_id'),
            'token_number': token.get('token_number'),
            'department': token.get('dept_name'),
            'queue_position': token.get('queue_position'),
            'estimated_wait_time': token.get('estimated_wait_time', 0),
            'estimated_arrival_time': arrival_info.get('arrival_time'),
            'status': token.get('status'),
            'created_at': token.get('created_at').strftime('%d %b %Y %H:%M') if token.get('created_at') else None
        })

    return render_template(
        'my_tokens.html',
        user=user_info,
        tokens=formatted_tokens
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
        'voice_assistant_redesigned.html',
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
