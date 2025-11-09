#!/usr/bin/env python3
"""
Process Kaggle datasets for fraud detection training
"""
import pandas as pd
import numpy as np
import os
import zipfile
from pathlib import Path

DATA_DIR = Path('data')
PROCESSED_DIR = Path('data/processed')

def unzip_file(zip_path, extract_to):
    """Unzip a file to a directory"""
    if os.path.exists(zip_path):
        print(f"Unzipping {zip_path} to {extract_to}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✓ Extracted to {extract_to}")
    else:
        print(f"⚠ File not found: {zip_path}")

def process_creditcard_fraud():
    """Process credit card fraud dataset"""
    print("\n" + "="*50)
    print("Processing Credit Card Fraud Dataset")
    print("="*50)
    
    csv_path = DATA_DIR / 'creditcard.csv'
    
    if not csv_path.exists():
        print(f"⚠ Credit card dataset not found at {csv_path}")
        return None
    
    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()[:10]}...")
    print(f"Fraud cases: {df['Class'].sum()} ({df['Class'].sum() / len(df) * 100:.2f}%)")
    
    # Save processed version
    processed_path = PROCESSED_DIR / 'creditcard_processed.csv'
    df.to_csv(processed_path, index=False)
    print(f"✓ Saved processed data to {processed_path}")
    
    return df

def process_supplier_quality():
    """Process supplier quality dataset"""
    print("\n" + "="*50)
    print("Processing Supplier Quality Dataset")
    print("="*50)
    
    # Look for CSV files in data directory
    csv_files = list(DATA_DIR.glob('*.csv'))
    
    # Priority order: generated file, then any supplier file
    supplier_file = None
    if (DATA_DIR / 'supplier_quality_data.csv').exists():
        supplier_file = DATA_DIR / 'supplier_quality_data.csv'
    else:
        supplier_files = [f for f in csv_files if 'supplier' in f.name.lower() or 'quality' in f.name.lower()]
        if supplier_files:
            supplier_file = supplier_files[0]
        else:
            # Look for any CSV that's not creditcard
            other_csvs = [f for f in csv_files if f.name != 'creditcard.csv']
            if other_csvs:
                supplier_file = other_csvs[0]
    
    if not supplier_file or not supplier_file.exists():
        print("⚠ No supplier quality dataset found")
        print("  You can generate one by running: python3 generate_supplier_data.py")
        return None
    
    print(f"Loading {supplier_file}...")
    
    try:
        df = pd.read_csv(supplier_file)
        print(f"Dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)[:10]}...")
        
        # Check if is_fraud column exists, if not create it
        if 'is_fraud' not in df.columns:
            print("⚠ 'is_fraud' column not found. Creating based on available data...")
            # You can add logic here to determine fraud based on other columns
            df['is_fraud'] = 0  # Default to no fraud
        
        # Ensure all expected columns exist
        expected_cols = [
            'application_id', 'type', 'company_name', 'email', 'phone', 'address',
            'city', 'state', 'zip', 'tax_id', 'industry', 'mfaEnabled', 'ssoSupport',
            'rbacImplemented', 'encryptionAtRest', 'encryptionInTransit', 'keyManagement',
            'firewallEnabled', 'vpnRequired', 'ipWhitelisting', 'auditLogging',
            'siemIntegration', 'alertingEnabled', 'gdprCompliant', 'soc2Certified',
            'isoCompliant', 'is_fraud'
        ]
        
        # Add missing columns with default values
        for col in expected_cols:
            if col not in df.columns:
                if col in ['mfaEnabled', 'ssoSupport', 'rbacImplemented', 'encryptionAtRest',
                          'encryptionInTransit', 'keyManagement', 'firewallEnabled', 'vpnRequired',
                          'ipWhitelisting', 'auditLogging', 'siemIntegration', 'alertingEnabled',
                          'gdprCompliant', 'soc2Certified', 'isoCompliant', 'is_fraud']:
                    df[col] = 0  # Boolean columns default to 0
                else:
                    df[col] = ''  # String columns default to empty
        
        # Save processed version
        processed_path = PROCESSED_DIR / 'supplier_quality_processed.csv'
        df.to_csv(processed_path, index=False)
        print(f"✓ Saved processed data to {processed_path}")
        
        print(f"\nDataset Summary:")
        print(f"  Total records: {len(df)}")
        print(f"  Fraud cases: {df['is_fraud'].sum()} ({df['is_fraud'].sum() / len(df) * 100:.2f}%)")
        print(f"  Columns: {len(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"✗ Error processing supplier quality dataset: {e}")
        return None

def create_training_features(df, dataset_type='creditcard'):
    """Create features suitable for training the fraud detection model"""
    print(f"\nCreating training features for {dataset_type} dataset...")
    
    if dataset_type == 'creditcard':
        # Extract relevant features from credit card dataset
        feature_cols = [col for col in df.columns if col.startswith('V') or col in ['Time', 'Amount']]
        X = df[feature_cols].values
        y = df['Class'].values if 'Class' in df.columns else None
        
    elif dataset_type == 'supplier':
        # Extract features from supplier dataset
        # Convert boolean columns to numeric
        bool_cols = ['mfaEnabled', 'ssoSupport', 'rbacImplemented', 'encryptionAtRest',
                    'encryptionInTransit', 'keyManagement', 'firewallEnabled', 'vpnRequired',
                    'ipWhitelisting', 'auditLogging', 'siemIntegration', 'alertingEnabled',
                    'gdprCompliant', 'soc2Certified', 'isoCompliant']
        
        # Create feature matrix
        features = []
        for col in bool_cols:
            if col in df.columns:
                features.append(df[col].astype(int).values)
        
        if features:
            X = np.column_stack(features)
        else:
            X = np.zeros((len(df), 1))
        
        y = df['is_fraud'].values if 'is_fraud' in df.columns else None
    
    else:
        X = None
        y = None
    
    if X is not None:
        print(f"  Feature matrix shape: {X.shape}")
        if y is not None:
            print(f"  Target distribution: {np.bincount(y)}")
    
    return X, y

def main():
    """Main processing function"""
    print("="*50)
    print("Kaggle Data Processing Script")
    print("="*50)
    
    # Create processed directory
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process credit card fraud dataset
    creditcard_df = process_creditcard_fraud()
    
    # Process supplier quality dataset
    supplier_df = process_supplier_quality()
    
    # Create training features
    if creditcard_df is not None:
        X_cc, y_cc = create_training_features(creditcard_df, 'creditcard')
    
    if supplier_df is not None:
        X_supplier, y_supplier = create_training_features(supplier_df, 'supplier')
    
    print("\n" + "="*50)
    print("Processing Complete!")
    print("="*50)
    print(f"\nProcessed files saved to: {PROCESSED_DIR}")
    print("\nNext steps:")
    print("1. Review the processed CSV files")
    print("2. Use the data to retrain the fraud detection model")
    print("3. Update ml_fraud_detection.py to use the new training data")

if __name__ == '__main__':
    main()

