"""
Department model and operations
Handles department data retrieval and queue information with SQLite storage.
"""

from app.models.database import get_db_connection
from app.models.token import Token


def _row_to_department(row):
    if not row:
        return None
    return {
        '_id': str(row['id']),
        'name': row['dept_name'],
        'dept_code': row['dept_code'],
        'description': row['description'],
        'icon': row['icon'],
        'queue_count': row['queue_count']
    }


class Department:
    """Department model for hospital departments"""
    
    @staticmethod
    def get_all_departments():
        """
        Get all departments
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return [_row_to_department(row) for row in rows]
    
    @staticmethod
    def get_department_by_id(dept_id):
        """
        Get department by ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments WHERE id = ?", (int(dept_id),))
        row = cursor.fetchone()
        conn.close()
        return _row_to_department(row)
    
    @staticmethod
    def get_department_by_code(dept_code):
        """
        Get department by code
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments WHERE dept_code = ?", (dept_code,))
        row = cursor.fetchone()
        conn.close()
        return _row_to_department(row)
    
    @staticmethod
    def get_department_with_queue_info(dept_code):
        """
        Get department with current queue information
        """
        department = Department.get_department_by_code(dept_code)
        if not department:
            return None
        active_tokens = len(Token.get_department_queue(dept_code))
        department['current_queue'] = active_tokens
        department['estimated_wait_time'] = active_tokens * 10
        return department
    
    @staticmethod
    def update_department_queue_count(dept_code, count):
        """
        Update queue count for a department in SQLite storage
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE departments SET queue_count = ? WHERE dept_code = ?",
            (int(count), dept_code)
        )
        conn.commit()
        cursor.execute("SELECT * FROM departments WHERE dept_code = ?", (dept_code,))
        row = cursor.fetchone()
        conn.close()
        return _row_to_department(row)
