"""
Token model and operations
Handles token generation and queue management with SQLite storage.
"""

import sqlite3
from datetime import datetime
from app.models.database import get_db_connection


def _row_to_token(row):
    if not row:
        return None
    return {
        '_id': str(row['id']),
        'user_id': str(row['user_id']),
        'dept_id': str(row['dept_id']),
        'token_number': row['token_number'],
        'dept_code': row['dept_code'],
        'dept_name': row['dept_name'],
        'token_type': row['token_type'],
        'appointment_date': row['appointment_date'],
        'appointment_time': row['appointment_time'],
        'status': row['status'],
        'queue_position': row['queue_position'],
        'estimated_wait_time': row['estimated_wait_time'],
        'created_at': datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
        'updated_at': datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
    }


class Token:
    """Token model for queue management"""
    
    @staticmethod
    def generate_token_number(dept_code):
        """
        Generate the next unique token number for the department.
        """
        prefix = 'GEN' if str(dept_code).upper().strip() == 'GEN' else str(dept_code).upper().strip() or 'GEN'
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token_number FROM tokens WHERE dept_code = ? ORDER BY id DESC LIMIT 1",
            (dept_code,)
        )
        row = cursor.fetchone()
        conn.close()

        next_sequence = 1
        if row and row['token_number']:
            try:
                next_sequence = int(row['token_number'].split('-')[-1]) + 1
            except (ValueError, IndexError):
                next_sequence = 1

        token_number = f"{prefix}-{str(next_sequence).zfill(4)}"
        return token_number

    @staticmethod
    def create_token(user_id, dept_id, dept_code, dept_name):
        """
        Create a new token for a user in SQLite storage.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(1) FROM tokens WHERE dept_code = ? AND status IN ('waiting', 'in_progress')",
            (dept_code,)
        )
        active_count = cursor.fetchone()[0] or 0
        queue_position = active_count + 1
        estimated_wait_time = (queue_position - 1) * 10
        token_type = 'General' if dept_code == 'GEN' else 'Department'
        now = datetime.now().isoformat()
        appointment_date = datetime.now().date().isoformat()
        appointment_time = datetime.now().time().strftime('%H:%M')

        token_id = None
        max_attempts = 5
        for attempt in range(max_attempts):
            token_number = Token.generate_token_number(dept_code)
            try:
                cursor.execute(
                    "INSERT INTO tokens (user_id, dept_id, token_number, dept_code, dept_name, token_type, appointment_date, appointment_time, status, queue_position, estimated_wait_time, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        int(user_id),
                        int(dept_id),
                        token_number,
                        dept_code,
                        dept_name,
                        token_type,
                        appointment_date,
                        appointment_time,
                        'waiting',
                        queue_position,
                        estimated_wait_time,
                        now,
                        now
                    )
                )
                conn.commit()
                token_id = cursor.lastrowid
                break
            except sqlite3.IntegrityError:
                conn.rollback()
                if attempt == max_attempts - 1:
                    conn.close()
                    raise
                continue

        conn.close()
        return Token.get_token_by_id(token_id)
    
    @staticmethod
    def get_token_by_number(token_number):
        """
        Get token by token number.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tokens WHERE token_number = ?",
            (token_number,)
        )
        row = cursor.fetchone()
        conn.close()
        return _row_to_token(row)
    
    @staticmethod
    def get_token_by_id(token_id):
        """
        Get token by ID.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tokens WHERE id = ?",
            (int(token_id),)
        )
        row = cursor.fetchone()
        conn.close()
        return _row_to_token(row)
    
    @staticmethod
    def get_user_tokens(user_id):
        """
        Get all tokens for a user.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tokens WHERE user_id = ? ORDER BY created_at DESC",
            (int(user_id),)
        )
        rows = cursor.fetchall()
        conn.close()
        return [_row_to_token(row) for row in rows]
    
    @staticmethod
    def get_department_queue(dept_code):
        """
        Get all active tokens for a department.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tokens WHERE dept_code = ? AND status IN ('waiting', 'in_progress') ORDER BY queue_position ASC",
            (dept_code,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [_row_to_token(row) for row in rows]
    
    @staticmethod
    def _update_token_status(token_id, status):
        """
        Update the status of a token if it is not already in a terminal state.
        """
        now = datetime.now().isoformat()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tokens SET status = ?, updated_at = ? WHERE id = ? AND status NOT IN ('completed', 'cancelled', 'skipped')",
            (status, now, int(token_id))
        )
        conn.commit()
        conn.close()
        return Token.get_token_by_id(token_id)

    @staticmethod
    def cancel_token(token_id):
        """
        Cancel a token in SQLite storage.
        """
        return Token._update_token_status(token_id, 'cancelled')

    @staticmethod
    def complete_token(token_id):
        """
        Mark a token as completed and automatically advance the next waiting token.

        When a token is completed, this helper updates its status to COMPLETED,
        then calls `auto_move_next_token` for the same department to promote the next
        waiting token to SERVING.
        """
        token_doc = Token.get_token_by_id(token_id)
        if not token_doc:
            return None

        completed_token = Token._update_token_status(token_id, 'completed')

        if completed_token and completed_token.get('status') == 'completed':
            # Advance the next token in the same department automatically.
            Token.auto_move_next_token(completed_token.get('dept_code'))

        return completed_token

    @staticmethod
    def auto_move_next_token(dept_code):
        """
        Automatically move the next waiting token to SERVING for a department.

        This helper finds the waiting token with the smallest queue_position
        for the department and updates its status to in_progress.
        It ignores cancelled and completed tokens and ensures only one
        in-progress token exists per department.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # If there is already a serving token, do not activate another.
        cursor.execute(
            "SELECT id FROM tokens WHERE dept_code = ? AND status = 'in_progress' ORDER BY queue_position ASC LIMIT 1",
            (dept_code,)
        )
        if cursor.fetchone():
            conn.close()
            return None

        # Select the next waiting token by queue_position ascending.
        cursor.execute(
            "SELECT id FROM tokens WHERE dept_code = ? AND status = 'waiting' ORDER BY queue_position ASC LIMIT 1",
            (dept_code,)
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        next_token_id = row['id']
        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE tokens SET status = 'in_progress', updated_at = ? WHERE id = ?",
            (now, next_token_id)
        )
        conn.commit()
        conn.close()
        return Token.get_token_by_id(next_token_id)

    @staticmethod
    def skip_token(token_id):
        """
        Skip a token and mark it as skipped.
        """
        return Token._update_token_status(token_id, 'skipped')

    @staticmethod
    def get_waiting_tokens(dept_code):
        """
        Get waiting tokens for a department.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tokens WHERE dept_code = ? AND status = 'waiting' ORDER BY queue_position ASC",
            (dept_code,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [_row_to_token(row) for row in rows]

    @staticmethod
    def get_current_serving_token(dept_code):
        """
        Get the current in-progress token for a department.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tokens WHERE dept_code = ? AND status = 'in_progress' ORDER BY queue_position ASC LIMIT 1",
            (dept_code,)
        )
        row = cursor.fetchone()
        conn.close()
        return _row_to_token(row)

    @staticmethod
    def call_next_token(dept_code):
        """
        Call the next waiting token into service for a department.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM tokens WHERE dept_code = ? AND status = 'in_progress' ORDER BY queue_position ASC LIMIT 1",
            (dept_code,)
        )
        if cursor.fetchone():
            conn.close()
            return None

        cursor.execute(
            "SELECT id FROM tokens WHERE dept_code = ? AND status = 'waiting' ORDER BY queue_position ASC LIMIT 1",
            (dept_code,)
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        token_id = row['id']
        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE tokens SET status = 'in_progress', updated_at = ? WHERE id = ?",
            (now, token_id)
        )
        conn.commit()
        conn.close()
        return Token.get_token_by_id(token_id)

    @staticmethod
    def get_queue_stats(dept_code):
        """
        Get queue statistics for a department.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(1) FROM tokens WHERE dept_code = ? AND status IN ('waiting', 'in_progress')",
            (dept_code,)
        )
        active_tokens = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(1) FROM tokens WHERE dept_code = ? AND status = 'completed'",
            (dept_code,)
        )
        completed_tokens = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(1) FROM tokens WHERE dept_code = ? AND status = 'cancelled'",
            (dept_code,)
        )
        cancelled_tokens = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(1) FROM tokens WHERE dept_code = ? AND status = 'skipped'",
            (dept_code,)
        )
        skipped_tokens = cursor.fetchone()[0] or 0
        cursor.execute(
            "SELECT COUNT(1) FROM tokens WHERE dept_code = ? AND status = 'in_progress'",
            (dept_code,)
        )
        in_progress_tokens = cursor.fetchone()[0] or 0
        conn.close()
        return {
            'dept_code': dept_code,
            'waiting_count': active_tokens - in_progress_tokens,
            'in_progress_count': in_progress_tokens,
            'completed_count': completed_tokens,
            'cancelled_count': cancelled_tokens,
            'skipped_count': skipped_tokens,
            'active_count': active_tokens,
            'average_wait_time': active_tokens * 10 if active_tokens > 0 else 0
        }
