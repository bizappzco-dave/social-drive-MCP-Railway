# SocialDrive AI - Railway Deployment Status

**Last Updated:** May 31, 2026 — FULLY OPERATIONAL ✅

---

## Live URLs

| Service | URL | Status |
|---------|-----|--------|
| Ollama (Railway) | https://ollama-production-6ab6.up.railway.app | ✅ Running — llama3.2:latest |
| MCP Server (Railway) | https://social-drive-mcp-railway-production-cb81.up.railway.app | ✅ Running — healthy |
| Frontend (Vercel) | https://socialdrive-ai.vercel.app | ✅ Deployed — NEXT_PUBLIC_MCP_URL set |

---

## Railway Project Details

**Project:** aware-simplicity  
**Project ID:** afa5edc7-d90e-4d08-99e7-aaf3b70e8865  
**Environment ID:** 9e9dfaff-f582-41c0-b592-675907870e25

| Service Name | Service ID | Role |
|---|---|---|
| distinguished-elegance | 11cc5683-b85b-459d-bf56-3ea5633e9ab3 | Ollama (Railway template) |
| social-drive-MCP-Railway | 5201592b-fefb-4953-9a6f-044ec07e0e1b | MCP HTTP server (GitHub) |

**IMPORTANT:** `distinguished-elegance` = Ollama service (not MCP). Railway auto-generates random names.
Verify by curling `/` — "Ollama is running" = Ollama, JSON = MCP.

---

## GitHub Repo

**MCP Server:** https://github.com/bizappzco-dave/social-drive-MCP-Railway  
**Local path:** `/home/dpmcg/image-analyzer-mcp/`

Commits in order:
- `62b7cb5` - Don't load .env on Railway
- `71ed50f` - Use Railway OLLAMA_BASE_URL env var
- `9b965f8` - Add .dockerignore
- `5538389` - Add railway.toml (force Dockerfile build)
- `b3d5a7b` - Deployment status backup
- `6b187ba` - Fix Dockerfile: add curl, remove hardcoded PORT/EXPOSE
- `8b0a310` - Remove healthcheck from railway.toml
- `46dda55` - Minimal Dockerfile: explicit deps, copy only needed files
- `a105970` - Fix: parse template_match string to dict in generate-captions ← LATEST

---

## Environment Variables

**Railway MCP Service (social-drive-MCP-Railway):**
```
OLLAMA_BASE_URL=https://ollama-production-6ab6.up.railway.app
OLLAMA_MODEL=llama3.2
```
Set via Railway dashboard → service → Variables tab.

**Vercel (socialdrive-ai):**
```
NEXT_PUBLIC_MCP_URL=https://social-drive-mcp-railway-production-cb81.up.railway.app
```

---

## MCP Endpoints

```bash
# Health check
curl https://social-drive-mcp-railway-production-cb81.up.railway.app/health
# Returns: {"status":"healthy","ollama_url":"https://ollama-production-6ab6.up.railway.app","model":"llama3.2"}

# Ollama status
curl https://social-drive-mcp-railway-production-cb81.up.railway.app/ollama/status
# Returns: {"ollama_healthy":true,"available_models":[{"name":"llama3.2:latest",...}]}

# Template match (POST)
curl -X POST https://social-drive-mcp-railway-production-cb81.up.railway.app/template/match \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "...", "industry": "barber"}'

# Generate captions (POST)
curl -X POST https://social-drive-mcp-railway-production-cb81.up.railway.app/generate-captions \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"...","template_match":"...or {}...","industry":"barber","count":3}'
```

---

## Known Bug Fixed

**template_match string-to-dict (fixed in a105970)**

The `/template/match` endpoint returns `{"success":true,"response":"...json string..."}`.
If you pass the raw `response` string as `template_match` to `/generate-captions`, it previously
crashed with `'str' object has no attribute 'get'`.

Fixed: the handler now auto-parses string → dict via regex JSON extraction.

---

## Redeploy Procedure

```bash
# 1. Make code change in /home/dpmcg/image-analyzer-mcp/
# 2. Push to GitHub
cd /home/dpmcg/image-analyzer-mcp && git add . && git commit -m "..." && git push origin main

# 3. Trigger Railway redeploy via API
TOKEN="IfkppiwbQEQJfuDIIfA_qtxd655xPIumF6RP4j2t0a_"
curl -s -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { serviceInstanceRedeploy(serviceId: \"5201592b-fefb-4953-9a6f-044ec07e0e1b\", environmentId: \"9e9dfaff-f582-41c0-b592-675907870e25\") }"}' 

# 4. Wait ~90 seconds, test health
curl https://social-drive-mcp-railway-production-cb81.up.railway.app/health
```

Note: Railway API sometimes times out on mutations — use the dashboard as fallback.

---

## Cost

| | Before | After |
|---|---|---|
| Ollama Cloud API | ~€40-50/month | €0 |
| Railway hosting | €0 | ~€5-10/month |
| **Total** | **~€50/month** | **~€5-10/month** |
| **Savings** | | **~75-80%** |
