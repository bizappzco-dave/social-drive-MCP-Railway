# SocialDrive AI - Railway MCP Deployment Status
**Date:** May 30, 2026  
**Session End:** 18:50 IST

---

## 🎯 Goal
Deploy self-hosted Ollama + MCP server on Railway to replace Ollama Cloud API (~€40-50/month → ~€5-10/month).

---

## ✅ Completed

### 1. Ollama Service (Railway)
- **Status:** ✅ RUNNING
- **URL:** `https://ollama-production-6ab6.up.railway.app`
- **Model:** `llama3.2:latest` (2.0GB)
- **Project:** `aware-simplicity` → `distinguished-elegance` service
- **Image:** `ollama/ollama:latest` (official Railway template)
- **Test:** `curl https://ollama-production-6ab6.up.railway.app/api/tags` ✅ Returns model list

### 2. MCP Server Code
- **Repo:** `bizappzco-dave/social-drive-MCP-Railway`
- **Files:** 
  - `Dockerfile` ✅ (Python 3.11, runs `simple_http_server.py`)
  - `railway.toml` ✅ (forces Dockerfile deployment)
  - `simple_http_server.py` ✅ (HTTP server, port 8765)
  - `ollama_client.py` ✅ (connects to Ollama URL)
  - `.dockerignore` ✅ (excludes .env from build)
- **Environment Variables Needed:**
  ```
  OLLAMA_BASE_URL=https://ollama-production-6ab6.up.railway.app
  OLLAMA_MODEL=llama3.2
  PORT=8765
  ```

### 3. Local Ollama (Reference)
- **Version:** 0.18.3
- **Status:** Running as systemd service
- **Models:** llama3.2:latest, bizappzco/SocialDriveAI:latest, qwen3.5:cloud, qwen2.5:7b
- **Port:** 11434
- **Check:** `ollama list`, `systemctl status ollama`

---

## ⏳ In Progress

### MCP Server Deployment (Railway)
- **Status:** ⚠️ BLOCKED - Railway CLI auth issues with GitHub
- **Service:** `mcp-server` created in `aware-simplicity` project
- **Problem:** Railway deploying raw `python:3.11-slim` image instead of using Dockerfile
- **Solution Created:** Added `railway.toml` to force Dockerfile deployment
- **Next Step:** Manual deployment via Railway dashboard

---

## 📋 Tomorrow's Steps (Railway Dashboard)

### 1. Go to Railway Project
https://railway.com/project/afa5edc7-d90e-4d08-99e7-aaf3b70e8865

### 2. Create New Service from GitHub
- Click **"New"** → **"GitHub Repo"**
- Select: `bizappzco-dave/social-drive-MCP-Railway`
- Railway should auto-detect `railway.toml` + `Dockerfile`

### 3. If Build Method Shows "Start Command":
- Click service → **"Settings"** tab
- Scroll to **"Build"** section
- Click **"Edit"**
- Change **"Build Method"** to **"Dockerfile"**
- Click **"Save"**

### 4. Add Environment Variables
Click **"Variables"** tab → Add:
```
OLLAMA_BASE_URL=https://ollama-production-6ab6.up.railway.app
OLLAMA_MODEL=llama3.2
PORT=8765
```

### 5. Deploy
- Click **"Deployments"** → **"Deploy from GitHub"**
- Wait ~2-3 minutes for build

### 6. Generate Domain
- Click **"Settings"** → **"Networking"**
- Click **"Generate Domain"**
- Copy URL (e.g., `https://social-drive-mcp-production.up.railway.app`)

### 7. Test
```bash
# Test health endpoint
curl https://your-mcp-domain.up.railway.app/health

# Expected response:
{"status": "healthy", "ollama_url": "https://ollama-production-6ab6.up.railway.app", "model": "llama3.2"}
```

### 8. Update Frontend (I'll Do This)
Once you give me the MCP server URL, I'll:
- Update `src/app/upload/[token]/simple-page.tsx`
- Update `src/app/upload/[token]/pro-page.tsx`
- Deploy frontend to Vercel
- Test end-to-end flow

---

## 🚨 Troubleshooting

### Container Exits Immediately
**Cause:** Railway not using Dockerfile  
**Fix:** Settings → Build → Change to "Dockerfile" → Save → Redeploy

### Health Check Fails
**Cause:** Ollama URL not set or Ollama service down  
**Fix:** Check variables, test Ollama: `curl https://ollama-production-6ab6.up.railway.app/api/tags`

### Build Fails
**Cause:** Missing dependencies  
**Fix:** Check build logs, verify `requirements.txt` in repo root

---

## 📊 Cost Savings

| Service | Before | After | Savings |
|---------|--------|-------|---------|
| Ollama Cloud API | ~€40-50/month | €0 (self-hosted) | 100% |
| Railway Hosting | N/A | ~€5-10/month | - |
| **Total** | **€40-50/month** | **€5-10/month** | **75-80%** |

---

## 🔗 Key URLs

- **Ollama Service:** https://ollama-production-6ab6.up.railway.app
- **MCP Server:** TBD (deploy tomorrow)
- **Railway Project:** https://railway.com/project/afa5edc7-d90e-4d08-99e7-aaf3b70e8865
- **GitHub Repo:** https://github.com/bizappzco-dave/social-drive-MCP-Railway

---

## 📝 Notes

- Railway CLI has GitHub auth issues - use dashboard for deployment
- `railway.toml` forces Dockerfile deployment (committed to repo)
- Two services needed: Ollama (✅ done) + MCP server (⏳ pending)
- Frontend currently points to `http://localhost:8765` - will update after MCP deploy

---

**Next Session:** Resume from "Tomorrow's Steps" above. Once MCP server URL is ready, update frontend and deploy to Vercel.
