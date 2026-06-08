"""
Flask application entry point
Run this file to start the application
"""

import os
from app import create_app
from app.models.database import db_init

# Create Flask application
app = create_app()

# Initialize SQLite database and seed tables
with app.app_context():
    db_init()

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 24 * 60 * 60  # 24 hours

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     Hospital Remote Token Generation System                    ║
    ║     Flask Development Server                                   ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Starting application...
    Visit: http://localhost:5000
    """)
    
    # Run development server
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )
