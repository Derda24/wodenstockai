# 🚀 WODEN Stock AI - Production Deployment Guide

## 🎯 **Deployment Strategy: Vercel + Cloudflare**

### **Frontend (Next.js) → Vercel**
### **Backend (FastAPI) → Railway/Render**
### **Domain → Cloudflare → Vercel**

---

## 📋 **Step 1: Prepare Frontend for Production**

### **1.1 Build and Test Locally**
```bash
cd frontend
npm run build
npm start
```

### **1.2 Deploy to Vercel**

#### **Option A: Vercel CLI (Recommended)**
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod
```

#### **Option B: Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com)
2. Create account/Login
3. Click "New Project"
4. Import your GitHub repository
5. Configure build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

---

## 🔧 **Step 2: Deploy Backend to Production**

### **2.1 Railway (Recommended)**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Deploy backend
cd backend
railway init
railway up
```

### **2.2 Alternative: Render**
1. Go to [render.com](https://render.com)
2. Create account/Login
3. Click "New Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `woden-stock-ai-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 🌐 **Step 3: Connect Cloudflare Domain to Vercel**

### **3.1 Get Vercel Domain**
After deployment, Vercel will give you a URL like:
`https://your-project.vercel.app`

### **3.2 Configure Cloudflare DNS**
1. Login to [Cloudflare](https://cloudflare.com)
2. Select your `wodenstockai.com` domain
3. Go to **DNS** tab
4. Add these records:

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| CNAME | `@` | `your-project.vercel.app` | Proxied ✅ |
| CNAME | `www` | `your-project.vercel.app` | Proxied ✅ |

### **3.3 Configure Vercel Domain**
1. In Vercel dashboard, go to your project
2. Click **Settings** → **Domains**
3. Add `wodenstockai.com`
4. Add `www.wodenstockai.com`
5. Vercel will provide DNS records to verify

---

## ⚙️ **Step 4: Environment Variables**

### **4.1 Vercel Environment Variables**
In Vercel dashboard → Settings → Environment Variables:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NEXT_PUBLIC_APP_NAME=WODEN Stock AI
NEXT_PUBLIC_APP_VERSION=2.0.0
```

### **4.2 Backend Environment Variables**
In Railway/Render dashboard:

```env
CORS_ORIGINS=https://wodenstockai.com,https://www.wodenstockai.com
ENVIRONMENT=production
```

---

## 🔒 **Step 5: Security & SSL**

### **5.1 Vercel (Automatic)**
- ✅ HTTPS automatically enabled
- ✅ SSL certificates managed
- ✅ Global CDN included

### **5.2 Cloudflare (Additional Security)**
- ✅ DDoS protection
- ✅ Web Application Firewall
- ✅ Rate limiting
- ✅ Bot protection

---

## 📱 **Step 6: Test Production**

### **6.1 Frontend Tests**
- [ ] Logo displays correctly
- [ ] Login works
- [ ] All tabs function
- [ ] Stock management works
- [ ] Excel upload works
- [ ] AI analysis works
- [ ] AI recommendations work

### **6.2 Backend Tests**
- [ ] API endpoints respond
- [ ] Stock data loads
- [ ] Excel processing works
- **6.3 Domain Tests**
- [ ] `wodenstockai.com` loads
- [ ] `www.wodenstockai.com` redirects
- [ ] HTTPS works
- [ ] Logo appears in browser tab

---

## 🚨 **Troubleshooting**

### **Common Issues:**
1. **Build Failures**: Check Node.js version (18+ required)
2. **API Errors**: Verify backend URL in environment variables
3. **Domain Issues**: Check Cloudflare DNS configuration
4. **Logo Not Loading**: Verify image paths in production

### **Support:**
- Vercel: [vercel.com/support](https://vercel.com/support)
- Cloudflare: [cloudflare.com/support](https://cloudflare.com/support)
- Railway: [railway.app/support](https://railway.app/support)

---

## 🎉 **Success Checklist**

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway/Render
- [ ] Domain connected to Vercel
- [ ] Environment variables configured
- [ ] SSL certificates active
- [ ] All functionality tested
- [ ] Logo displays everywhere
- [ ] Ready for production use

---

## 🌟 **Your WODEN Stock AI will be live at:**
**https://wodenstockai.com**

**Professional, fast, and ready to manage your stock operations!** 🚀
