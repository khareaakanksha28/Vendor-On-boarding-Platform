#!/usr/bin/env python3
"""
Prepare training data files from generated supplier data
Creates onboarding_train.csv, onboarding_test.csv, and onboarding_training_data.csv
"""
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

def main():
    """Split supplier data into train/test sets"""
    print("="*50)
    print("Preparing Training Data Files")
    print("="*50)
    
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Load supplier quality data
    supplier_file = data_dir / 'supplier_quality_data.csv'
    
    if not supplier_file.exists():
        print(f"⚠️ {supplier_file} not found. Generating data first...")
        import generate_training_data
        generate_training_data.main()
    
    print(f"\n📂 Loading {supplier_file}...")
    df = pd.read_csv(supplier_file)
    print(f"✅ Loaded {len(df)} records")
    
    # Save full dataset
    full_data_path = data_dir / 'onboarding_training_data.csv'
    df.to_csv(full_data_path, index=False)
    print(f"✅ Saved full dataset to {full_data_path}")
    
    # Split into train and test (80/20)
    if 'is_fraud' in df.columns:
        X = df.drop('is_fraud', axis=1)
        y = df['is_fraud']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Add target back
        train_df = X_train.copy()
        train_df['is_fraud'] = y_train.values
        
        test_df = X_test.copy()
        test_df['is_fraud'] = y_test.values
    else:
        # No target column, just split randomly
        train_df, test_df = train_test_split(
            df, test_size=0.2, random_state=42
        )
    
    # Save train and test sets
    train_path = data_dir / 'onboarding_train.csv'
    test_path = data_dir / 'onboarding_test.csv'
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"✅ Saved training set ({len(train_df)} records) to {train_path}")
    print(f"✅ Saved test set ({len(test_df)} records) to {test_path}")
    
    if 'is_fraud' in train_df.columns:
        print(f"\n📊 Training set: {train_df['is_fraud'].sum()} fraud cases ({train_df['is_fraud'].sum()/len(train_df)*100:.1f}%)")
        print(f"📊 Test set: {test_df['is_fraud'].sum()} fraud cases ({test_df['is_fraud'].sum()/len(test_df)*100:.1f}%)")
    
    print("\n" + "="*50)
    print("✅ Training data preparation complete!")
    print("="*50)

if __name__ == '__main__':
    main()

