"""
Admin routes blueprint
Handles admin queue management and token control
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from app.models.department import Department
from app.models.token import Token
from app.utils.auth import admin_login_required, get_current_admin_info

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@admin_login_required
def index():
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    departments = Department.get_all_departments()
    for dept in departments:
        # Fetch current queue statistics and tokens
        dept['stats'] = Token.get_queue_stats(dept['dept_code'])
        dept['current_token'] = Token.get_current_serving_token(dept['dept_code'])
        dept['waiting_tokens'] = Token.get_waiting_tokens(dept['dept_code'])

        # Auto-serve first waiting token when none is currently serving.
        # This ensures the dashboard always shows an active serving token
        # if there are waiting patients. The helper `auto_move_next_token`
        # will check and enforce that only one token is `in_progress` per dept.
        if dept['stats'].get('waiting_count', 0) > 0 and not dept['current_token']:
            try:
                activated = Token.auto_move_next_token(dept['dept_code'])
                if activated:
                    # Refresh the computed values after activation
                    dept['stats'] = Token.get_queue_stats(dept['dept_code'])
                    dept['current_token'] = Token.get_current_serving_token(dept['dept_code'])
                    dept['waiting_tokens'] = Token.get_waiting_tokens(dept['dept_code'])
            except Exception:
                # Fail silently and continue; do not break admin dashboard rendering
                pass
    return render_template(
        'admin_dashboard.html',
        departments=departments,
        admin=get_current_admin_info()
    )


@admin_bp.route('/call-next/<dept_code>', methods=['POST'])
@admin_login_required
def call_next_token(dept_code):
    token = Token.call_next_token(dept_code)
    if token:
        flash(f"Token {token['token_number']} is now in progress", 'success')
    else:
        flash('No waiting token available or a patient is already being served', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/complete/<token_id>', methods=['POST'])
@admin_login_required
def complete_token(token_id):
    token = Token.complete_token(token_id)
    if token and token.get('status') == 'completed':
        next_token = Token.get_current_serving_token(token.get('dept_code'))
        message = f"Token {token['token_number']} marked completed."
        if next_token:
            message += f" Next token {next_token['token_number']} is now serving."
        flash(message, 'success')
    else:
        flash('Unable to complete token. It may already be closed.', 'danger')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/skip/<token_id>', methods=['POST'])
@admin_login_required
def skip_token(token_id):
    token = Token.skip_token(token_id)
    if token and token.get('status') == 'skipped':
        flash(f"Token {token['token_number']} marked skipped", 'warning')
    else:
        flash('Unable to skip token. It may already be closed.', 'danger')
    return redirect(url_for('admin.dashboard'))
