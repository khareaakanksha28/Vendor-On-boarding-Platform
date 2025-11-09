# Secure & Intelligent Onboarding Hub

A comprehensive platform for automated vendor and client onboarding with ML-powered fraud detection, security assessment, and intelligent workflow management.

## Features

- 🔐 **Secure Authentication** - JWT-based authentication with role-based access control
- 🤖 **ML Fraud Detection** - Advanced machine learning models (SVM, Random Forest, Isolation Forest) for real-time fraud detection
- 📊 **Risk Assessment** - Automated risk scoring and application status management
- 🎨 **Modern UI** - React-based frontend with modern design system
- 🔄 **Workflow Engine** - Automated application processing with dynamic routing
- 📈 **Analytics Dashboard** - Real-time insights and application tracking
- 🔒 **Security Controls** - Comprehensive security compliance validation
- 🛡️ **PII Protection** - Automatic PII detection and masking

## Tech Stack

**Backend:**
- Flask (Python)
- SQLAlchemy (ORM)
- scikit-learn (Machine Learning)
- PostgreSQL/SQLite

**Frontend:**
- React 18
- Tailwind CSS
- Lucide React Icons

## Quick Start

1. **Backend Setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Access:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

## Default Credentials

- Username: `admin`
- Password: `admin123`

## ML Models

The system uses multiple ML models for fraud detection:
- **SVM (RBF)** - Best performing model (97.5% accuracy)
- **Random Forest** - Fallback model (96.9% accuracy)
- **Isolation Forest** - Anomaly detection

Models are automatically selected based on performance metrics.

## Project Structure

```
onboarding-hub/
├── backend/          # Flask API server
├── frontend/         # React application
├── data/            # Training datasets
├── models/          # Trained ML models
└── logs/           # Application logs
```

## Documentation

- `DEPLOYMENT.md` - Deployment guide
- `ARCHITECTURE.md` - System architecture details

## License

MIT
