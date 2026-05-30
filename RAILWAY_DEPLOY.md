# SocialDrive AI MCP Server on Railway
# Deployment Guide

## 🚀 Quick Start

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Verify email

### Step 2: Create New Project
1. Click **"New Project"**
2. Choose **"Deploy from GitHub repo"** (recommended) OR **"Empty Service"**
3. If GitHub: Connect your GitHub account and select the repo
4. If Empty: We'll push code manually

### Step 3: Configure Service

**Service Name:** `socialdrive-mcp` (or whatever you prefer)

**Environment Variables:**
```
PORT=8765
HOST=0.0.0.0
OLLAMA_BASE_URL=http://localhost:11434
MODEL=llama3.2:latest
```

**Important:** Railway will auto-detect the port from `PORT` env var

### Step 4: Deploy

**Option A - GitHub (Recommended):**
1. Push MCP code to GitHub repo
2. Railway auto-deploys on push
3. Done! ✅

**Option B - Railway CLI:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Step 5: Get Your URL

After deployment, Railway gives you a public URL:
```
https://socialdrive-mcp-production.up.railway.app
```

**Test it:**
```bash
curl https://your-railway-url.up.railway.app/health
```

### Step 6: Update Frontend

Change MCP URLs in these files:

**`src/app/upload/[token]/simple-page.tsx`:**
```typescript
// OLD (line 95, 113):
const templateResponse = await fetch('http://localhost:8765/template/match', ...)
const captionResponse = await fetch('http://localhost:8765/generate-captions', ...)

// NEW:
const MCP_BASE_URL = process.env.NEXT_PUBLIC_MCP_URL || 'https://your-railway-url.up.railway.app'
const templateResponse = await fetch(`${MCP_BASE_URL}/template/match`, ...)
const captionResponse = await fetch(`${MCP_BASE_URL}/generate-captions`, ...)
```

**`src/app/upload/[token]/pro-page.tsx`:**
```typescript
// Same changes as above
```

**Add to `.env.local`:**
```
NEXT_PUBLIC_MCP_URL=https://your-railway-url.up.railway.app
```

---

## 📊 Railway Pricing

**Free Tier:**
- $5/month credit
- 500 hours runtime/month
- 1GB RAM
- Shared CPU

**Paid Tier:**
- $5/month base + usage
- Unlimited hours
- More RAM/CPU available

**Estimated Cost:** ~€5-10/month for 24/7 MCP server

---

## 🔧 Troubleshooting

### Build Fails
- Check Railway build logs
- Ensure `requirements.txt` is in root
- Verify Python version (3.8+)

### Service Won't Start
- Check environment variables
- Verify PORT is set to 8765
- Check logs: `railway logs`

### Health Check Fails
- Wait 30 seconds after deploy
- Check logs for errors
- Verify Ollama is accessible (if using remote Ollama)

---

## 📝 Notes

- Railway sleeps services after inactivity on free tier
- Use **UptimeRobot** (free) to ping every 5 minutes to keep awake
- Or upgrade to paid tier for always-on

---

## 🎯 Next Steps

1. ✅ Set up Railway account
2. ✅ Deploy MCP server
3. ✅ Get public URL
4. ✅ Update frontend code
5. ✅ Test end-to-end
6. ✅ Deploy frontend to Vercel

---

**Questions?** Check Railway docs: https://docs.railway.app
