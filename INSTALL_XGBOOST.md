# Optional: Installing XGBoost/LightGBM Support

## Current Status
✅ **Your system is already using the BEST model (SVM) with 97.5% accuracy!**
- XGBoost/LightGBM are **optional** and not required
- The system is fully functional without them

## Why Install XGBoost/LightGBM?
- Only if you want to experiment with different models
- They may perform better on different datasets
- For research/comparison purposes

## Installation Steps (Optional)

### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. You may need to:
- Enter your password
- Add Homebrew to your PATH (instructions will be shown)

### 2. Install OpenMP (required for XGBoost)
```bash
brew install libomp
```

### 3. Re-run Model Training
```bash
cd onboarding-hub
source backend/venv/bin/activate
python3 train_ml_models_comparison.py
```

This will now include XGBoost and LightGBM in the comparison.

## Recommendation
**You don't need to do this!** Your system is already optimized with SVM, which is the best-performing model. Only install if you want to experiment with other models.

