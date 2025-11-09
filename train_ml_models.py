"""
Train ML Models for Fraud Detection

Uses the generated synthetic data or your own dataset
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pickle
import os
from pathlib import Path

def load_data(filepath=None):
    """Load training data"""
    # Try multiple possible file paths
    possible_paths = [
        filepath,
        'data/onboarding_train.csv',
        'data/onboarding_training_data.csv',
        'onboarding_train.csv',
        'data/supplier_quality_data.csv',
        'data/processed/supplier_quality_processed.csv'
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            print(f"📂 Loading data from {path}...")
            df = pd.read_csv(path)
            print(f"✅ Loaded {len(df)} records")
            return df
    
    raise FileNotFoundError("Could not find training data. Please ensure one of these files exists:\n" +
                          "  - onboarding_train.csv\n" +
                          "  - data/supplier_quality_data.csv\n" +
                          "  - data/processed/supplier_quality_processed.csv")

def prepare_features(df):
    """Extract features for ML model"""
    print("🔧 Preparing features...")
    
    features = {}
    
    # Email features
    if 'email' in df.columns:
        features['email_length'] = df['email'].str.len()
        features['has_corporate_email'] = ~df['email'].str.contains('gmail|yahoo|hotmail', case=False, na=False)
        features['email_digits'] = df['email'].str.count(r'\d')
    else:
        features['email_length'] = 0
        features['has_corporate_email'] = 0
        features['email_digits'] = 0
    
    # Phone features
    if 'phone' in df.columns:
        features['phone_provided'] = (df['phone'] != '').astype(int)
        features['phone_valid_format'] = df['phone'].str.match(r'[\d\-\+\(\)\s]+', na=False).astype(int)
    else:
        features['phone_provided'] = 0
        features['phone_valid_format'] = 0
    
    # Address features
    if all(col in df.columns for col in ['address', 'city', 'state', 'zip']):
        features['address_complete'] = (
            (df['address'] != '') & 
            (df['city'] != '') & 
            (df['state'] != '') & 
            (df['zip'] != '')
        ).astype(int)
    else:
        features['address_complete'] = 0
    
    # Tax ID
    if 'tax_id' in df.columns:
        features['tax_id_provided'] = (df['tax_id'] != '').astype(int)
    else:
        features['tax_id_provided'] = 0
    
    # Company name features
    if 'company_name' in df.columns:
        features['company_name_length'] = df['company_name'].str.len()
        features['company_name_has_llc'] = df['company_name'].str.contains(
            'LLC|Inc|Corp|Ltd', case=False, na=False
        ).astype(int)
    else:
        features['company_name_length'] = 0
        features['company_name_has_llc'] = 0
    
    # Industry risk
    if 'industry' in df.columns:
        high_risk_industries = ['Cryptocurrency', 'Gambling', 'Cannabis']
        features['high_risk_industry'] = df['industry'].isin(high_risk_industries).astype(int)
    else:
        features['high_risk_industry'] = 0
    
    # Security controls
    security_cols = [
        'mfaEnabled', 'ssoSupport', 'rbacImplemented',
        'encryptionAtRest', 'encryptionInTransit', 'keyManagement',
        'firewallEnabled', 'vpnRequired', 'ipWhitelisting',
        'auditLogging', 'siemIntegration', 'alertingEnabled',
        'gdprCompliant', 'soc2Certified', 'isoCompliant'
    ]
    
    available_security_cols = [col for col in security_cols if col in df.columns]
    if available_security_cols:
        features['security_controls_count'] = df[available_security_cols].sum(axis=1)
        # Add individual security features
        for col in available_security_cols:
            features[f'security_{col}'] = df[col].astype(int)
    else:
        features['security_controls_count'] = 0
    
    # Type encoding
    if 'type' in df.columns:
        features['is_vendor'] = (df['type'].str.lower() == 'vendor').astype(int)
        features['is_supplier'] = (df['type'].str.lower() == 'supplier').astype(int)
        features['is_contractor'] = (df['type'].str.lower() == 'contractor').astype(int)
    else:
        features['is_vendor'] = 0
        features['is_supplier'] = 0
        features['is_contractor'] = 0
    
    # Description features (if available)
    if 'description' in df.columns:
        features['description_length'] = df['description'].str.len()
        features['description_provided'] = (df['description'] != '').astype(int)
    else:
        features['description_length'] = 0
        features['description_provided'] = 0
    
    # Convert to DataFrame
    X = pd.DataFrame(features)
    
    # Get target variable
    if 'is_fraud' in df.columns:
        y = df['is_fraud']
    elif 'Class' in df.columns:
        y = df['Class']
    else:
        raise ValueError("No target variable found. Expected 'is_fraud' or 'Class' column.")
    
    print(f"✅ Created {len(X.columns)} features")
    print(f"   Features: {', '.join(X.columns.tolist()[:10])}...")
    
    return X, y, list(X.columns)

def train_random_forest(X_train, X_test, y_train, y_test):
    """Train Random Forest classifier"""
    print("\n🌲 Training Random Forest Classifier...")
    
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    
    # Evaluate
    train_score = rf_model.score(X_train, y_train)
    test_score = rf_model.score(X_test, y_test)
    
    print(f"✅ Training Accuracy: {train_score:.4f}")
    print(f"✅ Test Accuracy: {test_score:.4f}")
    
    # Predictions
    y_pred = rf_model.predict(X_test)
    y_pred_proba = rf_model.predict_proba(X_test)[:, 1]
    
    # Metrics
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud']))
    
    print("\n📊 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print(f"   True Negatives: {cm[0][0]}, False Positives: {cm[0][1]}")
    print(f"   False Negatives: {cm[1][0]}, True Positives: {cm[1][1]}")
    
    try:
        auc = roc_auc_score(y_test, y_pred_proba)
        print(f"\n📊 AUC-ROC Score: {auc:.4f}")
    except Exception as e:
        print(f"\n⚠️ Could not calculate AUC-ROC: {e}")
    
    # Feature importance
    print("\n🎯 Top 10 Most Important Features:")
    feature_importance = pd.DataFrame({
        'feature': [f'feature_{i}' for i in range(len(rf_model.feature_importances_))],
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Map back to actual feature names if available
    if hasattr(X_train, 'columns'):
        feature_importance['feature'] = X_train.columns
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    return rf_model

def train_isolation_forest(X_train, contamination=0.2):
    """Train Isolation Forest for anomaly detection"""
    print("\n🌳 Training Isolation Forest (Anomaly Detection)...")
    
    # Calculate contamination from data if y_train is available
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    
    iso_forest.fit(X_train)
    
    # Get anomaly scores
    anomaly_scores = iso_forest.score_samples(X_train)
    print(f"✅ Isolation Forest trained")
    print(f"   Mean anomaly score: {anomaly_scores.mean():.4f}")
    print(f"   Std anomaly score: {anomaly_scores.std():.4f}")
    
    return iso_forest

def save_models(rf_model, iso_forest, scaler, feature_names):
    """Save trained models"""
    print("\n💾 Saving models...")
    
    os.makedirs('models', exist_ok=True)
    os.makedirs('backend/models', exist_ok=True)
    
    model_data = {
        'rf_model': rf_model,
        'isolation_forest': iso_forest,
        'scaler': scaler,
        'feature_names': feature_names
    }
    
    # Save to both locations
    with open('models/fraud_detection_models.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    with open('backend/models/fraud_detection_models.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("✅ Models saved to:")
    print("   - models/fraud_detection_models.pkl")
    print("   - backend/models/fraud_detection_models.pkl")

def test_prediction_example(rf_model, scaler, feature_names):
    """Test prediction with example data"""
    print("\n🧪 Testing prediction with example...")
    
    # Create feature vector matching our feature set
    # Example: Suspicious application
    example_suspicious = {}
    for feat in feature_names:
        if 'security' in feat:
            example_suspicious[feat] = 0
        elif 'email' in feat:
            example_suspicious[feat] = 15 if 'length' in feat else 0
        elif 'phone' in feat:
            example_suspicious[feat] = 0
        elif 'address' in feat:
            example_suspicious[feat] = 0
        elif 'security_controls_count' in feat:
            example_suspicious[feat] = 2
        elif 'high_risk' in feat:
            example_suspicious[feat] = 1
        else:
            example_suspicious[feat] = 0
    
    # Example: Legitimate application
    example_legitimate = {}
    for feat in feature_names:
        if 'security' in feat and 'count' not in feat:
            example_legitimate[feat] = 1
        elif 'security_controls_count' in feat:
            example_legitimate[feat] = 12
        elif 'email' in feat:
            example_legitimate[feat] = 25 if 'length' in feat else 1
        elif 'phone' in feat or 'address' in feat or 'tax_id' in feat:
            example_legitimate[feat] = 1
        elif 'high_risk' in feat:
            example_legitimate[feat] = 0
        else:
            example_legitimate[feat] = 1
    
    for name, example in [('Suspicious', example_suspicious), ('Legitimate', example_legitimate)]:
        try:
            # Ensure all features are present
            X_example = pd.DataFrame([example])
            # Reorder columns to match feature_names
            X_example = X_example.reindex(columns=feature_names, fill_value=0)
            X_example_scaled = scaler.transform(X_example)
            
            prediction = rf_model.predict(X_example_scaled)[0]
            probability = rf_model.predict_proba(X_example_scaled)[0]
            
            print(f"\n{name} Application:")
            print(f"  Prediction: {'FRAUD' if prediction == 1 else 'LEGITIMATE'}")
            print(f"  Fraud Probability: {probability[1]:.2%}")
            print(f"  Legitimate Probability: {probability[0]:.2%}")
        except Exception as e:
            print(f"\n⚠️ Could not test {name} example: {e}")

def main():
    """Main training pipeline"""
    print("=" * 60)
    print("🤖 ML Model Training Pipeline")
    print("=" * 60)
    
    # 1. Load data
    try:
        df = load_data()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: Run 'python3 generate_supplier_data.py' to create training data")
        return
    
    # 2. Prepare features
    try:
        X, y, feature_names = prepare_features(df)
    except Exception as e:
        print(f"\n❌ Error preparing features: {e}")
        return
    
    # 3. Split data
    print("\n📊 Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✅ Train set: {len(X_train)} samples ({y_train.sum()} fraud cases)")
    print(f"✅ Test set: {len(X_test)} samples ({y_test.sum()} fraud cases)")
    
    # 4. Scale features
    print("\n⚖️ Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("✅ Features scaled")
    
    # 5. Train Random Forest
    rf_model = train_random_forest(X_train_scaled, X_test_scaled, y_train, y_test)
    
    # 6. Train Isolation Forest
    contamination = y_train.mean() if hasattr(y_train, 'mean') else 0.2
    iso_forest = train_isolation_forest(X_train_scaled, contamination=contamination)
    
    # 7. Save models
    save_models(rf_model, iso_forest, scaler, feature_names)
    
    # 8. Test predictions
    test_prediction_example(rf_model, scaler, feature_names)
    
    print("\n" + "=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review model performance metrics above")
    print("2. Use the saved model in your Flask API")
    print("3. Update backend/ml_fraud_detection.py to load the model")
    print("\nModel file location: models/fraud_detection_models.pkl")

if __name__ == '__main__':
    main()
