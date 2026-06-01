# Deploy to Vercel - Step by Step

Your backend is already running at: `https://ai-voice-agent-l1x7.onrender.com`

## QUICK STEPS (5 minutes)

### Step 1: GitHub Setup (Already Done ✓)
Your code is already pushed to: `https://github.com/Likesh2010/AI-Voice-Agent`

### Step 2: Go to Vercel

Visit: https://vercel.com/new

Click **"Continue with GitHub"** and authorize if needed

### Step 3: Import Your Repository

- Select: `Likesh2010/AI-Voice-Agent`
- Click **"Import"**

### Step 4: Configure Project

**Build & Output:**
- Framework Preset: `Next.js`
- Root Directory: `./frontend`
- Build Command: `npm run build`
- Output Directory: `.next`

**Environment Variables:**

Click "Environment Variables" and add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://ai-voice-agent-l1x7.onrender.com` |

### Step 5: Deploy

Click **"Deploy"** button

⏳ Wait 2-3 minutes for build to complete

✅ You'll get a URL like: `https://your-project.vercel.app`

## TEST YOUR DEPLOYMENT

1. Open your Vercel URL
2. Fill signup form:
   - Name: `Your Name`
   - Company: `Your Company`
   - Email: `your.email@example.com`
   - Password: `anything`
3. Click "Create Client Account"
4. Should sign up successfully ✓

## IF IT STILL FAILS

### Option A: Verify Environment Variable Set

1. Go to your Vercel Project Settings
2. Click "Environment Variables"
3. Check that `NEXT_PUBLIC_API_URL` is set to `https://ai-voice-agent-l1x7.onrender.com`
4. Click three dots menu on the variable → "Redeploy from cache"
5. Wait for rebuild

### Option B: Check Browser Console

1. Open your Vercel deployment
2. Press F12 (Developer Tools)
3. Go to "Network" tab
4. Try signup again
5. Click on the failed request in Network tab
6. Check the "Response" to see what error the API returned

### Option C: Test Backend Directly

Open in browser: `https://ai-voice-agent-l1x7.onrender.com/`

Should show: `{"status":"ok","app":"Voice Recruitment Agent"}`

## LOCAL DEVELOPMENT (Keep Using)

Your local setup still works:

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit: `http://localhost:3000`

## NEED HELP?

Common Issues:

| Problem | Solution |
|---------|----------|
| Signup page blank | Clear browser cache + hard refresh (Ctrl+Shift+R) |
| API URL error | Check Vercel Environment Variables are set |
| CORS error | Not possible - backend allows all origins |
| Backend 500 error | Backend needs redeploy - contact support |

---

**That's it! You now have live production deployment on Vercel.**
