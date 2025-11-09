# DevPost Submission - Quick Setup

## What You Need for DevPost

1. ✅ **GitHub Repository**: https://github.com/khareaakanksha28/Vendor-On-boarding-Platform
2. ⏳ **Live Demo Link**: Deploy frontend (see below)
3. ✅ **Project Description**: In README.md
4. ✅ **Screenshots**: Take screenshots of your app

---

## Get Frontend Link (5 Minutes)

### Quick Vercel Deployment

1. **Sign Up**: https://vercel.com/signup
   - Click "Continue with GitHub"
   - Authorize Vercel

2. **Import Project**:
   - Click "Add New Project"
   - Select: `Vendor-On-boarding-Platform`
   - Click "Import"

3. **Configure**:
   - **Root Directory**: `frontend`
   - **Framework**: Create React App (auto-detected)
   - **Build Command**: `npm run build` (auto)
   - **Output Directory**: `build` (auto)

4. **Environment Variable**:
   - Click "Environment Variables"
   - Add:
     - **Name**: `REACT_APP_API_URL`
     - **Value**: `http://localhost:5001/api/v1` (for demo)
     - Or your deployed backend URL

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - **Copy your URL**: `https://vendor-onboarding-platform.vercel.app`

---

## DevPost Submission Form

Fill in:
- **Project Name**: Secure & Intelligent Onboarding Hub
- **GitHub Repository**: https://github.com/khareaakanksha28/Vendor-On-boarding-Platform
- **Live Demo**: `https://your-app.vercel.app` (after deployment)
- **Description**: See README.md
- **Screenshots**: Take screenshots of your app

---

## Alternative: Netlify

If Vercel doesn't work:

1. Go to: https://app.netlify.com
2. Sign up with GitHub
3. "Add new site" → "Import an existing project"
4. Select your repo
5. Settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/build`
6. Add environment variable: `REACT_APP_API_URL`
7. Deploy

---

## Note

- Frontend will work but needs backend running
- For demo: Run backend locally or deploy backend too
- DevPost usually accepts GitHub link + demo video if live demo has issues

