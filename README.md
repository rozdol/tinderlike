# TinderLike Offers - FastAPI Application

A Tinder-like web application for offers and promotions, built with FastAPI and modern web technologies.

## Features

- **Tinder-like Swiping Interface**: Swipe through offers with like/dislike functionality
- **User Authentication**: Registration, login, and OAuth support (Google, Apple)
- **Email & Phone Verification**: Secure account verification system
- **Offer Management**: Browse, like, and manage promotional offers
- **Multiple Notification Channels**: Email, SMS, WhatsApp, and Telegram notifications
- **Countdown Timers**: Real-time expiry countdown for offers
- **Mobile-First Design**: Responsive, touch-friendly interface
- **OAuth Integration**: Google and Apple sign-in support

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Alembic**: Database migrations
- **JWT**: Authentication tokens
- **Pydantic**: Data validation

### Frontend
- **HTML5/CSS3**: Modern, responsive design
- **JavaScript (ES6+)**: Interactive functionality
- **Font Awesome**: Icons
- **Mobile-First**: Touch-optimized interface

### Services
- **Email Service**: SMTP integration
- **SMS Service**: Twilio integration
- **WhatsApp**: Twilio WhatsApp API
- **Telegram**: Telegram Bot API

## Project Structure

```
tinderlike/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── offers.py        # Offer management routes
│   │   ├── users.py         # User profile routes
│   │   └── notifications.py # Notification routes
│   └── services/            # Business logic services
│       ├── __init__.py
│       ├── notification_service.py
│       ├── verification_service.py
│       └── oauth_service.py
├── frontend/                # Frontend application
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── alembic/                 # Database migrations
│   ├── env.py
│   └── script.py.mako
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── alembic.ini             # Alembic configuration
└── README.md
```

## Database Schema

### Users
- Basic user information (email, phone, name)
- OAuth integration fields
- Notification preferences
- Verification status

### Offers
- Offer details (title, description, image)
- Provider information
- Pricing and discount details
- Referral links and promo codes
- Expiry timestamps

### UserLikes
- User-offer relationships
- Like timestamps

### Notifications
- User notification history
- Multiple notification types
- Read/unread status

### VerificationCodes
- Email and phone verification codes
- Expiry management

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)
- Node.js (for frontend development, optional)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd tinderlike
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/tinderlike_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=your-apple-client-id
APPLE_TEAM_ID=your-apple-team-id
APPLE_KEY_ID=your-apple-key-id
APPLE_PRIVATE_KEY=your-apple-private-key

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 5. Database Setup

Create PostgreSQL database:

```sql
CREATE DATABASE tinderlike_db;
```

Run database migrations:

```bash
alembic upgrade head
```

### 6. Run the Application

#### Development Mode

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Serve frontend (using Python's built-in server)
cd frontend
python -m http.server 3000
```

#### Production Mode

```bash
# Using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 7. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/verify` - Account verification
- `POST /api/v1/auth/oauth` - OAuth login
- `GET /api/v1/auth/me` - Get current user

### Offers
- `GET /api/v1/offers/` - Get available offers
- `GET /api/v1/offers/next` - Get next offer for swiping
- `POST /api/v1/offers/swipe` - Swipe on offer (like/dislike)
- `GET /api/v1/offers/liked` - Get liked offers
- `DELETE /api/v1/offers/liked/{offer_id}` - Unlike offer

### Users
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `POST /api/v1/users/telegram-connect` - Connect Telegram

### Notifications
- `GET /api/v1/notifications/` - Get all notifications
- `GET /api/v1/notifications/unread` - Get unread notifications
- `PUT /api/v1/notifications/{id}/read` - Mark notification as read
- `DELETE /api/v1/notifications/{id}` - Delete notification

## Frontend Features

### Authentication Flow
1. **Registration**: Email, phone, and verification
2. **Login**: Email/password or OAuth
3. **Verification**: Email and phone code verification

### Main Interface
1. **Swipe Area**: Tinder-like card interface
2. **Offer Details**: Comprehensive offer information
3. **Liked Offers**: Saved offers management
4. **Profile Settings**: User preferences and notifications

### Mobile Optimization
- Touch-friendly swipe gestures
- Responsive design for all screen sizes
- Fast loading and smooth animations
- Offline capability (basic)

## Configuration Options

### Email Service
Configure SMTP settings for email notifications and verification.

### SMS Service (Twilio)
Set up Twilio account for SMS and WhatsApp notifications.

### Telegram Bot
Create a Telegram bot for instant messaging notifications.

### OAuth Providers
Configure Google and Apple OAuth for social login.

## Development

### Adding New Features

1. **Database Changes**: Create new Alembic migration
2. **API Endpoints**: Add routes in appropriate API module
3. **Frontend**: Update HTML/CSS/JS as needed
4. **Testing**: Add tests for new functionality

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions
- Include type hints where possible

### Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Environment Variables

Ensure all required environment variables are set in production:
- Database connection string
- Secret keys
- API keys for external services
- Frontend URL

### Security Considerations

- Use HTTPS in production
- Set secure secret keys
- Configure CORS properly
- Implement rate limiting
- Regular security updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the code comments and docstrings

## Roadmap

- [ ] Advanced swipe animations
- [ ] Push notifications
- [ ] Offer categories and filtering
- [ ] User preferences and recommendations
- [ ] Analytics and reporting
- [ ] Admin dashboard
- [ ] Mobile app (React Native)
- [ ] Real-time chat support
- [ ] Payment integration
- [ ] Advanced OAuth providers
