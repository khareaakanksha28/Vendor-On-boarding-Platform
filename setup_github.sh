#!/bin/bash

# GitHub Setup Script for Onboarding Hub

echo "🚀 Setting up GitHub repository..."
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo ""
echo "📝 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "⚠️  No changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "Initial commit: Secure & Intelligent Onboarding Hub

- Complete onboarding platform with fraud detection
- ML models: SVM, Random Forest, Isolation Forest
- React frontend with Figma design system
- Flask backend with JWT authentication
- Auto-approval for low-risk applications
- Kaggle data import functionality
- End-to-end application management UI"
    echo "✅ Changes committed"
fi

echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Name it: onboarding-hub (or your preferred name)"
echo "   - Don't initialize with README (we already have one)"
echo ""
echo "2. Add the remote and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Or if you already have a remote:"
echo "   git remote -v  # Check existing remotes"
echo "   git push -u origin main"
echo ""
echo "✅ Setup complete! Your code is ready for GitHub."

