# Frontend Deployment Guide

## Option 1: Deploy to Vercel (Recommended - Easiest)

### Step 1: Create Vercel Account
1. Go to: https://vercel.com/signup
2. Sign up with GitHub (easiest - connects to your repo)

### Step 2: Deploy from GitHub
1. After signing in, click "Add New Project"
2. Import your repository: `Vendor-On-boarding-Platform`
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Create React App
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
4. Add Environment Variable:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: Your backend URL (e.g., `https://your-backend.herokuapp.com/api/v1`)
5. Click "Deploy"

### Step 3: Get Your Frontend Link
- Vercel will give you a URL like: `https://vendor-onboarding-platform.vercel.app`
- This is your frontend link for submission!

---

## Option 2: Deploy to Netlify

### Step 1: Create Netlify Account
1. Go to: https://app.netlify.com/signup
2. Sign up with GitHub

### Step 2: Deploy
1. Click "Add new site" → "Import an existing project"
2. Select your GitHub repository
3. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`
4. Add Environment Variable:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: Your backend URL
5. Click "Deploy site"

---

## Option 3: Deploy Backend First (Required)

Your frontend needs a backend URL. Options:

### A. Deploy Backend to Heroku (Free)
1. Create account: https://heroku.com
2. Install Heroku CLI
3. Deploy backend:
   ```bash
   cd backend
   heroku create your-app-name
   git push heroku main
   ```

### B. Use Local Backend (Development Only)
- Not recommended for submission
- Only works when your computer is on

### C. Use Backend as a Service
- Railway.app
- Render.com
- Fly.io

---

## Quick Vercel Deployment (Recommended)

1. **Sign up**: https://vercel.com (use GitHub)
2. **Import**: Your `Vendor-On-boarding-Platform` repo
3. **Settings**:
   - Root: `frontend`
   - Build: `npm run build`
   - Output: `build`
4. **Environment**: Add `REACT_APP_API_URL`
5. **Deploy** → Get your frontend URL!

---

## Important Notes

- Frontend URL will be something like: `https://vendor-onboarding-platform.vercel.app`
- Backend URL needs to be deployed separately (Heroku, Railway, etc.)
- Update `REACT_APP_API_URL` in Vercel settings with your backend URL
- Frontend will automatically redeploy when you push to GitHub

