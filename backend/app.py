from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import hashlib
from datetime import datetime, timedelta
import re
import os
import uuid
from functools import wraps
from config import Config

# Import fraud detection model
try:
    from ml_fraud_detection_enhanced import fraud_model
except ImportError:
    from ml_fraud_detection import fraud_model

app = Flask(__name__)
app.config.from_object(Config)

# Database configuration - use SQLite for local development
database_url = os.getenv('DATABASE_URL', 'sqlite:///onboarding.db')
# If DATABASE_URL points to PostgreSQL but it's not available, fall back to SQLite
if 'postgresql' in database_url.lower() or 'postgres' in database_url.lower():
    try:
        # Test PostgreSQL connection
        import psycopg2
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 5432,
            user=parsed.username or 'user',
            password=parsed.password or 'password',
            database=parsed.path[1:] if parsed.path else 'onboarding'
        )
        conn.close()
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    except:
        # Fall back to SQLite if PostgreSQL is not available
        print("⚠️ PostgreSQL not available, using SQLite for local development")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///onboarding.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']))
db = SQLAlchemy(app)
jwt = JWTManager(app)

# ============== DATABASE MODELS ==============

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='reviewer')  # admin, reviewer, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        # Use pbkdf2:sha256 method for Python 3.9 compatibility (scrypt not available)
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # vendor, client
    company_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip = db.Column(db.String(20))
    tax_id = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending_review')
    risk_score = db.Column(db.Float)
    fraud_score = db.Column(db.Float)
    fraud_detection_result = db.Column(db.Text)  # JSON string
    submitted_date = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    
    # Relationships
    security_controls = db.relationship('SecurityControl', backref='application', lazy=True, cascade='all, delete-orphan')
    pii_data = db.relationship('PIIData', backref='application', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='application', lazy=True, cascade='all, delete-orphan')


class SecurityControl(db.Model):
    __tablename__ = 'security_controls'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    control_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Boolean, default=False)


class PIIData(db.Model):
    __tablename__ = 'pii_data'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    pii_type = db.Column(db.String(50), nullable=False)
    masked_value = db.Column(db.String(200))
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ApplicationComment(db.Model):
    __tablename__ = 'application_comments'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='comments')
    application = db.relationship('Application', backref='comments')


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # certificate, contract, etc.
    file_size = db.Column(db.Integer)  # in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='uploaded_documents')
    application = db.relationship('Application', backref='documents')


# ============== UTILITY FUNCTIONS ==============

def detect_pii(data):
    """Detect PII in application data"""
    pii_fields = []
    patterns = {
        'ssn': r'\d{3}-\d{2}-\d{4}',
        'phone': r'\d{3}-\d{3}-\d{4}',
        'email': r'@'
    }
    
    for key, value in data.items():
        if isinstance(value, str):
            if 'ssn' in key.lower() or re.match(patterns['ssn'], value):
                pii_fields.append({'field': key, 'type': 'SSN', 'value': value})
            elif 'phone' in key.lower() or re.match(patterns['phone'], value):
                pii_fields.append({'field': key, 'type': 'Phone', 'value': value})
            elif 'email' in key.lower() or '@' in value:
                pii_fields.append({'field': key, 'type': 'Email', 'value': value})
            elif 'address' in key.lower():
                pii_fields.append({'field': key, 'type': 'Address', 'value': value})
    
    return pii_fields


def mask_pii(value, pii_type):
    """Mask PII data"""
    if not value:
        return ''
    
    if pii_type == 'SSN':
        return '***-**-' + value[-4:]
    elif pii_type == 'Phone':
        return '***-***-' + value[-4:]
    elif pii_type == 'Email':
        if '@' in value:
            name, domain = value.split('@')
            return name[:2] + '***@' + domain
        return value
    elif pii_type == 'Address':
        words = value.split(' ')
        return ' '.join(words[:2] + ['***'] * (len(words) - 2))
    return value


def calculate_risk_score(data):
    """Calculate risk score for application"""
    score = 100
    
    # Email domain check
    email = data.get('email', '')
    if '@gmail.com' in email or '@yahoo.com' in email:
        score -= 10
    
    # Missing information penalties
    if not data.get('tax_id'):
        score -= 20
    if not data.get('address') or not data.get('city') or not data.get('state'):
        score -= 10
    
    # Industry risk
    high_risk_industries = ['Cryptocurrency', 'Gambling', 'Cannabis']
    if data.get('industry') in high_risk_industries:
        score -= 15
    
    # Security controls check
    security_cols = ['mfaEnabled', 'ssoSupport', 'rbacImplemented', 'encryptionAtRest',
                    'encryptionInTransit', 'keyManagement', 'firewallEnabled', 'vpnRequired',
                    'ipWhitelisting', 'auditLogging', 'siemIntegration', 'alertingEnabled',
                    'gdprCompliant', 'soc2Certified', 'isoCompliant']
    security_count = sum(1 for col in security_cols if data.get(col, False))
    if security_count < 5:
        score -= (15 - security_count) * 2
    
    return max(0, min(100, score))


def log_audit(application_id, user_id, action, details, ip_address):
    """Create audit log entry"""
    log = AuditLog(
        application_id=application_id,
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()


def role_required(required_role):
    """Decorator to check user role"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            role_hierarchy = {'viewer': 1, 'reviewer': 2, 'admin': 3}
            
            if role_hierarchy.get(user.role, 0) < role_hierarchy.get(required_role, 999):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ============== AUTHENTICATION ENDPOINTS ==============

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'onboarding-hub-api',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route(f'{Config.API_PREFIX}/auth/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'reviewer')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'User created successfully',
        'user_id': user.id,
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 201


@app.route(f'{Config.API_PREFIX}/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 200


# ============== APPLICATION ENDPOINTS ==============

@app.route(f'{Config.API_PREFIX}/applications', methods=['GET'])
@jwt_required()
def get_applications():
    """Get all applications with filters and search"""
    status = request.args.get('status')
    type_ = request.args.get('type')
    search = request.args.get('search', '').strip()
    min_risk = request.args.get('min_risk')
    max_risk = request.args.get('max_risk')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    query = Application.query
    
    # Status filter
    if status:
        query = query.filter_by(status=status)
    
    # Type filter
    if type_:
        query = query.filter_by(type=type_)
    
    # Search filter (company name, email)
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Application.company_name.ilike(search_pattern),
                Application.email.ilike(search_pattern),
                Application.industry.ilike(search_pattern)
            )
        )
    
    # Risk score filters
    if min_risk:
        try:
            query = query.filter(Application.risk_score >= float(min_risk))
        except:
            pass
    if max_risk:
        try:
            query = query.filter(Application.risk_score <= float(max_risk))
        except:
            pass
    
    # Date range filters
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(Application.submitted_date >= from_date)
        except:
            pass
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(Application.submitted_date <= to_date)
        except:
            pass
    
    pagination = query.order_by(Application.submitted_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    applications = [{
        'id': app.id,
        'type': app.type,
        'company_name': app.company_name,
        'email': app.email,
        'phone': app.phone,
        'status': app.status,
        'risk_score': app.risk_score,
        'fraud_score': app.fraud_score,
        'submitted_date': app.submitted_date.isoformat() if app.submitted_date else None
    } for app in pagination.items]
    
    return jsonify({
        'applications': applications,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@app.route(f'{Config.API_PREFIX}/applications/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    """Get single application with full details"""
    app = Application.query.get_or_404(app_id)
    
    # Get security controls
    controls = {}
    for ctrl in app.security_controls:
        if ctrl.category not in controls:
            controls[ctrl.category] = {}
        controls[ctrl.category][ctrl.control_name] = ctrl.status
    
    # Get PII data
    pii = [{
        'field': p.field_name,
        'type': p.pii_type,
        'masked_value': p.masked_value
    } for p in app.pii_data]
    
    # Get audit logs
    logs = [{
        'action': log.action,
        'details': log.details,
        'timestamp': log.timestamp.isoformat() if log.timestamp else None,
        'user_id': log.user_id
    } for log in app.audit_logs]
    
    # Get comments
    comments = [{
        'id': c.id,
        'comment': c.comment,
        'user_id': c.user_id,
        'username': c.user.username if c.user else 'Unknown',
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in app.comments]
    
    # Parse fraud detection result
    fraud_result = None
    if app.fraud_detection_result:
        import json
        try:
            fraud_result = json.loads(app.fraud_detection_result)
        except:
            pass
    
    return jsonify({
        'id': app.id,
        'type': app.type,
        'company_name': app.company_name,
        'email': app.email,
        'phone': app.phone,
        'address': app.address,
        'city': app.city,
        'state': app.state,
        'zip': app.zip,
        'tax_id': app.tax_id,
        'industry': app.industry,
        'description': app.description,
        'status': app.status,
        'risk_score': app.risk_score,
        'fraud_score': app.fraud_score,
        'fraud_detection': fraud_result,
        'submitted_date': app.submitted_date.isoformat() if app.submitted_date else None,
        'security_controls': controls,
        'pii_detected': pii,
        'audit_logs': logs,
        'comments': comments
    }), 200


@app.route(f'{Config.API_PREFIX}/applications', methods=['POST'])
@jwt_required()
def create_application():
    """Create new application for vendor/client onboarding"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = int(get_jwt_identity())
        
        # Validate required fields
        if not data.get('company_name') or not data.get('email'):
            return jsonify({'error': 'Company name and email are required'}), 400
        
        # Run fraud detection
        try:
            fraud_result = fraud_model.predict(data)
            fraud_score = fraud_result.get('fraud_score', 0)
        except Exception as e:
            print(f"Fraud detection error: {e}")
            # Fallback fraud detection result
            fraud_result = {
                'is_fraud': False,
                'fraud_score': 0.5,
                'risk_level': 'medium',
                'model_type': 'fallback'
            }
            fraud_score = 0.5
        
        # Calculate risk score
        risk_score = calculate_risk_score(data)
        
        # Adjust risk score based on fraud detection
        if fraud_result.get('is_fraud', False):
            risk_score = min(risk_score, 30)
        elif fraud_result.get('risk_level') == 'high':
            risk_score = min(risk_score, 50)
        elif fraud_result.get('risk_level') == 'medium':
            risk_score = min(risk_score, 70)
        
        # Determine initial status based on risk and fraud detection
        # Auto-approve: Very low fraud score (< 0.1), low risk level, high risk score (>= 85), good security controls
        security_controls_count = sum([
            data.get('mfaEnabled', False), data.get('ssoSupport', False),
            data.get('encryptionAtRest', False), data.get('encryptionInTransit', False),
            data.get('firewallEnabled', False), data.get('gdprCompliant', False)
        ])
        
        if fraud_result.get('is_fraud', False) or fraud_result.get('risk_level') == 'high':
            status = 'flagged'
        elif (fraud_result.get('fraud_score', 1) < 0.1 and 
              fraud_result.get('risk_level') == 'low' and 
              risk_score >= 85 and 
              security_controls_count >= 4):
            # Auto-approve very low-risk applications with good security
            status = 'approved'
        elif risk_score >= 70:
            status = 'pending_review'
        else:
            status = 'flagged'
        
        # Create application
        app = Application(
            type=data.get('type', 'vendor'),
            company_name=data.get('company_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip=data.get('zip'),
            tax_id=data.get('tax_id'),
            industry=data.get('industry'),
            description=data.get('description'),
            status=status,
            risk_score=risk_score,
            fraud_score=fraud_score
        )
        
        # Store fraud detection result as JSON
        import json
        app.fraud_detection_result = json.dumps(fraud_result)
        
        db.session.add(app)
        db.session.flush()
        
        # Save security controls
        security_controls = {
            'Identity & Access Management': ['mfaEnabled', 'ssoSupport', 'rbacImplemented'],
            'Data Encryption': ['encryptionAtRest', 'encryptionInTransit', 'keyManagement'],
            'Network Security': ['firewallEnabled', 'vpnRequired', 'ipWhitelisting'],
            'Logging & Monitoring': ['auditLogging', 'siemIntegration', 'alertingEnabled'],
            'Compliance': ['gdprCompliant', 'soc2Certified', 'isoCompliant']
        }
        
        for category, controls in security_controls.items():
            for control in controls:
                ctrl = SecurityControl(
                    application_id=app.id,
                    category=category,
                    control_name=control,
                    status=data.get(control, False)
                )
                db.session.add(ctrl)
        
        # Detect and save PII
        pii_detected = detect_pii(data)
        for pii in pii_detected:
            pii_record = PIIData(
                application_id=app.id,
                field_name=pii['field'],
                pii_type=pii['type'],
                masked_value=mask_pii(pii['value'], pii['type'])
            )
            db.session.add(pii_record)
        
        # Create audit log
        log_audit(
            app.id,
            user_id,
            'APPLICATION_CREATED',
            f"New {data.get('type', 'vendor')} application submitted",
            request.remote_addr
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Application created successfully',
            'application_id': app.id,
            'risk_score': risk_score,
            'fraud_score': fraud_score,
            'fraud_detection': fraud_result,
            'status': status
        }), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creating application: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to create application: {str(e)}'}), 500


@app.route(f'{Config.API_PREFIX}/applications/<int:app_id>/status', methods=['PUT'])
@role_required('reviewer')
def update_application_status(app_id):
    """Update application status with optional comment"""
    data = request.get_json()
    user_id = int(get_jwt_identity())
    
    app = Application.query.get_or_404(app_id)
    old_status = app.status
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
    
    app.status = new_status
    app.reviewed_by = user_id
    app.reviewed_at = datetime.utcnow()
    
    # Add comment if provided
    comment_text = data.get('comment', '').strip()
    if comment_text:
        comment = ApplicationComment(
            application_id=app.id,
            user_id=user_id,
            comment=comment_text
        )
        db.session.add(comment)
    
    # Create audit log
    log_audit(
        app.id,
        user_id,
        'STATUS_CHANGED',
        f"Status changed from {old_status} to {new_status}. Comment: {comment_text[:100] if comment_text else 'N/A'}",
        request.remote_addr
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Status updated successfully',
        'status': new_status
    }), 200


@app.route(f'{Config.API_PREFIX}/applications/<int:app_id>/comments', methods=['POST'])
@jwt_required()
def add_application_comment(app_id):
    """Add a comment to an application"""
    data = request.get_json()
    user_id = int(get_jwt_identity())
    
    comment_text = data.get('comment', '').strip()
    if not comment_text:
        return jsonify({'error': 'Comment is required'}), 400
    
    app = Application.query.get_or_404(app_id)
    
    comment = ApplicationComment(
        application_id=app.id,
        user_id=user_id,
        comment=comment_text
    )
    db.session.add(comment)
    
    # Create audit log
    log_audit(
        app.id,
        user_id,
        'COMMENT_ADDED',
        f"Comment added: {comment_text[:100]}",
        request.remote_addr
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Comment added successfully',
        'comment': {
            'id': comment.id,
            'comment': comment.comment,
            'user_id': comment.user_id,
            'created_at': comment.created_at.isoformat() if comment.created_at else None
        }
    }), 201


@app.route(f'{Config.API_PREFIX}/applications/<int:app_id>/comments', methods=['GET'])
@jwt_required()
def get_application_comments(app_id):
    """Get all comments for an application"""
    app = Application.query.get_or_404(app_id)
    
    comments = ApplicationComment.query.filter_by(application_id=app_id)\
        .order_by(ApplicationComment.created_at.desc()).all()
    
    return jsonify({
        'comments': [{
            'id': c.id,
            'comment': c.comment,
            'user_id': c.user_id,
            'username': c.user.username if c.user else 'Unknown',
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in comments]
    }), 200


# ============== ANALYTICS ENDPOINTS ==============

@app.route(f'{Config.API_PREFIX}/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get dashboard analytics"""
    total = Application.query.count()
    pending = Application.query.filter_by(status='pending_review').count()
    approved = Application.query.filter_by(status='approved').count()
    flagged = Application.query.filter_by(status='flagged').count()
    
    # Average risk score
    from sqlalchemy import func
    avg_risk = db.session.query(func.avg(Application.risk_score)).scalar() or 0
    
    # Applications by type
    by_type = db.session.query(
        Application.type, 
        func.count(Application.id)
    ).group_by(Application.type).all()
    
    # Applications by status
    by_status = db.session.query(
        Application.status,
        func.count(Application.id)
    ).group_by(Application.status).all()
    
    # Recent applications
    recent = Application.query.order_by(
        Application.submitted_date.desc()
    ).limit(10).all()
    
    return jsonify({
        'summary': {
            'total': total,
            'pending': pending,
            'approved': approved,
            'flagged': flagged,
            'avg_risk_score': round(avg_risk, 2)
        },
        'by_type': dict(by_type),
        'by_status': dict(by_status),
        'recent': [{
            'id': app.id,
            'company_name': app.company_name,
            'status': app.status,
            'submitted_date': app.submitted_date.isoformat() if app.submitted_date else None
        } for app in recent]
    }), 200


@app.route(f'{Config.API_PREFIX}/analytics/risk-trends', methods=['GET'])
@jwt_required()
def get_risk_trends():
    """Get risk score trends"""
    days = int(request.args.get('days', 30))
    start_date = datetime.utcnow() - timedelta(days=days)
    
    from sqlalchemy import func
    
    # Risk scores over time
    trends = db.session.query(
        func.date(Application.submitted_date).label('date'),
        func.avg(Application.risk_score).label('avg_risk'),
        func.count(Application.id).label('count')
    ).filter(
        Application.submitted_date >= start_date
    ).group_by(
        func.date(Application.submitted_date)
    ).all()
    
    return jsonify({
        'trends': [{
            'date': str(t.date),
            'avg_risk_score': round(t.avg_risk, 2),
            'application_count': t.count
        } for t in trends]
    }), 200


# ============== AUDIT LOG ENDPOINTS ==============

@app.route(f'{Config.API_PREFIX}/audit-logs', methods=['GET'])
@role_required('admin')
def get_audit_logs():
    """Get audit logs"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    pagination = AuditLog.query.order_by(
        AuditLog.timestamp.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    logs = [{
        'id': log.id,
        'application_id': log.application_id,
        'user_id': log.user_id,
        'action': log.action,
        'details': log.details,
        'ip_address': log.ip_address,
        'timestamp': log.timestamp.isoformat() if log.timestamp else None
    } for log in pagination.items]
    
    return jsonify({
        'logs': logs,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


# ============== USER MANAGEMENT ENDPOINTS ==============

@app.route(f'{Config.API_PREFIX}/users', methods=['GET'])
@role_required('admin')
def get_users():
    """Get all users (admin only)"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    pagination = User.query.order_by(User.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = [{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'created_at': None  # Add if you have this field
    } for u in pagination.items]
    
    return jsonify({
        'users': users,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@app.route(f'{Config.API_PREFIX}/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    """Update user (admin only)"""
    data = request.get_json()
    admin_id = int(get_jwt_identity())
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from modifying themselves
    if user_id == admin_id and data.get('role') != user.role:
        return jsonify({'error': 'Cannot change your own role'}), 400
    
    # Update fields
    if 'role' in data:
        user.role = data['role']
    if 'email' in data:
        user.email = data['email']
    
    # Create audit log
    log_audit(
        None,
        admin_id,
        'USER_UPDATED',
        f"User {user.username} updated by admin",
        request.remote_addr
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 200


@app.route(f'{Config.API_PREFIX}/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """Delete user (admin only)"""
    admin_id = int(get_jwt_identity())
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user_id == admin_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    username = user.username
    
    # Create audit log before deletion
    log_audit(
        None,
        admin_id,
        'USER_DELETED',
        f"User {username} deleted by admin",
        request.remote_addr
    )
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': f'User {username} deleted successfully'}), 200


# ============== DOCUMENT UPLOAD ENDPOINTS ==============

@app.route(f'{Config.API_PREFIX}/applications/<int:app_id>/documents', methods=['POST'])
@jwt_required()
def upload_document(app_id):
    """Upload a document for an application"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    file_type = request.form.get('file_type', 'document')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
    filename = file.filename
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG, TXT'}), 400
    
    # Validate file size (max 10MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        return jsonify({'error': 'File too large. Maximum size: 10MB'}), 400
    
    # Create uploads directory
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'documents')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(uploads_dir, unique_filename)
    
    # Save file
    file.save(file_path)
    
    # Create document record
    user_id = int(get_jwt_identity())
    app = Application.query.get_or_404(app_id)
    
    document = Document(
        application_id=app_id,
        user_id=user_id,
        filename=unique_filename,
        original_filename=secure_filename(filename),
        file_path=file_path,
        file_type=file_type,
        file_size=file_size
    )
    
    db.session.add(document)
    
    # Create audit log
    log_audit(
        app_id,
        user_id,
        'DOCUMENT_UPLOADED',
        f"Document uploaded: {secure_filename(filename)}",
        request.remote_addr
    )
    
    db.session.commit()
    
    return jsonify({
        'message': 'Document uploaded successfully',
        'document': {
            'id': document.id,
            'filename': document.original_filename,
            'file_type': document.file_type,
            'file_size': document.file_size,
            'uploaded_at': document.uploaded_at.isoformat() if document.uploaded_at else None
        }
    }), 201


@app.route(f'{Config.API_PREFIX}/applications/<int:app_id>/documents', methods=['GET'])
@jwt_required()
def get_application_documents(app_id):
    """Get all documents for an application"""
    app = Application.query.get_or_404(app_id)
    
    documents = Document.query.filter_by(application_id=app_id)\
        .order_by(Document.uploaded_at.desc()).all()
    
    return jsonify({
        'documents': [{
            'id': d.id,
            'filename': d.original_filename,
            'file_type': d.file_type,
            'file_size': d.file_size,
            'uploaded_by': d.user.username if d.user else 'Unknown',
            'uploaded_at': d.uploaded_at.isoformat() if d.uploaded_at else None
        } for d in documents]
    }), 200


@app.route(f'{Config.API_PREFIX}/documents/<int:doc_id>/download', methods=['GET'])
@jwt_required()
def download_document(doc_id):
    """Download a document"""
    
    document = Document.query.get_or_404(doc_id)
    
    if not os.path.exists(document.file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        document.file_path,
        as_attachment=True,
        download_name=document.original_filename
    )


@app.route(f'{Config.API_PREFIX}/documents/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    """Delete a document"""
    
    document = Document.query.get_or_404(doc_id)
    user_id = int(get_jwt_identity())
    
    # Only allow deletion by uploader or admin
    if document.user_id != user_id:
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete file
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except:
            pass
    
    # Create audit log
    log_audit(
        document.application_id,
        user_id,
        'DOCUMENT_DELETED',
        f"Document deleted: {document.original_filename}",
        request.remote_addr
    )
    
    db.session.delete(document)
    db.session.commit()
    
    return jsonify({'message': 'Document deleted successfully'}), 200


# ============== EXPORT ENDPOINTS ==============

@app.route(f'{Config.API_PREFIX}/applications/export/csv', methods=['GET'])
@jwt_required()
def export_applications_csv():
    """Export applications to CSV"""
    import csv
    from io import StringIO
    
    status = request.args.get('status')
    type_ = request.args.get('type')
    search = request.args.get('search', '').strip()
    
    query = Application.query
    
    if status:
        query = query.filter_by(status=status)
    if type_:
        query = query.filter_by(type=type_)
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Application.company_name.ilike(search_pattern),
                Application.email.ilike(search_pattern)
            )
        )
    
    applications = query.order_by(Application.submitted_date.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Type', 'Company Name', 'Email', 'Phone', 'Industry',
        'Status', 'Risk Score', 'Fraud Score', 'Submitted Date'
    ])
    
    # Write data
    for app in applications:
        writer.writerow([
            app.id,
            app.type,
            app.company_name,
            app.email,
            app.phone or '',
            app.industry or '',
            app.status,
            app.risk_score or 0,
            app.fraud_score or 0,
            app.submitted_date.isoformat() if app.submitted_date else ''
        ])
    
    output.seek(0)
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=applications.csv'}
    )


# ============== DATA IMPORT ENDPOINTS ==============

@app.route(f'{Config.API_PREFIX}/import/kaggle-data', methods=['POST'])
@role_required('admin')
def import_kaggle_data():
    """Import applications from Kaggle CSV data"""
    try:
        import pandas as pd
        import json
        import os
        
        # Look for CSV files in data directory (relative to project root)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_files = [
            os.path.join(base_dir, 'data', 'onboarding_train.csv'),
            os.path.join(base_dir, 'data', 'onboarding_test.csv'),
            os.path.join(base_dir, 'data', 'supplier_quality_data.csv')
        ]
        
        csv_file = None
        for file_path in csv_files:
            if os.path.exists(file_path):
                csv_file = file_path
                break
        
        if not csv_file:
            return jsonify({'error': 'No CSV data file found. Please ensure data files exist in the data/ directory.'}), 404
        
        # Read CSV
        df = pd.read_csv(csv_file)
        
        imported_count = 0
        skipped_count = 0
        
        for _, row in df.iterrows():
            # Check if application already exists (by email)
            if Application.query.filter_by(email=row.get('email', '')).first():
                skipped_count += 1
                continue
            
            # Map CSV columns to Application model
            company_name = row.get('company_name', f"Company {row.get('application_id', 'Unknown')}")
            email = row.get('email', f"contact{imported_count}@example.com")
            
            if not company_name or not email:
                skipped_count += 1
                continue
            
            # Determine status based on is_fraud and security controls
            is_fraud = row.get('is_fraud', 0)
            security_count = sum([
                row.get('mfaEnabled', 0), row.get('ssoSupport', 0),
                row.get('encryptionAtRest', 0), row.get('encryptionInTransit', 0),
                row.get('firewallEnabled', 0), row.get('gdprCompliant', 0)
            ])
            
            if is_fraud == 1:
                status = 'flagged'
                fraud_score = 0.8
                risk_score = 30
            elif is_fraud == 0 and security_count >= 4:
                # Auto-approve legitimate applications with good security
                status = 'approved'
                fraud_score = 0.05
                risk_score = 90
            else:
                status = 'pending_review'
                fraud_score = 0.1
                risk_score = 75
            
            # Create application
            app = Application(
                type=row.get('type', 'vendor').lower(),
                company_name=company_name,
                email=email,
                phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                address=row.get('address', '') if pd.notna(row.get('address')) else None,
                city=row.get('city', '') if pd.notna(row.get('city')) else None,
                state=row.get('state', '') if pd.notna(row.get('state')) else None,
                zip=row.get('zip', '') if pd.notna(row.get('zip')) else None,
                tax_id=str(row.get('tax_id', '')) if pd.notna(row.get('tax_id')) else None,
                industry=row.get('industry', '') if pd.notna(row.get('industry')) else None,
                status=status,
                risk_score=risk_score,
                fraud_score=fraud_score,
                submitted_date=datetime.utcnow()
            )
            
            # Store fraud detection result
            fraud_result = {
                'is_fraud': bool(is_fraud == 1),
                'fraud_score': float(fraud_score),
                'risk_level': 'high' if is_fraud == 1 else 'low',
                'model_type': 'kaggle_import'
            }
            app.fraud_detection_result = json.dumps(fraud_result)
            
            db.session.add(app)
            db.session.flush()
            
            # Save security controls
            security_controls = {
                'Identity & Access Management': ['mfaEnabled', 'ssoSupport', 'rbacImplemented'],
                'Data Encryption': ['encryptionAtRest', 'encryptionInTransit', 'keyManagement'],
                'Network Security': ['firewallEnabled', 'vpnRequired', 'ipWhitelisting'],
                'Logging & Monitoring': ['auditLogging', 'siemIntegration', 'alertingEnabled'],
                'Compliance': ['gdprCompliant', 'soc2Certified', 'isoCompliant']
            }
            
            for category, controls in security_controls.items():
                for control in controls:
                    value = row.get(control, False)
                    if pd.notna(value):
                        ctrl = SecurityControl(
                            application_id=app.id,
                            category=category,
                            control_name=control,
                            status=bool(value) if isinstance(value, (int, float)) else False
                        )
                        db.session.add(ctrl)
            
            # Detect and save PII
            data_dict = row.to_dict()
            pii_detected = detect_pii(data_dict)
            for pii in pii_detected:
                pii_record = PIIData(
                    application_id=app.id,
                    field_name=pii['field'],
                    pii_type=pii['type'],
                    masked_value=mask_pii(pii['value'], pii['type'])
                )
                db.session.add(pii_record)
            
            imported_count += 1
            
            # Commit in batches of 50
            if imported_count % 50 == 0:
                db.session.commit()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Data imported successfully',
            'imported': imported_count,
            'skipped': skipped_count,
            'total': len(df)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error importing data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to import data: {str(e)}'}), 500


# ============== INITIALIZE DATABASE ==============

def create_tables():
    """Create database tables and default admin user"""
    try:
        with app.app_context():
            db.create_all()
            
            # Create default admin user if not exists
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@onboarding.com',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ Created default admin user (username: admin, password: admin123)")
    except Exception as e:
        print(f"⚠️ Error initializing database: {e}")
        print("   The app will continue, but database features may not work.")


# Initialize database on startup
try:
    with app.app_context():
        create_tables()
except Exception as e:
    print(f"⚠️ Could not initialize database on startup: {e}")
    print("   Database will be initialized on first request.")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))  # Changed to 5001 to avoid conflict with AirPlay
    app.run(host='0.0.0.0', port=port, debug=app.config.get('FLASK_DEBUG', False))
