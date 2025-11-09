# Deployment Guide

This document provides deployment instructions for the Onboarding Hub platform.

## Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (for production) or SQLite (for development)

## Environment Setup

Create `backend/.env` file with:
```env
DATABASE_URL=sqlite:///onboarding.db
JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

## Local Development

1. Install backend dependencies: `pip install -r backend/requirements.txt`
2. Install frontend dependencies: `npm install` (in frontend directory)
3. Start backend: `python backend/app.py`
4. Start frontend: `npm start` (in frontend directory)

## Production Deployment

### Using Docker
```bash
docker-compose up -d
```

### Manual Deployment
1. Set `FLASK_ENV=production` in `.env`
2. Use PostgreSQL database
3. Build frontend: `cd frontend && npm run build`
4. Serve with nginx/apache or process manager (PM2)

## ML Model Training

Train models using:
```bash
python3 train_ml_models_comparison.py
```

This will compare multiple models and save the best performing one.

## Security Notes

- Change `JWT_SECRET_KEY` to a secure random value
- Use HTTPS in production
- Set `FLASK_DEBUG=False` in production
- Use environment-specific configuration files
