# Hospital Remote Token Generation System

A full-stack web application built with **Python Flask** for managing hospital OPD (Outpatient Department) queue tokens. Patients can remotely generate tokens before arriving at the hospital, reducing waiting times and improving patient experience.

## 🏥 Project Overview

This system allows patients to:
- Register and authenticate securely
- Select from multiple hospital departments
- Generate queue tokens remotely with estimated waiting times
- Track their queue position
- Cancel tokens if needed
- View token history and status

**Tech Stack:**
- **Backend**: Python Flask with Flask-CORS
- **Frontend**: HTML, CSS, JavaScript (no external frameworks)
- **Templates**: Jinja2
- **Database**: MongoDB
- **Authentication**: Session-based with password hashing

## 📁 Project Structure

```
hospital-token-system/
│
├── app/
│   ├── __init__.py              # Flask app factory
│   │
│   ├── models/
│   │   ├── database.py          # MongoDB connection & initialization
│   │   ├── user.py              # User model & operations
│   │   ├── token.py             # Token model & queue management
│   │   └── department.py        # Department model & info
│   │
│   ├── routes/
│   │   ├── main.py              # Home, dashboard, about routes
│   │   ├── auth.py              # Login, register, logout routes
│   │   └── token.py             # Token generation & queue routes
│   │
│   ├── utils/
│   │   ├── auth.py              # Authentication utilities
│   │   └── token_generator.py   # Token generation utilities
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Additional CSS styles
│   │   ├── js/
│   │   │   └── main.js          # JavaScript interactivity
│   │   └── images/              # Image assets
│   │
│   └── templates/
│       ├── base.html            # Base template with navbar/footer
│       ├── home.html            # Home page
│       ├── login.html           # Login page
│       ├── register.html        # Registration page
│       ├── departments.html     # Department selection
│       ├── generate_token.html  # Token generation confirmation
│       ├── token.html           # Token confirmation page
│       ├── dashboard.html       # User dashboard
│       ├── my_tokens.html       # Token history
│       └── about.html           # About hospital
│
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB (local or cloud instance)
- pip (Python package manager)

### Installation Steps

1. **Clone or extract the project**
   ```bash
   cd hospital-token-system
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MongoDB**
   
   Make sure MongoDB is running. You can:
   - Install MongoDB locally and run `mongod`
   - Or use MongoDB Atlas (cloud service)
   
   Update `.env` file with your MongoDB URI:
   ```
   MONGO_URI=mongodb://localhost:27017/hospital_token_system
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser and visit:
   ```
   http://localhost:5000
   ```

## 📋 Features

### User Authentication
- **Registration**: New users can create accounts with mobile number/email and password
- **Login**: Secure login with session management
- **Validation**: Email and mobile number validation with duplicate checks
- **Password Security**: Passwords are hashed using Werkzeug security

### Department Management
- **5 Departments**: General OPD, Cardiology, Orthopedics, ENT, Neurology
- **Queue Information**: Real-time queue status for each department
- **Estimated Wait Time**: Calculated as 10 minutes per patient

### Token Generation System
- **Two Token Types**:
  - General Tokens: `GEN0001`, `GEN0002`, etc.
  - Department Tokens: `CARD001`, `ORTH002`, `ENT003`, etc.
- **Queue Position**: Shows patient's position in queue
- **Estimated Arrival Time**: Calculated based on queue position
- **Token Status**: Active, Completed, Cancelled

### User Dashboard
- **Profile Information**: View personal details
- **Token History**: See all generated tokens
- **Quick Stats**: Total and active tokens count
- **Token Management**: Cancel tokens if needed

## 🔑 Key Routes

### Authentication Routes
- `GET /auth/register` - Registration form
- `POST /auth/register` - Process registration
- `GET /auth/login` - Login form
- `POST /auth/login` - Process login
- `GET /auth/logout` - Logout user
- `POST /auth/check-mobile` - Check mobile availability (AJAX)
- `POST /auth/check-email` - Check email availability (AJAX)

### Token Routes
- `GET /token/departments` - Department selection page
- `GET /token/generate/<dept_code>` - Token generation form
- `POST /token/generate/<dept_code>` - Generate token
- `GET /token/confirm/<token_id>` - Token confirmation page
- `GET /token/queue-status/<dept_code>` - Queue status (AJAX)
- `GET /token/my-tokens` - Token history
- `POST /token/cancel/<token_id>` - Cancel token

### Main Routes
- `GET /` - Home page
- `GET /dashboard` - User dashboard
- `GET /about` - About hospital

## 💾 Database Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "mobile_number": "9876543210",
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "full_name": "John Doe",
  "created_at": ISODate,
  "updated_at": ISODate,
  "is_active": true
}
```

### Tokens Collection
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "dept_id": ObjectId,
  "token_number": "CARD0001",
  "dept_code": "CARD",
  "dept_name": "Cardiology",
  "queue_position": 5,
  "estimated_wait_time": 40,
  "status": "active",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### Departments Collection
```json
{
  "_id": ObjectId,
  "name": "Cardiology",
  "dept_code": "CARD",
  "description": "Heart and Cardiovascular Diseases",
  "icon": "❤️",
  "queue_count": 5
}
```

## 🎨 UI/UX Design

### Color Scheme
- **Primary**: `#0066cc` (Blue)
- **Dark**: `#004ba6` (Dark Blue)
- **Accent**: `#00d4ff` (Light Blue)
- **Success**: `#28a745` (Green)
- **Danger**: `#dc3545` (Red)
- **Background**: `#f5f7fa` (Light Gray)

### Design Features
- **Modern Healthcare Theme**: Blue and white color scheme
- **Mobile Responsive**: Fully responsive design for all devices
- **Card-Based Layout**: Clean card design for content organization
- **Smooth Animations**: CSS animations for better UX
- **Accessible**: Keyboard navigation and focus states
- **Print-Friendly**: Token can be printed for physical reference

## 🔐 Security Features

1. **Password Security**
   - Passwords are hashed using Werkzeug's security functions
   - Minimum 6 characters required

2. **Session Management**
   - Secure session-based authentication
   - 24-hour session timeout
   - Protected routes with login requirement

3. **Input Validation**
   - Mobile number format validation
   - Email format validation
   - Server-side validation for all inputs
   - CSRF protection via Flask

4. **Data Protection**
   - MongoDB unique indexes on sensitive fields
   - No passwords stored in plain text

## 🧪 Testing the Application

### Demo Account Setup
1. Visit `http://localhost:5000`
2. Click "Register" to create a new account
3. Fill in the registration form:
   - Full Name: John Doe
   - Mobile: 9876543210
   - Email: john@example.com
   - Password: password123

4. Login with your credentials
5. Select a department and generate a token
6. View token details and queue information

### Test Departments
- **General OPD** (GEN)
- **Cardiology** (CARD)
- **Orthopedics** (ORTH)
- **ENT** (ENT)
- **Neurology** (NEUR)

## 🛠️ Development

### Running in Development Mode
The application runs in debug mode by default. Flask will:
- Automatically reload on code changes
- Show detailed error pages
- Enable debugger

### Code Structure
- **Models**: Handle database operations
- **Routes**: Handle HTTP requests and responses
- **Utils**: Contain utility functions
- **Templates**: Contain HTML with Jinja2 templating
- **Static**: Contain CSS and JavaScript files

### Adding New Features

1. **Add a new model** in `app/models/`
2. **Create routes** in appropriate file in `app/routes/`
3. **Create templates** in `app/templates/`
4. **Add styles** to `app/static/css/style.css`
5. **Add JavaScript** to `app/static/js/main.js`

## 📦 Dependencies

- **Flask 2.3.0** - Web framework
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **pymongo 4.3.3** - MongoDB driver
- **python-dotenv 1.0.0** - Environment variable management
- **Werkzeug 2.3.0** - WSGI utilities and password hashing

## 🐛 Common Issues & Solutions

### MongoDB Connection Error
**Problem**: `connection refused` or `cannot connect to MongoDB`

**Solution**:
1. Ensure MongoDB is running
2. Check MONGO_URI in `.env` file
3. Verify MongoDB is accessible on the specified port

### Port Already in Use
**Problem**: `Address already in use`

**Solution**:
1. Change port in `run.py` (default: 5000)
2. Or kill the process using port 5000

### Templates Not Found
**Problem**: `jinja2.exceptions.TemplateNotFound`

**Solution**:
1. Ensure you're running from project root directory
2. Check that `app/templates/` folder exists with all templates

## 📱 Mobile Responsiveness

The application is fully responsive with breakpoints for:
- Desktop (1200px and above)
- Tablet (768px - 1199px)
- Mobile (below 768px)

All forms and cards are mobile-optimized for easy use on smartphones.

## 🚢 Deployment

### Deployment Options

1. **Heroku**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

2. **PythonAnywhere**
   - Upload files to PythonAnywhere
   - Configure WSGI app
   - Add MongoDB URI in environment

3. **AWS/Azure/GCP**
   - Use containerization (Docker)
   - Deploy to App Service/EC2
   - Use managed MongoDB service

### Environment Configuration
For production, update `.env`:
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_production_secret_key_here
MONGO_URI=your_production_mongodb_uri
```

## 📚 Code Examples

### Registering a User
```python
from app.models.user import User

user = User.create_user(
    mobile_number='9876543210',
    email='user@example.com',
    password='password123',
    full_name='John Doe'
)
```

### Generating a Token
```python
from app.models.token import Token

token = Token.create_token(
    user_id='user_object_id',
    dept_id='department_object_id',
    dept_code='CARD',
    dept_name='Cardiology'
)
```

### Getting Queue Status
```python
from app.models.token import Token

stats = Token.get_queue_stats('CARD')
print(stats['active_tokens'])  # Number of active tokens
print(stats['average_wait_time'])  # Average wait time in minutes
```

## 📞 Support & Documentation

- Check inline code comments for detailed explanations
- Review function docstrings for usage examples
- MongoDB documentation: https://docs.mongodb.com/
- Flask documentation: https://flask.palletsprojects.com/

## 📄 License

This project is created for educational purposes. Feel free to use and modify it according to your needs.

## 👥 Contributors

- Project built with Flask best practices
- Beginner-friendly and well-commented code
- Clean architecture with separation of concerns

## 🎓 Learning Outcomes

By studying this project, you'll learn:
- Flask application structure and blueprints
- MongoDB integration with Python
- User authentication and session management
- HTML/CSS/JavaScript frontend development
- Jinja2 templating
- RESTful API design
- Database modeling and queries
- Form validation
- Security best practices

---

**Happy Coding!** 🚀

For questions or improvements, feel free to modify and extend this project!
