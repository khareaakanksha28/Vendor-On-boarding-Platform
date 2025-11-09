#!/bin/bash

# Setup Kaggle CLI and download datasets

set -e

echo "=========================================="
echo "Kaggle Dataset Setup Script"
echo "=========================================="

# Check if kaggle.json exists
if [ ! -f "kaggle.json" ]; then
    echo "⚠️  kaggle.json not found in current directory"
    echo "Please download your Kaggle API credentials:"
    echo "1. Go to https://www.kaggle.com/settings"
    echo "2. Click 'Create New API Token'"
    echo "3. Save kaggle.json in this directory"
    echo ""
    read -p "Press Enter after you've placed kaggle.json here, or Ctrl+C to cancel..."
fi

# Configure Kaggle API
echo "📁 Setting up Kaggle configuration..."
mkdir -p ~/.kaggle

if [ -f "kaggle.json" ]; then
    cp kaggle.json ~/.kaggle/
    chmod 600 ~/.kaggle/kaggle.json
    echo "✓ Kaggle API configured"
else
    echo "✗ kaggle.json not found. Please add it and run again."
    exit 1
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data
mkdir -p data/processed

# Find kaggle command
if command -v kaggle &> /dev/null; then
    KAGGLE_CMD="kaggle"
elif [ -f "backend/venv/bin/kaggle" ]; then
    KAGGLE_CMD="backend/venv/bin/kaggle"
elif python3 -m kaggle --version &> /dev/null; then
    KAGGLE_CMD="python3 -m kaggle"
else
    echo "✗ Kaggle CLI not found. Installing..."
    pip3 install kaggle
    if command -v kaggle &> /dev/null; then
        KAGGLE_CMD="kaggle"
    else
        KAGGLE_CMD="python3 -m kaggle"
    fi
fi

echo "Using kaggle command: $KAGGLE_CMD"

# Download datasets
echo ""
echo "📥 Downloading datasets..."

echo "  → Downloading creditcardfraud dataset..."
if $KAGGLE_CMD datasets download -d mlg-ulb/creditcardfraud -p data/ 2>/dev/null; then
    echo "  ✓ Credit card fraud dataset downloaded"
else
    echo "  ⚠️  Failed to download creditcardfraud dataset (may require accepting terms on Kaggle)"
    echo "     Visit: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"
fi

echo "  → Downloading supplier-quality-data dataset..."
if $KAGGLE_CMD datasets download -d saravanandeveloper/supplier-quality-data -p data/ 2>/dev/null; then
    echo "  ✓ Supplier quality dataset downloaded"
else
    echo "  ⚠️  Supplier quality dataset not found on Kaggle"
    echo "  → Generating synthetic supplier quality dataset instead..."
    python3 generate_supplier_data.py
fi

# Unzip datasets
echo ""
echo "📦 Extracting datasets..."

if [ -f "data/creditcardfraud.zip" ]; then
    echo "  → Extracting creditcardfraud.zip..."
    unzip -q data/creditcardfraud.zip -d data/
    echo "  ✓ Credit card fraud dataset extracted"
else
    echo "  ⚠️  creditcardfraud.zip not found"
fi

if [ -f "data/supplier-quality-data.zip" ]; then
    echo "  → Extracting supplier-quality-data.zip..."
    unzip -q data/supplier-quality-data.zip -d data/
    echo "  ✓ Supplier quality dataset extracted"
elif [ -f "data/supplier_quality_data.csv" ]; then
    echo "  ✓ Using generated supplier quality dataset"
else
    echo "  ⚠️  Supplier quality dataset not found, generating one..."
    python3 generate_supplier_data.py
fi

# Process datasets
echo ""
echo "🔄 Processing datasets..."
python3 process_kaggle_data.py

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review the processed data in data/processed/"
echo "2. Update ml_fraud_detection.py to use the new training data"
echo "3. Retrain the model with the processed datasets"

