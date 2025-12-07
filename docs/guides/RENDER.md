# Render.com Deployment Guide

This guide helps you deploy x402 Insurance to Render.com quickly and efficiently.

## Quick Deployment

### Option 1: Blueprint (Fastest)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **"New" → "Blueprint"**
4. Connect your GitHub repo
5. Render will automatically detect `render.yaml` and deploy

### Option 2: Manual Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New" → "Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name**: `x402-insurance`
   - **Runtime**: `Docker`
   - **Dockerfile Path**: `./Dockerfile.prod`
   - **Instance Type**: `Starter` (free) or `Standard` (production)

### Option 3: Native Python (No Docker)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New" → "Web Service"**
3. Connect your GitHub repo
4. Settings:
   - **Name**: `x402-insurance`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements-prod.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 server:app`

## Environment Variables (Required)

Set these in the Render Dashboard under **"Environment"**:

### Critical Secrets (Never commit these!)
```bash
BACKEND_WALLET_PRIVATE_KEY=0x...  # Your wallet private key
BACKEND_WALLET_ADDRESS=0x...      # Your wallet address
```

### Optional Monitoring
```bash
SENTRY_DSN=https://...            # Enable error tracking
SENTRY_ENVIRONMENT=production
```

All other environment variables are pre-configured in `render.yaml`.

## Speed Optimization

### 1. Use Pre-Built Docker Image (Fastest)

Instead of Render building from scratch (5-8 min), use pre-built images (30-60 sec):

1. Build locally or via GitHub Actions
2. Push to Docker Hub
3. Configure Render to pull the image

```bash
# In Render, use "Deploy an existing image"
docker.io/yourusername/x402insurance:latest
```

### 2. Use Production Dockerfile

Uses `Dockerfile.prod` which only installs production dependencies:
- Skips test packages (pytest, black, ruff)
- Saves 2-3 minutes per build

### 3. Enable Build Cache

Render caches Docker layers. Ensure:
- `requirements-prod.txt` is copied before application code
- Layers are ordered from least to most frequently changed

### 4. Upgrade to Paid Plan (Optional)

- Free tier: Slower build machines (~5-8 minutes)
- Starter plan ($7/mo): Faster builds (~3-5 minutes)
- Standard plan ($25/mo): Much faster (~2-3 minutes)

## Typical Build Times

| Component | Time | Notes |
|-----------|------|-------|
| Git clone | 10-30s | Depends on repo size |
| Docker layer cache | 0-60s | First build: slow, subsequent: fast |
| Install dependencies | 60-120s | Production deps only |
| Copy zkEngine (11MB) | 10-20s | Binary file |
| Copy application | 5-10s | Python files |
| **Total (first build)** | **4-6 min** | Free tier |
| **Total (cached)** | **2-3 min** | With layer cache |

## Troubleshooting

### Build taking > 10 minutes?

1. **Check Docker layer caching**
   ```bash
   # In Render logs, look for:
   # "Using cache" = good (fast)
   # "Downloading" = bad (slow)
   ```

2. **Verify using production Dockerfile**
   - Should see: `Using ./Dockerfile.prod`

3. **Check for large files**
   ```bash
   find . -type f -size +1M -not -path "./venv/*" -not -path "./.git/*"
   ```

### Deployment stuck at "Installing dependencies"?

This usually means:
- Network issues downloading from PyPI
- Render's build machine is under load

**Solution**: Cancel and retry.

### App crashes after deployment?

Check logs for:
```bash
# Missing environment variables
Error: BACKEND_WALLET_PRIVATE_KEY not set

# Solution: Add in Render Dashboard → Environment
```

## Security Checklist

Before going live:

- [ ] Set `BACKEND_WALLET_PRIVATE_KEY` in Render Dashboard (not in code)
- [ ] Set `BACKEND_WALLET_ADDRESS` in Render Dashboard
- [ ] Change `ALLOWED_ORIGINS` from `*` to your domain
- [ ] Enable Sentry monitoring (optional but recommended)
- [ ] Add persistent disk for data storage
- [ ] Review rate limits in `render.yaml`

## Monitoring

After deployment:

1. **Health Check**: `https://your-app.onrender.com/health`
2. **Dashboard**: `https://your-app.onrender.com/`
3. **API Docs**: `https://your-app.onrender.com/docs`
4. **Metrics**: Render Dashboard → Metrics tab

## Cost Estimate

| Plan | Price | Build Time | Uptime |
|------|-------|------------|--------|
| Free | $0 | 5-8 min | Spins down after 15min idle |
| Starter | $7/mo | 3-5 min | Always on |
| Standard | $25/mo | 2-3 min | Always on + more resources |

**Recommendation**: Start with **Starter** for production ($7/mo).

## Quick Commands

```bash
# Test Dockerfile locally (to verify it works before deploying)
docker build -f Dockerfile.prod -t x402-insurance .
docker run -p 8000:8000 --env-file .env x402-insurance

# Check build size (smaller = faster upload)
docker images x402-insurance
```

## Debug Slow Builds

### Check if a package is slow to install:
```bash
# Run locally to time each package
for pkg in $(grep -E "^[a-z]" requirements-prod.txt); do
  echo "Installing $pkg..."
  time pip install --no-cache-dir $pkg
done
```

### Most common slow packages:
- `web3` - 30-40s (lots of deps)
- `cryptography` - 20-30s (if compiled)

## Expected Build Times by Plan

| Plan | First Build | Cached Build | Notes |
|------|-------------|--------------|-------|
| Free | 5-8 min | 3-5 min | Slower CPU, no persistent cache |
| Starter ($7/mo) | 3-5 min | 1-2 min | Better CPU, persistent cache |
| Standard ($25/mo) | 2-3 min | 30-60s | Fast CPU, persistent cache |

## Support

- Render issues: https://render.com/docs
- x402 Insurance issues: https://github.com/hshadab/x402insurance/issues
