# Deployment Guide - Vercel + Render

## Current Architecture

- **Backend**: Already deployed on Render at `https://ai-voice-agent-l1x7.onrender.com`
- **Frontend**: Ready to deploy to Vercel
- **Database**: SQLite (included in Render backend)

## Quick Start - Deploy Frontend to Vercel

### 1. Connect to GitHub (One-time setup)

```bash
# Make sure your code is pushed to GitHub
git add .
git commit -m "Prepare for Vercel deployment"
git push origin master
```

### 2. Deploy to Vercel

**Option A: Using Vercel CLI (Recommended)**

```bash
# Install Vercel CLI globally
npm i -g vercel

# Login to Vercel (follow prompts)
vercel login

# Deploy from project root
vercel --prod
```

**Option B: Using Vercel Web Dashboard**

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select your GitHub repository
4. Configure build settings:
   - Framework: Next.js
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/.next`
5. Add Environment Variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://ai-voice-agent-l1x7.onrender.com`
6. Click "Deploy"

### 3. Environment Variables for Vercel

In Vercel Dashboard → Project Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL = https://ai-voice-agent-l1x7.onrender.com
```

## Troubleshooting

### Frontend shows "Failed to connect to server"

**Causes & Solutions:**

1. **API URL not set in Vercel**
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Add/Update `NEXT_PUBLIC_API_URL`
   - Redeploy the project

2. **CORS issue**
   - Backend at Render allows all origins (`*`), so this should work
   - Check browser console for CORS errors

3. **Backend not responding**
   - Test backend: `curl https://ai-voice-agent-l1x7.onrender.com/`
   - Should return: `{"status":"ok","app":"Voice Recruitment Agent"}`

### Signup endpoint returns 500 error

**Solution:**
- Backend error logs are at Render Dashboard → Logs
- Most common cause was bcrypt compatibility (already fixed)

## Testing the Deployment

### 1. Test API Health Check

```bash
curl https://ai-voice-agent-l1x7.onrender.com/
# Should return: {"status":"ok","app":"Voice Recruitment Agent"}
```

### 2. Test Signup Endpoint

```bash
curl -X POST https://ai-voice-agent-l1x7.onrender.com/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "company": "Test Co"
  }'
```

### 3. Test from Vercel Frontend

1. Visit your Vercel deployment URL
2. Fill in signup form with valid data
3. Should complete without errors

## Local Development (Keep working locally)

Keep using your local setup:

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
# Visit http://localhost:3000
```

The `.env.local` file is ignored by git, so it won't interfere with Vercel deployment.

## Environment Variables Summary

| Environment | API URL | Frontend URL |
|---|---|---|
| Local | `http://localhost:8000` | `http://localhost:3000` |
| Production | `https://ai-voice-agent-l1x7.onrender.com` | `https://<your-vercel-url>.vercel.app` |

## Next Steps

1. Deploy frontend to Vercel
2. Set `NEXT_PUBLIC_API_URL` in Vercel environment variables
3. Test signup flow from Vercel deployment
4. Monitor backend logs at Render Dashboard if issues occur
