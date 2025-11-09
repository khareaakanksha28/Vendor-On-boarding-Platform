"""
Train and Compare Multiple ML Models for Fraud Detection
Compares: Random Forest, XGBoost, LightGBM, SVM, and Isolation Forest
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

# Try to import XGBoost and LightGBM
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except (ImportError, Exception) as e:
    XGBOOST_AVAILABLE = False
    print(f"⚠️ XGBoost not available: {str(e)[:100]}")
    print("   Note: XGBoost requires OpenMP. On macOS, run: brew install libomp")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except (ImportError, Exception) as e:
    LIGHTGBM_AVAILABLE = False
    print(f"⚠️ LightGBM not available: {str(e)[:100]}")
    print("   Note: LightGBM may require additional dependencies")

def load_data(filepath='data/onboarding_train.csv'):
    """Load training data"""
    print(f"📂 Loading data from {filepath}...")
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    df = pd.read_csv(filepath)
    print(f"✅ Loaded {len(df)} records")
    return df

def prepare_features(df):
    """Extract features for ML model"""
    print("🔧 Preparing features...")
    features = {}
    
    # Email features
    features['email_length'] = df['email'].str.len()
    features['has_corporate_email'] = ~df['email'].str.contains('gmail|yahoo|hotmail', na=False, case=False).astype(int)
    features['email_digits'] = df['email'].str.count(r'\d')
    
    # Phone features
    features['phone_provided'] = (df['phone'] != '').astype(int)
    features['phone_valid_format'] = df['phone'].str.match(r'.*\d{3}.*\d{3}.*\d{4}.*', na=False).astype(int)
    
    # Address features
    features['address_complete'] = (
        (df['address'] != '') & (df['city'] != '') & (df['state'] != '') & (df['zip'] != '')
    ).astype(int)
    
    # Tax ID
    features['tax_id_provided'] = (df['tax_id'] != '').astype(int)
    
    # Company name
    features['company_name_length'] = df['company_name'].str.len()
    features['company_name_has_llc'] = df['company_name'].str.contains('LLC|Inc|Corp|Ltd', case=False, na=False).astype(int)
    
    # Industry risk
    high_risk_industries = ['Cryptocurrency', 'Gambling', 'Cannabis']
    features['high_risk_industry'] = df['industry'].isin(high_risk_industries).astype(int)
    
    # Security controls
    security_cols = [
        'mfaEnabled', 'ssoSupport', 'rbacImplemented',
        'encryptionAtRest', 'encryptionInTransit', 'keyManagement',
        'firewallEnabled', 'vpnRequired', 'ipWhitelisting',
        'auditLogging', 'siemIntegration', 'alertingEnabled',
        'gdprCompliant', 'soc2Certified', 'isoCompliant'
    ]
    features['security_controls_count'] = df[security_cols].sum(axis=1)
    
    # Type encoding
    features['is_vendor'] = (df['type'] == 'vendor').astype(int)
    features['is_supplier'] = (df['type'] == 'supplier').astype(int)
    features['is_contractor'] = (df['type'] == 'contractor').astype(int)
    
    # Description
    features['description_length'] = df['description'].str.len() if 'description' in df.columns else pd.Series([0] * len(df))
    features['description_provided'] = (df['description'] != '').astype(int) if 'description' in df.columns else pd.Series([0] * len(df))
    
    # Convert to DataFrame
    X = pd.DataFrame(features)
    y = df['is_fraud'] if 'is_fraud' in df.columns else pd.Series([0] * len(df))
    
    print(f"✅ Created {len(X.columns)} features")
    return X, y, list(X.columns)

def train_and_evaluate_model(model, name, X_train, X_test, y_train, y_test):
    """Train and evaluate a model"""
    print(f"\n{'='*60}")
    print(f"🤖 Training {name}...")
    print(f"{'='*60}")
    
    # Train
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print(f"\n📊 {name} Performance:")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision:  {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    
    if y_pred_proba is not None:
        try:
            auc = roc_auc_score(y_test, y_pred_proba)
            print(f"  AUC-ROC:   {auc:.4f}")
        except:
            pass
    
    # Cross-validation
    try:
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        print(f"  CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    except:
        pass
    
    print(f"\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud'], zero_division=0))
    
    return {
        'model': model,
        'name': name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba
    }

def main():
    """Main training and comparison pipeline"""
    print("=" * 60)
    print("🔬 ML Model Comparison for Fraud Detection")
    print("=" * 60)
    
    # 1. Load data
    df = load_data('data/onboarding_train.csv')
    if df is None:
        print("❌ Cannot proceed without data")
        return
    
    # 2. Prepare features
    X, y, feature_names = prepare_features(df)
    
    # 3. Split data
    print("\n📊 Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✅ Train set: {len(X_train)} samples")
    print(f"✅ Test set: {len(X_test)} samples")
    
    # 4. Scale features
    print("\n⚖️ Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("✅ Features scaled")
    
    # 5. Train and compare models
    results = []
    
    # Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_result = train_and_evaluate_model(rf_model, "Random Forest", X_train_scaled, X_test_scaled, y_train, y_test)
    results.append(rf_result)
    
    # XGBoost
    if XGBOOST_AVAILABLE:
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss'
        )
        xgb_result = train_and_evaluate_model(xgb_model, "XGBoost", X_train_scaled, X_test_scaled, y_train, y_test)
        results.append(xgb_result)
    
    # LightGBM
    if LIGHTGBM_AVAILABLE:
        lgb_model = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        lgb_result = train_and_evaluate_model(lgb_model, "LightGBM", X_train_scaled, X_test_scaled, y_train, y_test)
        results.append(lgb_result)
    
    # SVM (for comparison, but slower)
    print("\n⚠️ Training SVM (this may take a while)...")
    svm_model = SVC(
        kernel='rbf',
        probability=True,
        random_state=42,
        C=1.0,
        gamma='scale'
    )
    svm_result = train_and_evaluate_model(svm_model, "SVM (RBF)", X_train_scaled, X_test_scaled, y_train, y_test)
    results.append(svm_result)
    
    # Isolation Forest (for anomaly detection)
    iso_forest = IsolationForest(
        contamination=0.15,
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_train_scaled)
    iso_predictions = iso_forest.predict(X_test_scaled)
    iso_predictions_binary = (iso_predictions == -1).astype(int)
    
    iso_accuracy = accuracy_score(y_test, iso_predictions_binary)
    iso_precision = precision_score(y_test, iso_predictions_binary, zero_division=0)
    iso_recall = recall_score(y_test, iso_predictions_binary, zero_division=0)
    iso_f1 = f1_score(y_test, iso_predictions_binary, zero_division=0)
    
    print(f"\n📊 Isolation Forest Performance:")
    print(f"  Accuracy:  {iso_accuracy:.4f}")
    print(f"  Precision:  {iso_precision:.4f}")
    print(f"  Recall:    {iso_recall:.4f}")
    print(f"  F1-Score:  {iso_f1:.4f}")
    
    results.append({
        'model': iso_forest,
        'name': 'Isolation Forest',
        'accuracy': iso_accuracy,
        'precision': iso_precision,
        'recall': iso_recall,
        'f1': iso_f1
    })
    
    # 6. Compare results
    print("\n" + "=" * 60)
    print("🏆 MODEL COMPARISON RESULTS")
    print("=" * 60)
    print(f"{'Model':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 60)
    
    for result in sorted(results, key=lambda x: x['f1'], reverse=True):
        print(f"{result['name']:<20} {result['accuracy']:<12.4f} {result['precision']:<12.4f} {result['recall']:<12.4f} {result['f1']:<12.4f}")
    
    # 7. Select best model (by F1 score)
    best_model_result = max(results, key=lambda x: x['f1'])
    print(f"\n✅ Best Model: {best_model_result['name']} (F1: {best_model_result['f1']:.4f})")
    
    # 8. Save best model
    print("\n💾 Saving models...")
    os.makedirs('models', exist_ok=True)
    
    model_data = {
        'rf_model': rf_model,
        'isolation_forest': iso_forest,
        'scaler': scaler,
        'feature_names': feature_names,
        'best_model': best_model_result['model'],
        'best_model_name': best_model_result['name'],
        'model_comparison': {r['name']: {'accuracy': r['accuracy'], 'f1': r['f1']} for r in results}
    }
    
    # Add other models if available
    if XGBOOST_AVAILABLE:
        model_data['xgb_model'] = xgb_model
    if LIGHTGBM_AVAILABLE:
        model_data['lgb_model'] = lgb_model
    
    with open('models/fraud_detection_models.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("✅ Models saved to models/fraud_detection_models.pkl")
    print(f"✅ Best model: {best_model_result['name']}")
    
    print("\n" + "=" * 60)
    print("✅ Model Training and Comparison Complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()

