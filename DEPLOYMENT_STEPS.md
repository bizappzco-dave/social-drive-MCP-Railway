# 🚀 SocialDrive MCP - GitHub + Railway Deployment

**Quick Reference Guide** - Follow these steps in order

---

## ✅ Step 1: Create GitHub Repo

1. Go to https://github.com/new
2. **Repository name:** `socialdrive-mcp`
3. **Visibility:** Public (or Private)
4. **⚠️ DO NOT initialize with:** README, .gitignore, or License
5. Click **"Create repository"**
6. **Copy the repo URL** (you'll need it in Step 3)

---

## ✅ Step 2: Push Code To GitHub

Run these commands in your terminal:

```bash
cd /home/dpmcg/image-analyzer-mcp

# Initialize git repo
git init

# Add all files
git add *.py requirements.txt Dockerfile RAILWAY_DEPLOY.md

# Commit
git commit -m "Initial commit - SocialDrive MCP server for Railway"

# Set main branch
git branch -M main

# Add your GitHub remote (REPLACE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/socialdrive-mcp.git

# Push to GitHub
git push -u origin main
```

**⚠️ IMPORTANT:** Replace `YOUR_USERNAME` with your actual GitHub username!

---

## ✅ Step 3: Deploy To Railway

1. Go to https://railway.app
2. Click **"New Project"**
3. Choose **"Deploy from GitHub repo"**
4. Connect your GitHub account (if not already connected)
5. Select **`socialdrive-mcp`** repo
6. Railway will auto-detect Python and start building
7. **⏱️ Build takes ~2-3 minutes**

---

## ✅ Step 4: Add Environment Variables

In Railway dashboard (while it's building):

1. Click on your project
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add these 4 variables:

```
PORT=8765
HOST=0.0.0.0
OLLAMA_BASE_URL=http://localhost:11434
MODEL=llama3.2:latest
```

✅ Railway will auto-redeploy with new vars

---

## ✅ Step 5: Get Your Railway URL

After deployment completes:

1. In Railway dashboard, click **"Settings"**
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. You'll get a URL like:
   ```
   https://socialdrive-mcp-production.up.railway.app
   ```
5. **Copy this URL!**

**Test it:**
```bash
curl https://your-railway-url.up.railway.app/health
```

✅ Should return: `{"status":"ok"}`

---

## ✅ Step 6: Update Frontend (I'll Help With This!)

**Once you have the Railway URL, tell me and I'll:**

1. Update `simple-page.tsx` to use production URL
2. Update `pro-page.tsx` to use production URL
3. Add environment variable config
4. Deploy updated frontend to Vercel

---

## 📊 Environment Variables Reference

| Variable | Value | Required |
|----------|-------|----------|
| `PORT` | `8765` | ✅ Yes |
| `HOST` | `0.0.0.0` | ✅ Yes |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | ✅ Yes |
| `MODEL` | `llama3.2:latest` | ✅ Yes |

---

## 🧪 Testing Checklist

After deployment, test these endpoints:

```bash
# Health check
curl https://your-railway-url/health

# Template match (test with base64 image)
curl -X POST https://your-railway-url/template/match \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "...", "industry": "barber"}'

# Generate captions
curl -X POST https://your-railway-url/generate-captions \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "...", "template_match": {...}, "industry": "barber", "count": 3}'
```

---

## 🆘 Troubleshooting

### Build Fails
- Check Railway build logs
- Verify `requirements.txt` is in root
- Ensure Python version is 3.8+

### Service Won't Start
- Check environment variables are set
- Verify PORT is 8765
- Check logs: Railway → Logs tab

### Health Check Fails
- Wait 30 seconds after deploy
- Check logs for errors
- Verify Ollama is accessible

### CORS Errors (from frontend)
- I'll add CORS headers to the server
- Update frontend with correct URL

---

## 📞 Next Steps

1. ✅ Complete Steps 1-5 above
2. ✅ Get your Railway URL
3. ✅ **Tell me the URL**
4. ✅ I'll update the frontend code
5. ✅ Deploy to Vercel
6. ✅ Test end-to-end!

---

## 💰 Railway Pricing

**Free Tier:**
- $5/month credit
- 500 hours runtime/month
- 1GB RAM
- Shared CPU

**Pro Tip:** Use UptimeRobot (free) to ping every 5 minutes to prevent sleep

**Estimated Cost:** ~€5/month for 24/7 MCP server

---

**Good luck with deployment! Let me know when you have the Railway URL! 🚀**
