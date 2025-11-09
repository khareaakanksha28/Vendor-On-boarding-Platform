"""
Enhanced Fraud Detection Model
Uses trained Random Forest model if available, falls back to Isolation Forest
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os
from pathlib import Path

class EnhancedFraudDetectionModel:
    """Enhanced ML-based fraud detection with Random Forest support"""
    
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.lgb_model = None
        self.best_model = None
        self.best_model_name = None
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.model_type = 'isolation_forest'  # or 'random_forest', 'xgboost', 'lightgbm'
        self.is_trained = False
        
        # Model paths
        self.models_path = Path(__file__).parent.parent / 'models' / 'fraud_detection_models.pkl'
        self.backend_models_path = Path(__file__).parent / 'models' / 'fraud_detection_models.pkl'
        self.legacy_model_path = Path(__file__).parent / 'fraud_model.pkl'
        self.legacy_scaler_path = Path(__file__).parent / 'fraud_scaler.pkl'
        
        self._load_model()
    
    def _load_model(self):
        """Load trained model if exists - supports multiple model types"""
        # Try to load new models (may include XGBoost, LightGBM, etc.)
        for model_path in [self.models_path, self.backend_models_path]:
            if model_path.exists():
                try:
                    print(f"Loading trained models from {model_path}...")
                    with open(model_path, 'rb') as f:
                        model_data = pickle.load(f)
                    
                    # Load best model if available
                    self.best_model = model_data.get('best_model')
                    self.best_model_name = model_data.get('best_model_name', 'random_forest')
                    
                    # Load individual models
                    self.rf_model = model_data.get('rf_model')
                    self.xgb_model = model_data.get('xgb_model')
                    self.lgb_model = model_data.get('lgb_model')
                    self.isolation_forest = model_data.get('isolation_forest')
                    self.scaler = model_data.get('scaler', self.scaler)
                    self.feature_names = model_data.get('feature_names')
                    
                    # Use best model if available, otherwise fall back to RF
                    if self.best_model is not None:
                        self.model_type = self.best_model_name
                        self.is_trained = True
                        print(f"✓ Loaded best model: {self.best_model_name}")
                        return
                    elif self.rf_model is not None:
                        self.model_type = 'random_forest'
                        self.is_trained = True
                        print("✓ Loaded Random Forest model")
                        return
                    elif self.xgb_model is not None:
                        self.model_type = 'xgboost'
                        self.is_trained = True
                        print("✓ Loaded XGBoost model")
                        return
                    elif self.lgb_model is not None:
                        self.model_type = 'lightgbm'
                        self.is_trained = True
                        print("✓ Loaded LightGBM model")
                        return
                    elif self.isolation_forest is not None:
                        self.model_type = 'isolation_forest'
                        self.is_trained = True
                        print("✓ Loaded Isolation Forest model")
                        return
                except Exception as e:
                    print(f"Error loading model from {model_path}: {e}")
        
        # Try to load legacy model
        if self.legacy_model_path.exists() and self.legacy_scaler_path.exists():
            try:
                with open(self.legacy_model_path, 'rb') as f:
                    self.isolation_forest = pickle.load(f)
                with open(self.legacy_scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.model_type = 'isolation_forest'
                self.is_trained = True
                print("✓ Loaded legacy Isolation Forest model")
                return
            except Exception as e:
                print(f"Error loading legacy model: {e}")
        
        # Initialize default model
        print("No trained model found, initializing default model...")
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize default Isolation Forest model"""
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        
        # Generate sample training data
        np.random.seed(42)
        n_samples = 1000
        normal_data = np.random.randn(n_samples, 8)
        normal_data[:, 0] = np.abs(normal_data[:, 0]) * 100
        normal_data[:, 1] = np.abs(normal_data[:, 1]) * 5 + 1
        normal_data[:, 2] = np.abs(normal_data[:, 2]) * 10000 + 5000
        normal_data[:, 3] = np.abs(normal_data[:, 3]) * 10
        normal_data[:, 4] = np.abs(normal_data[:, 4]) * 5
        normal_data[:, 5] = np.abs(normal_data[:, 5]) * 24
        normal_data[:, 6] = np.abs(normal_data[:, 6]) * 10
        normal_data[:, 7] = np.abs(normal_data[:, 7]) * 100
        
        X_scaled = self.scaler.fit_transform(normal_data)
        self.isolation_forest.fit(X_scaled)
        self.is_trained = True
        self.model_type = 'isolation_forest'
    
    def extract_features_for_rf(self, user_data):
        """Extract features in the format expected by Random Forest model"""
        if self.feature_names is None:
            return None
        
        features = {}
        
        # Email features
        email = str(user_data.get('email', ''))
        features['email_length'] = len(email)
        features['has_corporate_email'] = 1 if not any(x in email.lower() for x in ['gmail', 'yahoo', 'hotmail']) else 0
        features['email_digits'] = sum(c.isdigit() for c in email)
        
        # Phone features
        phone = str(user_data.get('phone', ''))
        features['phone_provided'] = 1 if phone else 0
        features['phone_valid_format'] = 1 if phone and any(c.isdigit() for c in phone) else 0
        
        # Address features
        features['address_complete'] = 1 if all(user_data.get(k) for k in ['address', 'city', 'state', 'zip']) else 0
        
        # Tax ID
        features['tax_id_provided'] = 1 if user_data.get('tax_id') else 0
        
        # Company name
        company_name = str(user_data.get('company_name', ''))
        features['company_name_length'] = len(company_name)
        features['company_name_has_llc'] = 1 if any(x in company_name.upper() for x in ['LLC', 'INC', 'CORP', 'LTD']) else 0
        
        # Industry
        industry = str(user_data.get('industry', ''))
        high_risk = ['Cryptocurrency', 'Gambling', 'Cannabis']
        features['high_risk_industry'] = 1 if industry in high_risk else 0
        
        # Security controls
        security_cols = [
            'mfaEnabled', 'ssoSupport', 'rbacImplemented',
            'encryptionAtRest', 'encryptionInTransit', 'keyManagement',
            'firewallEnabled', 'vpnRequired', 'ipWhitelisting',
            'auditLogging', 'siemIntegration', 'alertingEnabled',
            'gdprCompliant', 'soc2Certified', 'isoCompliant'
        ]
        
        security_count = sum(1 for col in security_cols if user_data.get(col, 0))
        features['security_controls_count'] = security_count
        
        # Add individual security features
        for col in security_cols:
            features[f'security_{col}'] = 1 if user_data.get(col, 0) else 0
        
        # Type
        app_type = str(user_data.get('type', '')).lower()
        features['is_vendor'] = 1 if app_type == 'vendor' else 0
        features['is_supplier'] = 1 if app_type == 'supplier' else 0
        features['is_contractor'] = 1 if app_type == 'contractor' else 0
        
        # Description
        description = str(user_data.get('description', ''))
        features['description_length'] = len(description)
        features['description_provided'] = 1 if description else 0
        
        # Create DataFrame with correct column order
        feature_df = pd.DataFrame([features])
        # Reorder to match feature_names
        if self.feature_names:
            feature_df = feature_df.reindex(columns=self.feature_names, fill_value=0)
        
        return feature_df.values
    
    def extract_features_legacy(self, user_data):
        """Extract features for legacy Isolation Forest model"""
        return np.array([[
            user_data.get('age', 30),
            user_data.get('account_age_years', 0),
            user_data.get('annual_income', 50000),
            user_data.get('credit_score', 650),
            user_data.get('num_devices', 1),
            user_data.get('hours_since_registration', 0),
            user_data.get('failed_login_attempts', 0),
            user_data.get('transaction_amount', 0)
        ]])
    
    def predict(self, user_data):
        """Predict if user data indicates fraud - supports multiple model types"""
        if not self.is_trained:
            self._initialize_model()
        
        # Try best model first
        if self.best_model is not None:
            try:
                X = self.extract_features_for_rf(user_data)
                if X is not None:
                    if isinstance(X, np.ndarray):
                        if self.feature_names:
                            X_df = pd.DataFrame(X, columns=self.feature_names)
                        else:
                            X_df = pd.DataFrame(X)
                    else:
                        X_df = X
                    
                    X_scaled = self.scaler.transform(X_df)
                    prediction = self.best_model.predict(X_scaled)[0]
                    probability = self.best_model.predict_proba(X_scaled)[0]
                    
                    fraud_score = float(probability[1])
                    is_fraud = bool(prediction == 1)
                    
                    if fraud_score < 0.3:
                        risk_level = 'low'
                    elif fraud_score < 0.7:
                        risk_level = 'medium'
                    else:
                        risk_level = 'high'
                    
                    return {
                        'is_fraud': is_fraud,
                        'fraud_score': fraud_score,
                        'risk_level': risk_level,
                        'model_type': self.best_model_name,
                        'fraud_probability': fraud_score,
                        'legitimate_probability': float(probability[0])
                    }
            except Exception as e:
                print(f"Error in best model prediction, falling back: {e}")
        
        # Try XGBoost
        if self.model_type == 'xgboost' and self.xgb_model is not None:
            try:
                X = self.extract_features_for_rf(user_data)
                if X is not None:
                    if isinstance(X, np.ndarray):
                        if self.feature_names:
                            X_df = pd.DataFrame(X, columns=self.feature_names)
                        else:
                            X_df = pd.DataFrame(X)
                    else:
                        X_df = X
                    
                    X_scaled = self.scaler.transform(X_df)
                    prediction = self.xgb_model.predict(X_scaled)[0]
                    probability = self.xgb_model.predict_proba(X_scaled)[0]
                    
                    fraud_score = float(probability[1])
                    is_fraud = bool(prediction == 1)
                    
                    if fraud_score < 0.3:
                        risk_level = 'low'
                    elif fraud_score < 0.7:
                        risk_level = 'medium'
                    else:
                        risk_level = 'high'
                    
                    return {
                        'is_fraud': is_fraud,
                        'fraud_score': fraud_score,
                        'risk_level': risk_level,
                        'model_type': 'xgboost',
                        'fraud_probability': fraud_score,
                        'legitimate_probability': float(probability[0])
                    }
            except Exception as e:
                print(f"Error in XGBoost prediction, falling back: {e}")
        
        # Try LightGBM
        if self.model_type == 'lightgbm' and self.lgb_model is not None:
            try:
                X = self.extract_features_for_rf(user_data)
                if X is not None:
                    if isinstance(X, np.ndarray):
                        if self.feature_names:
                            X_df = pd.DataFrame(X, columns=self.feature_names)
                        else:
                            X_df = pd.DataFrame(X)
                    else:
                        X_df = X
                    
                    X_scaled = self.scaler.transform(X_df)
                    prediction = self.lgb_model.predict(X_scaled)[0]
                    probability = self.lgb_model.predict_proba(X_scaled)[0]
                    
                    fraud_score = float(probability[1])
                    is_fraud = bool(prediction == 1)
                    
                    if fraud_score < 0.3:
                        risk_level = 'low'
                    elif fraud_score < 0.7:
                        risk_level = 'medium'
                    else:
                        risk_level = 'high'
                    
                    return {
                        'is_fraud': is_fraud,
                        'fraud_score': fraud_score,
                        'risk_level': risk_level,
                        'model_type': 'lightgbm',
                        'fraud_probability': fraud_score,
                        'legitimate_probability': float(probability[0])
                    }
            except Exception as e:
                print(f"Error in LightGBM prediction, falling back: {e}")
        
        # Try Random Forest
        if self.model_type == 'random_forest' and self.rf_model is not None:
            # Use Random Forest model
            try:
                X = self.extract_features_for_rf(user_data)
                if X is None:
                    raise ValueError("Could not extract features for RF model")
                
                # Convert to DataFrame with feature names for scaler compatibility
                if isinstance(X, np.ndarray):
                    if self.feature_names:
                        X_df = pd.DataFrame(X, columns=self.feature_names)
                    else:
                        X_df = pd.DataFrame(X)
                else:
                    X_df = X
                
                X_scaled = self.scaler.transform(X_df)
                prediction = self.rf_model.predict(X_scaled)[0]
                probability = self.rf_model.predict_proba(X_scaled)[0]
                
                fraud_score = float(probability[1])
                is_fraud = bool(prediction == 1)
                
                # Determine risk level
                if fraud_score < 0.3:
                    risk_level = 'low'
                elif fraud_score < 0.7:
                    risk_level = 'medium'
                else:
                    risk_level = 'high'
                
                return {
                    'is_fraud': is_fraud,
                    'fraud_score': fraud_score,
                    'risk_level': risk_level,
                    'model_type': 'random_forest',
                    'fraud_probability': fraud_score,
                    'legitimate_probability': float(probability[0])
                }
            except Exception as e:
                print(f"Error in RF prediction, falling back to Isolation Forest: {e}")
                # Fall through to Isolation Forest
        
        # Use Isolation Forest (default or fallback)
        features = self.extract_features_legacy(user_data)
        features_scaled = self.scaler.transform(features)
        
        if self.isolation_forest is None:
            self._initialize_model()
            features_scaled = self.scaler.transform(features)
        
        prediction = self.isolation_forest.predict(features_scaled)[0]
        anomaly_score = self.isolation_forest.score_samples(features_scaled)[0]
        
        fraud_score = max(0, min(1, (1 - (anomaly_score + 0.5)) / 2))
        is_fraud = prediction == -1
        
        if fraud_score < 0.3:
            risk_level = 'low'
        elif fraud_score < 0.7:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'is_fraud': bool(is_fraud),
            'fraud_score': float(fraud_score),
            'risk_level': risk_level,
            'anomaly_score': float(anomaly_score),
            'model_type': 'isolation_forest'
        }

# Global model instance
fraud_model = EnhancedFraudDetectionModel()

