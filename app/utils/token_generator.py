"""
Token generation and queue management utilities
"""

from datetime import datetime, timedelta


def calculate_estimated_arrival_time(queue_position):
    """
    Calculate estimated arrival time based on queue position
    Assumes 10 minutes per patient
    
    Args:
        queue_position (int): Patient's position in queue
        
    Returns:
        dict: Contains estimated_wait_minutes and estimated_arrival_time
    """
    wait_minutes = (queue_position - 1) * 10
    estimated_arrival = datetime.now() + timedelta(minutes=wait_minutes)
    
    return {
        'wait_minutes': wait_minutes,
        'arrival_time': estimated_arrival.strftime('%H:%M'),
        'arrival_datetime': estimated_arrival
    }


def format_token_response(token_doc):
    """
    Format token document for API response
    
    Args:
        token_doc (dict): Token document from database
        
    Returns:
        dict: Formatted token data for response
    """
    arrival_info = calculate_estimated_arrival_time(token_doc.get('queue_position', 1))
    
    return {
        'token_id': str(token_doc.get('_id', '')),
        'token_number': token_doc.get('token_number'),
        'department': token_doc.get('dept_name'),
        'department_code': token_doc.get('dept_code'),
        'queue_position': token_doc.get('queue_position'),
        'estimated_wait_time': token_doc.get('estimated_wait_time', 0),
        'estimated_arrival_time': arrival_info['arrival_time'],
        'status': token_doc.get('status'),
        'created_at': token_doc.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if token_doc.get('created_at') else None
    }


def get_queue_position_text(position):
    """
    Get human-readable queue position text
    
    Args:
        position (int): Queue position number
        
    Returns:
        str: Human-readable position text
    """
    if position == 1:
        return "Next to be called"
    elif position <= 3:
        return f"{position} in queue"
    else:
        return f"{position} ahead of you"


def format_wait_time(minutes):
    """
    Format wait time in human-readable format
    
    Args:
        minutes (int): Wait time in minutes
        
    Returns:
        str: Formatted wait time string
    """
    if minutes == 0:
        return "No wait"
    elif minutes < 60:
        return f"{minutes} minutes"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours}h {mins}m"
