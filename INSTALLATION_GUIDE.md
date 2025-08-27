# Installation Guide - TinderLike Offers

This guide provides multiple installation options to resolve Python 3.13 compatibility issues.

## Option 1: SQLite (Recommended for Quick Start)

The easiest way to get started is using SQLite, which doesn't require PostgreSQL installation.

```bash
# Use the SQLite quick start script
./start-sqlite.sh
```

This will:
- Install all dependencies without PostgreSQL
- Use SQLite database (stored locally as `tinderlike.db`)
- Set up the application for immediate testing

## Option 2: PostgreSQL with Python 3.11/3.12

If you want to use PostgreSQL (recommended for production), use Python 3.11 or 3.12:

### Install Python 3.11 or 3.12
```bash
# Using pyenv (recommended)
pyenv install 3.11.7
pyenv local 3.11.7

# Or using Homebrew on macOS
brew install python@3.11
```

### Install PostgreSQL
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb tinderlike_db
```

### Install Dependencies
```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configure and Run
```bash
# Copy environment file
cp env.example .env

# Edit .env with your database settings
# DATABASE_URL=postgresql://username:password@localhost/tinderlike_db

# Run migrations
alembic upgrade head

# Seed data
python scripts/seed_data.py

# Start application
python run.py
```

## Option 3: Docker (Recommended for Production)

Use Docker to avoid all compatibility issues:

```bash
# Start with Docker Compose
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Start Redis
- Start the FastAPI application
- Serve the frontend via Nginx

## Option 4: Manual Fix for Python 3.13

If you want to use Python 3.13, you can try these steps:

### Install PostgreSQL Development Headers
```bash
# macOS
brew install postgresql libpq

# Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev
```

### Install Rust (for pydantic-core)
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### Try Alternative Requirements
```bash
# Try the alternative requirements file
pip install -r requirements-alt.txt
```

## Troubleshooting

### psycopg2-binary Installation Issues
If you get compilation errors with `psycopg2-binary`:

1. **Use SQLite instead** (Option 1)
2. **Use Python 3.11/3.12** (Option 2)
3. **Install system dependencies**:
   ```bash
   # macOS
   brew install postgresql libpq openssl
   
   # Ubuntu/Debian
   sudo apt-get install libpq-dev python3-dev libssl-dev
   ```

### pydantic-core Compilation Issues
If you get Rust compilation errors:

1. **Install Rust**:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source ~/.cargo/env
   ```

2. **Or use older pydantic version**:
   ```bash
   pip install pydantic==2.4.2
   ```

### Database Connection Issues
If you can't connect to PostgreSQL:

1. **Check if PostgreSQL is running**:
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Ubuntu/Debian
   sudo systemctl status postgresql
   ```

2. **Create database and user**:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE tinderlike_db;
   CREATE USER tinderlike_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE tinderlike_db TO tinderlike_user;
   \q
   ```

## Quick Test

After installation, test the application:

1. **Start the backend**:
   ```bash
   python run.py
   ```

2. **Serve the frontend** (in another terminal):
   ```bash
   cd frontend
   python -m http.server 3000
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Environment Variables

Create a `.env` file with these settings:

```env
# Database (choose one)
DATABASE_URL=sqlite:///./tinderlike.db  # For SQLite
DATABASE_URL=postgresql://user:password@localhost/tinderlike_db  # For PostgreSQL

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (optional for testing)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Other services (optional for testing)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

## Next Steps

1. **Test the application** with sample data
2. **Configure email/SMS services** for notifications
3. **Set up OAuth providers** for social login
4. **Deploy to production** using Docker or your preferred method

For production deployment, see the main README.md file for detailed instructions.
