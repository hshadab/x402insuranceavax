# Render.com Speed Optimization Tips

## Current Status
Your repo: **11MB in git** (good!)
zkEngine binary: **11MB** (pre-compiled, no rebuild needed ✓)
Production deps: **10 packages** (minimal ✓)

## ⚡ Quick Fixes

### 1. **Use Dockerfile.render** ✅ (Done)
Updated `render.yaml` to use the ultra-optimized single-stage build:
- No multi-stage overhead
- Pre-downloads binary wheels when available
- Aggressive pip caching
- Pinned Python version for cache stability

### 2. **Check What's Actually Slow**

In Render dashboard, look at the build logs and time each step:

```
Step 1: Cloning repository...           [Expected: 10-30s]
Step 2: Pulling python:3.11.6-slim...   [Expected: 20-60s, cached: 5s]
Step 3: Installing dependencies...      [Expected: 60-120s]
Step 4: Copying files...                [Expected: 10-20s]
Step 5: Starting service...             [Expected: 5-10s]
```

**Total expected: 3-5 minutes (first build), 2-3 minutes (cached)**

### 3. **If Still Slow > 5 minutes**

The bottleneck is likely **installing Python dependencies**. Here's why:

**Heavy packages in web3:**
- `web3==6.11.0` pulls ~30 dependencies
- `eth-account` includes cryptography libs
- `httpx` includes SSL/TLS deps

**Solutions:**

#### Option A: Use pre-built Docker image (FASTEST)
Instead of building on every deploy, use a pre-built image:

1. Build locally and push to Docker Hub:
```bash
docker build -f Dockerfile.render -t yourusername/x402-insurance:latest .
docker push yourusername/x402-insurance:latest
```

2. In Render, use "Docker Image" deploy method instead of repo

**Build time: 10-30 seconds** (just pulls image)

#### Option B: Use Render's Docker cache (Paid tier)
- Upgrade to Starter plan ($7/mo)
- Enables persistent build cache
- 2-3x faster builds

#### Option C: Simplify dependencies further
Remove optional features:
```bash
# In requirements-prod.txt, remove:
sentry-sdk[flask]==1.38.0  # Monitoring (optional)
flask-limiter==3.5.0        # Rate limiting (optional)
```

### 4. **Verify Binary is Not Being Rebuilt**

Check Render logs for these lines:

❌ BAD (rebuilding):
```
gcc -c ...
building wheel for ...
```

✅ GOOD (just copying):
```
COPY zkengine/ zkengine/
```

If you see gcc/building, you're compiling Python packages. Fix:
```bash
pip install --prefer-binary ...
```

### 5. **Check Render Region**
- Oregon (us-west): Fast for West Coast
- Ohio (us-east): Fast for East Coast
- If you're far from the region, builds will be slower

Change in `render.yaml`:
```yaml
region: ohio  # or oregon
```

## 🔍 Debug Slow Builds

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
- `psycopg2-binary` - 15-25s (already removed ✓)

### Pre-install wheels locally:
```bash
# Download all wheels locally
pip download -r requirements-prod.txt -d wheels/

# Then in Dockerfile:
COPY wheels/ wheels/
RUN pip install --no-index --find-links=wheels/ -r requirements-prod.txt
```

## 📊 Expected Build Times by Plan

| Plan | First Build | Cached Build | Notes |
|------|-------------|--------------|-------|
| Free | 5-8 min | 3-5 min | Slower CPU, no persistent cache |
| Starter ($7/mo) | 3-5 min | 1-2 min | Better CPU, persistent cache |
| Standard ($25/mo) | 2-3 min | 30-60s | Fast CPU, persistent cache |

## 🆘 If Still Super Slow (>10 min)

1. **Check Render Status**: https://status.render.com
   - Might be platform-wide issue

2. **Contact Render Support**:
   - Include build ID
   - Ask if build server is slow

3. **Try Different Deploy Method**:
   - Instead of Docker, use native Python runtime
   - Might be faster for simple apps

4. **Use Alternative Platform**:
   - Fly.io: Often faster builds
   - Railway: Better free tier performance
   - Heroku: Well-optimized build pipeline

## ✅ Current Optimization Status

- [x] Minimal production dependencies (10 packages)
- [x] Single-stage Dockerfile (no multi-stage overhead)
- [x] Optimized layer caching (requirements before code)
- [x] Pre-compiled binary (no zkEngine rebuild)
- [x] Pinned Python version (better cache hits)
- [x] Prefer binary wheels (avoid compilation)
- [x] Removed test dependencies (pytest, black, ruff)
- [x] Removed psycopg2-binary (not needed)

Your setup is **already highly optimized**. If it's still slow, it's likely Render's infrastructure.

## 💡 Recommended Next Step

**If current build is still > 5 minutes:**
1. Check the build logs in Render dashboard
2. Find which step is taking the longest
3. Let me know what you see and I can optimize that specific step

**Example slow steps and fixes:**
- "Pulling python:3.11.6" taking 3+ min → Render's Docker registry is slow
- "Installing dependencies" taking 5+ min → Upgrade to paid plan or use pre-built image
- "Cloning repository" taking 2+ min → GitHub/Render connection issue
