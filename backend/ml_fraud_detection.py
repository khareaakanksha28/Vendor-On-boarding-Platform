import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os

class FraudDetectionModel:
    """ML-based fraud detection for onboarding applications"""
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,  # Expect 10% fraud
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = 'fraud_model.pkl'
        self.scaler_path = 'fraud_scaler.pkl'
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model if exists"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                self.is_trained = True
            except Exception as e:
                print(f"Error loading model: {e}")
                self._initialize_model()
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize model with sample training data"""
        # Generate sample training data for initial model
        np.random.seed(42)
        n_samples = 1000
        
        # Normal user patterns
        normal_data = np.random.randn(n_samples, 8)
        normal_data[:, 0] = np.abs(normal_data[:, 0]) * 100  # Age: 0-100
        normal_data[:, 1] = np.abs(normal_data[:, 1]) * 5 + 1  # Account age: 1-6 years
        normal_data[:, 2] = np.abs(normal_data[:, 2]) * 10000 + 5000  # Income: 5k-15k
        normal_data[:, 3] = np.abs(normal_data[:, 3]) * 10  # Credit score: 0-10
        normal_data[:, 4] = np.abs(normal_data[:, 4]) * 5  # Number of devices: 0-5
        normal_data[:, 5] = np.abs(normal_data[:, 5]) * 24  # Hours since registration: 0-24
        normal_data[:, 6] = np.abs(normal_data[:, 6]) * 10  # Failed login attempts: 0-10
        normal_data[:, 7] = np.abs(normal_data[:, 7]) * 100  # Transaction amount: 0-100
        
        # Train model
        X_scaled = self.scaler.fit_transform(normal_data)
        self.model.fit(X_scaled)
        self.is_trained = True
        self._save_model()
    
    def _save_model(self):
        """Save trained model"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def extract_features(self, user_data):
        """Extract features from user data for fraud detection"""
        features = np.array([[
            user_data.get('age', 30),
            user_data.get('account_age_years', 0),
            user_data.get('annual_income', 50000),
            user_data.get('credit_score', 650),
            user_data.get('num_devices', 1),
            user_data.get('hours_since_registration', 0),
            user_data.get('failed_login_attempts', 0),
            user_data.get('transaction_amount', 0)
        ]])
        return features
    
    def predict(self, user_data):
        """Predict if user data indicates fraud
        
        Returns:
            dict: {
                'is_fraud': bool,
                'fraud_score': float (0-1, higher = more suspicious),
                'risk_level': str ('low', 'medium', 'high')
            }
        """
        if not self.is_trained:
            self._initialize_model()
        
        features = self.extract_features(user_data)
        features_scaled = self.scaler.transform(features)
        
        # Predict anomaly (1 = normal, -1 = anomaly)
        prediction = self.model.predict(features_scaled)[0]
        
        # Get anomaly score (lower = more anomalous)
        anomaly_score = self.model.score_samples(features_scaled)[0]
        
        # Convert to fraud score (0-1, higher = more suspicious)
        # Normalize anomaly score to 0-1 range
        fraud_score = max(0, min(1, (1 - (anomaly_score + 0.5)) / 2))
        
        is_fraud = prediction == -1
        
        # Determine risk level
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
            'anomaly_score': float(anomaly_score)
        }
    
    def retrain(self, training_data):
        """Retrain model with new data"""
        if not training_data or len(training_data) < 10:
            return False
        
        try:
            features_list = [self.extract_features(data) for data in training_data]
            X = np.vstack(features_list)
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            self.is_trained = True
            self._save_model()
            return True
        except Exception as e:
            print(f"Error retraining model: {e}")
            return False
    
    def train_from_kaggle_data(self, data_path, dataset_type='creditcard'):
        """Train model using Kaggle dataset
        
        Args:
            data_path: Path to the processed CSV file
            dataset_type: Type of dataset ('creditcard' or 'supplier')
        """
        try:
            print(f"Loading dataset from {data_path}...")
            df = pd.read_csv(data_path)
            
            if dataset_type == 'creditcard':
                # Use V1-V28 features and Amount, Time
                feature_cols = [col for col in df.columns if col.startswith('V') or col in ['Time', 'Amount']]
                if not feature_cols:
                    print("Error: No valid feature columns found")
                    return False
                
                X = df[feature_cols].values
                # Sample a subset for training (Isolation Forest works better with normal data)
                # Use only non-fraud cases for training
                if 'Class' in df.columns:
                    normal_data = df[df['Class'] == 0]
                    if len(normal_data) > 10000:
                        normal_data = normal_data.sample(n=10000, random_state=42)
                    X = normal_data[feature_cols].values
                
            elif dataset_type == 'supplier':
                # Extract security features from supplier dataset
                bool_cols = ['mfaEnabled', 'ssoSupport', 'rbacImplemented', 'encryptionAtRest',
                            'encryptionInTransit', 'keyManagement', 'firewallEnabled', 'vpnRequired',
                            'ipWhitelisting', 'auditLogging', 'siemIntegration', 'alertingEnabled',
                            'gdprCompliant', 'soc2Certified', 'isoCompliant']
                
                available_cols = [col for col in bool_cols if col in df.columns]
                if not available_cols:
                    print("Error: No security feature columns found")
                    return False
                
                # Convert boolean to numeric
                X = df[available_cols].astype(int).values
                
                # Use non-fraud cases for training
                if 'is_fraud' in df.columns:
                    normal_data = df[df['is_fraud'] == 0]
                    if len(normal_data) > 0:
                        X = normal_data[available_cols].astype(int).values
            else:
                print(f"Unknown dataset type: {dataset_type}")
                return False
            
            if len(X) < 10:
                print(f"Error: Not enough data for training ({len(X)} samples)")
                return False
            
            print(f"Training with {len(X)} samples, {X.shape[1]} features...")
            
            # Scale and train
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            self.is_trained = True
            self._save_model()
            
            print("✓ Model trained and saved successfully")
            return True
            
        except Exception as e:
            print(f"Error training from Kaggle data: {e}")
            import traceback
            traceback.print_exc()
            return False

# Global model instance
fraud_model = FraudDetectionModel()

