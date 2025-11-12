# Simple Render Deployment (No Docker!)

**Deploy in 3-5 minutes with just one click.**

## What Changed?

Removed all the Docker complexity. Now using Render's native Python runtime:
- ✅ No Docker
- ✅ No Docker Hub
- ✅ No GitHub Actions
- ✅ Just push and deploy

## Quick Deploy (5 minutes)

### Step 1: Push to GitHub
```bash
git push origin main
```

### Step 2: Deploy on Render

**Option A: Blueprint (One-Click)**
1. Go to: https://dashboard.render.com/select-repo
2. Select your repo: `hshadab/x402insurance`
3. Render detects `render.yaml` automatically
4. Click **"Apply"**
5. Done! ✅

**Option B: Manual Setup**
1. Go to: https://dashboard.render.com
2. Click **"New" → "Web Service"**
3. Connect GitHub repo: `hshadab/x402insurance`
4. Settings:
   - **Name**: `x402-insurance`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements-prod.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 server:app`
   - **Plan**: `Starter` (free tier works)

5. **Environment Variables** (click "Add" for these):
   ```
   BACKEND_WALLET_PRIVATE_KEY=0x22af9bb0c38c6a666a13f51155720cc3c1af64dfd69f0aeb99cb4e7cd4a0d165
   BACKEND_WALLET_ADDRESS=0xf36B80afFb2e41418874FfA56B069f1Fe671FC35
   ```

6. Click **"Create Web Service"**

### Step 3: Wait for Build
Build time: **3-5 minutes** (normal for installing Python packages)

### Step 4: Access Your App
Render gives you a URL: `https://x402-insurance.onrender.com`

---

## Build Time Breakdown

| Step | Time | Why |
|------|------|-----|
| Install Python deps | 2-3 min | Installing web3 + dependencies |
| Copy files | 30 sec | Including 11MB zkEngine binary |
| Start server | 10 sec | Gunicorn startup |
| **Total** | **3-5 min** | **This is normal!** |

**The bottleneck**: Installing `web3` and its 30+ dependencies. This is unavoidable.

---

## Why It Takes 3-5 Minutes

The `web3` package requires:
- eth-account
- eth-abi
- eth-utils
- cytoolz
- cryptography
- ... 25+ more packages

**This is the same whether you use Docker or not.**

Render's free tier has slower build machines. Options:
- **Accept 3-5 min builds** (normal for prototypes)
- **Upgrade to Starter ($7/mo)** → 2-3 min builds
- **Remove blockchain features** (not realistic)

---

## Updating Your App

Just push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render auto-deploys in 3-5 minutes. That's it!

---

## Troubleshooting

**Build fails with "No module named X":**
- Make sure `requirements-prod.txt` has all dependencies
- Check build logs in Render dashboard

**App crashes on start:**
- Check environment variables are set (wallet keys)
- Check logs: Render Dashboard → Logs tab

**zkEngine not found:**
- It's included in your repo
- Render copies everything from GitHub

---

## Cost

| Plan | Cost | Build Time | Features |
|------|------|------------|----------|
| Free | $0 | 5-7 min | Spins down after 15 min idle |
| Starter | $7/mo | 3-5 min | Always on, faster CPU |

**Recommendation**: Start with **free tier** for prototypes.

---

## That's It!

No Docker. No Docker Hub. No GitHub Actions.
Just push and wait 3-5 minutes.

**Simple. ✅**
