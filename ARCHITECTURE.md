# System Architecture

## Overview

The Onboarding Hub is a full-stack application designed for secure vendor and client onboarding with integrated fraud detection and risk assessment capabilities.

## Architecture Components

### Backend (Flask API)
- RESTful API server
- JWT-based authentication
- SQLAlchemy ORM for database operations
- ML model integration for fraud detection
- Role-based access control

### Frontend (React)
- Single-page application
- Modern UI with Tailwind CSS
- Real-time dashboard and analytics
- Application management interface

### Database
- PostgreSQL (production)
- SQLite (development)
- Stores applications, users, security controls, audit logs

### ML Models
- SVM (RBF) - Primary fraud detection model
- Random Forest - Fallback model
- Isolation Forest - Anomaly detection

## Data Flow

1. User submits onboarding application
2. System extracts features and runs fraud detection
3. Risk score calculated based on multiple factors
4. Application status determined (approved/pending/flagged)
5. Security controls validated
6. PII detected and masked
7. Audit logs created

## Security Features

- JWT token-based authentication
- Password hashing with Werkzeug
- Role-based access control (admin, reviewer, user)
- PII detection and masking
- Comprehensive audit logging
- Security control validation

## Scalability

- Stateless API design
- Database connection pooling
- Caching support (Redis optional)
- Docker containerization for easy deployment
