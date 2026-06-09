"""
Token generation routes blueprint
Handles token generation, department selection, and queue management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app.models.department import Department
from app.models.token import Token
from app.utils.auth import login_required, get_current_user_info
from app.utils.token_generator import calculate_estimated_arrival_time, format_token_response

token_bp = Blueprint('token', __name__)


@token_bp.route('/departments')
@login_required
def departments():
    """
    Department selection page (redesigned)
    Shows list of departments with queue information
    """
    user_info = get_current_user_info()
    departments = Department.get_all_departments()
    
    # Add current queue info for each department
    for dept in departments:
        queue_info = Department.get_department_with_queue_info(dept['dept_code'])
        dept['current_queue'] = queue_info.get('current_queue', 0) if queue_info else 0
        dept['estimated_wait'] = queue_info.get('estimated_wait_time', 0) if queue_info else 0
    
    return render_template(
        'manual_token_redesigned.html',
        user=user_info,
        departments=departments
    )


@token_bp.route('/generate/<dept_code>', methods=['GET', 'POST'])
@login_required
def generate_token(dept_code):
    """
    Generate token for selected department
    
    Args:
        dept_code (str): Department code
    """
    user_info = get_current_user_info()
    
    # Get department info
    department = Department.get_department_by_code(dept_code)
    
    if not department:
        flash('Invalid department selected', 'danger')
        return redirect(url_for('token.departments'))
    
    if request.method == 'POST':
        # Create token
        token = Token.create_token(
            user_info['user_id'],
            str(department['_id']),
            department['dept_code'],
            department['name']
        )
        
        if not token:
            flash('Failed to generate token. Please try again.', 'danger')
            return redirect(url_for('token.departments'))
        
        # Redirect to token confirmation
        flash('Token generated successfully!', 'success')
        return redirect(url_for('token.confirm', token_id=str(token['_id'])))
    
    # GET request - show confirmation page before generation
    queue_info = Department.get_department_with_queue_info(dept_code)
    estimated_queue_position = (queue_info.get('current_queue', 0) if queue_info else 0) + 1
    arrival_info = calculate_estimated_arrival_time(estimated_queue_position)
    
    return render_template(
        'generate_token.html',
        user=user_info,
        department=department,
        estimated_queue_position=estimated_queue_position,
        estimated_wait_time=arrival_info['wait_minutes'],
        estimated_arrival_time=arrival_info['arrival_time']
    )


@token_bp.route('/voice-generate', methods=['POST'])
@login_required
def voice_generate_token():
    """Generate token from voice assistant suggestions."""
    user_info = get_current_user_info()
    request_data = request.get_json(silent=True) or {}
    dept_code = request_data.get('dept_code') or request.form.get('dept_code')

    print('voice_generate_token request.json =', request_data)
    print('voice_generate_token dept_code =', dept_code)

    if not dept_code:
        return jsonify({'success': False, 'message': 'Department code is required.'}), 400

    department = Department.get_department_by_code(dept_code)
    print('voice_generate_token department lookup result =', department)
    if not department:
        return jsonify({'success': False, 'message': 'Invalid department selected.'}), 400

    try:
        token = Token.create_token(
            user_info['user_id'],
            str(department['_id']),
            department['dept_code'],
            department['name']
        )

        if not token:
            return jsonify({'success': False, 'message': 'Failed to generate token.'}), 500

        return jsonify({
            'success': True,
            'token_number': token['token_number'],
            'department': token['dept_name'],
            'message': f"Aapka token {token['token_number']} generate ho gaya hai."
        })

    except Exception as e:
        print(f"Error generating voice token: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while generating the token.'}), 500


@token_bp.route('/generate-token-api', methods=['POST'])
@login_required
def generate_token_api():
    """
    API endpoint to generate token (works for both voice assistant and manual selection)
    Returns JSON response
    """
    user_info = get_current_user_info()
    request_data = request.get_json(silent=True) or {}
    dept_code = request_data.get('dept_code')

    if not dept_code:
        return jsonify({'success': False, 'error': 'Department code is required'}), 400

    department = Department.get_department_by_code(dept_code)
    if not department:
        return jsonify({'success': False, 'error': 'Invalid department selected'}), 400

    try:
        token = Token.create_token(
            user_info['user_id'],
            str(department['_id']),
            department['dept_code'],
            department['name']
        )

        if not token:
            return jsonify({'success': False, 'error': 'Failed to generate token'}), 500

        # Get queue info for the token
        queue_info = Department.get_department_with_queue_info(dept_code)
        queue_position = queue_info.get('current_queue', 1) if queue_info else 1
        estimated_wait = queue_info.get('estimated_wait_time', 10) if queue_info else 10

        return jsonify({
            'success': True,
            'token': {
                '_id': str(token.get('_id')),
                'token_number': token.get('token_number'),
                'dept_code': token.get('dept_code'),
                'dept_name': token.get('dept_name'),
                'queue_position': queue_position,
                'estimated_wait_time': estimated_wait,
                'status': token.get('status')
            }
        })

    except Exception as e:
        print(f"Error generating token: {e}")
        return jsonify({'success': False, 'error': 'An error occurred while generating the token'}), 500


@token_bp.route('/api/departments/stats')
@login_required
def get_departments_stats():
    """
    API endpoint to get fresh department statistics
    Returns JSON with queue info for all departments
    Used by frontend to update department cards after token generation
    """
    try:
        departments = Department.get_all_departments()
        
        # Add current queue info for each department
        stats = []
        for dept in departments:
            queue_info = Department.get_department_with_queue_info(dept['dept_code'])
            stats.append({
                'dept_code': dept['dept_code'],
                'name': dept['name'],
                'icon': dept.get('icon', ''),
                'current_queue': queue_info.get('current_queue', 0) if queue_info else 0,
                'estimated_wait': queue_info.get('estimated_wait_time', 0) if queue_info else 0
            })
        
        return jsonify({'success': True, 'departments': stats})
    
    except Exception as e:
        print(f"Error fetching department stats: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch department statistics'}), 500


@token_bp.route('/confirm/<token_id>')
@login_required
def confirm(token_id):
    """
    Token confirmation page
    Shows generated token details
    
    Args:
        token_id (str): Token ID
    """
    user_info = get_current_user_info()
    
    try:
        # Get token from SQLite storage by ID
        token_doc = Token.get_token_by_id(token_id)
        
        # If not found by ID, try by token number
        if not token_doc:
            token_doc = Token.get_token_by_number(token_id)
        
        if not token_doc:
            flash('Token not found', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Verify token belongs to current user
        token_user_id = str(token_doc.get('user_id'))
        if token_user_id != user_info['user_id']:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.dashboard'))
        
        # Format token data
        arrival_info = calculate_estimated_arrival_time(token_doc.get('queue_position', 1))
        
        token_display = {
            'token_id': str(token_doc.get('_id')),
            'token_number': token_doc.get('token_number'),
            'department': token_doc.get('dept_name'),
            'queue_position': token_doc.get('queue_position'),
            'estimated_wait_time': token_doc.get('estimated_wait_time', 0),
            'estimated_arrival_time': arrival_info['arrival_time'],
            'status': token_doc.get('status'),
            'created_at': token_doc.get('created_at').strftime('%H:%M %p') if token_doc.get('created_at') else None
        }
        
        return render_template(
            'token.html',
            user=user_info,
            token=token_display
        )
    
    except Exception as e:
        print(f"Error in confirm route: {e}")
        flash('An error occurred', 'danger')
        return redirect(url_for('main.dashboard'))


@token_bp.route('/token-result/<token_id>')
@login_required
def token_result(token_id):
    """
    Token result page (redesigned)
    Shows token details after successful generation
    
    Args:
        token_id (str): Token ID
    """
    user_info = get_current_user_info()
    
    try:
        # Get token details
        token_doc = Token.get_token_by_id(token_id)
        
        if not token_doc:
            flash('Token not found', 'danger')
            return redirect(url_for('main.home_dashboard'))
        
        # Verify token belongs to current user
        if str(token_doc.get('user_id')) != user_info['user_id']:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.home_dashboard'))
        
        # Get department info
        department = Department.get_department_by_code(token_doc.get('dept_code'))
        
        # Calculate arrival info
        arrival_info = calculate_estimated_arrival_time(token_doc.get('queue_position', 1))
        
        return render_template(
            'token_result_redesigned.html',
            user=user_info,
            token=token_doc,
            department=department,
            queue_position=token_doc.get('queue_position', 1),
            estimated_wait_time=token_doc.get('estimated_wait_time', 10)
        )
    
    except Exception as e:
        print(f"Error in token result route: {e}")
        flash('An error occurred', 'danger')
        return redirect(url_for('main.home_dashboard'))


@token_bp.route('/print-token/<token_id>')
@login_required
def print_token(token_id):
    """
    Printable token receipt route.
    Fetches token details from SQLite by token ID, verifies the current user,
    and renders a clean print page that automatically opens the browser print dialog.

    Args:
        token_id (str): Token ID
    """
    user_info = get_current_user_info()

    try:
        token_doc = Token.get_token_by_id(token_id)
        if not token_doc:
            flash('Token not found', 'danger')
            return redirect(url_for('main.dashboard'))

        if str(token_doc.get('user_id')) != user_info['user_id']:
            flash('Unauthorized access', 'danger')
            return redirect(url_for('main.dashboard'))

        arrival_info = calculate_estimated_arrival_time(token_doc.get('queue_position', 1))

        token_display = {
            'token_id': str(token_doc.get('_id')),
            'token_number': token_doc.get('token_number'),
            'department': token_doc.get('dept_name'),
            'queue_position': token_doc.get('queue_position'),
            'status': token_doc.get('status'),
            'created_at': token_doc.get('created_at').strftime('%d %b %Y %H:%M') if token_doc.get('created_at') else None,
            'patient_name': user_info.get('full_name') or 'Patient',
            'estimated_arrival_time': arrival_info['arrival_time']
        }

        return render_template(
            'print_token.html',
            user=user_info,
            token=token_display
        )

    except Exception as e:
        print(f"Error in print token route: {e}")
        flash('An error occurred', 'danger')
        return redirect(url_for('main.dashboard'))


@token_bp.route('/queue-status/<dept_code>', methods=['GET'])
def queue_status(dept_code):
    """
    AJAX route to get current queue status for a department
    Returns JSON response
    
    Args:
        dept_code (str): Department code
    """
    try:
        queue_info = Department.get_department_with_queue_info(dept_code)
        
        if not queue_info:
            return jsonify({
                'error': 'Department not found',
                'current_queue': 0,
                'estimated_wait_time': 0
            }), 404
        
        return jsonify({
            'dept_code': dept_code,
            'dept_name': queue_info.get('name'),
            'current_queue': queue_info.get('current_queue', 0),
            'estimated_wait_time': queue_info.get('estimated_wait_time', 0)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@token_bp.route('/my-tokens', methods=['GET'])
@login_required
def my_tokens():
    """
    Show user's all tokens history
    """
    user_info = get_current_user_info()
    tokens = Token.get_user_tokens(user_info['user_id'])
    
    # Format tokens for display
    formatted_tokens = []
    for token in tokens:
        arrival_info = calculate_estimated_arrival_time(token.get('queue_position', 1))
        formatted_tokens.append({
            'token_id': token.get('_id'),
            'token_number': token.get('token_number'),
            'department': token.get('dept_name'),
            'queue_position': token.get('queue_position'),
            'estimated_wait_time': token.get('estimated_wait_time', 0),
            'estimated_arrival_time': arrival_info['arrival_time'],
            'status': token.get('status'),
            'created_at': token.get('created_at').strftime('%d %b %Y %H:%M') if token.get('created_at') else None
        })
    
    return render_template(
        'my_tokens.html',
        user=user_info,
        tokens=formatted_tokens
    )


@token_bp.route('/cancel/<token_id>', methods=['POST'])
@login_required
def cancel_token(token_id):
    """
    Cancel a token
    
    Args:
        token_id (str): Token ID to cancel
    """
    user_info = get_current_user_info()
    
    try:
        # Get token from SQLite storage by ID
        token_doc = Token.get_token_by_id(token_id)
        
        if not token_doc:
            flash('Invalid token ID. Token not found.', 'danger')
            return redirect(url_for('token.my_tokens'))
        
        # Verify token belongs to current user
        if str(token_doc.get('user_id')) != user_info['user_id']:
            flash('Unauthorized token cancellation attempt.', 'danger')
            return redirect(url_for('token.my_tokens'))
        
        # Prevent cancelling already cancelled or completed tokens
        if token_doc.get('status') in ['cancelled', 'completed', 'skipped']:
            status = token_doc.get('status')
            if status == 'cancelled':
                flash('This token has already been cancelled.', 'warning')
            elif status == 'completed':
                flash('This token has already been completed and cannot be cancelled.', 'warning')
            else:
                flash('This token cannot be cancelled.', 'warning')
            return redirect(url_for('token.my_tokens'))
        
        # Cancel token
        cancelled = Token.cancel_token(token_id)
        
        if cancelled and cancelled.get('status') == 'cancelled':
            flash('Token cancelled successfully.', 'success')
            return redirect(url_for('token.my_tokens'))
        else:
            flash('Failed to cancel token. Please try again.', 'danger')
            return redirect(url_for('token.my_tokens'))
    
    except Exception as e:
        print(f"Error cancelling token: {e}")
        flash('An error occurred while cancelling the token.', 'danger')
        return redirect(url_for('token.my_tokens'))
