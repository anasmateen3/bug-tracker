# Bug Tracker Deployment Guide

## Prerequisites
1. MongoDB Atlas account (free tier available)
2. Vercel account (for frontend)
3. Railway/Render account (for backend)

## Step 1: Setup MongoDB Atlas

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a new cluster (free tier M0)
3. Create a database user:
   - Database Access → Add New Database User
   - Save username and password
4. Whitelist IP addresses:
   - Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)
5. Get connection string:
   - Clusters → Connect → Connect your application
   - Copy the connection string
   - Replace `<password>` with your database user password

## Step 2: Deploy Backend (Railway)

### Option A: Railway (Recommended)

1. Go to [Railway](https://railway.app)
2. New Project → Deploy from GitHub repo
3. Select your repository
4. Configure:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

5. Add Environment Variables:
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net
   DB_NAME=bugtracker_production
   JWT_SECRET=your-generated-secret-key
   CORS_ORIGINS=https://your-app.vercel.app
   ```

6. Generate domain or use Railway's provided URL
7. Copy the backend URL (e.g., `https://your-app.up.railway.app`)

### Option B: Render

1. Go to [Render](https://render.com)
2. New → Web Service
3. Connect your repository
4. Configure:
   - **Name**: bugtracker-backend
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

5. Add Environment Variables (same as Railway)
6. Copy the backend URL

## Step 3: Deploy Frontend (Vercel)

1. Go to [Vercel](https://vercel.com)
2. Import Git Repository
3. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build`
   - **Output Directory**: `build`
   - **Install Command**: `yarn install`

4. Add Environment Variable:
   ```
   REACT_APP_BACKEND_URL=https://your-backend.railway.app
   ```
   ⚠️ **Important**: Use your Railway/Render backend URL from Step 2

5. Deploy!

## Step 4: Update Backend CORS

1. After Vercel deployment, copy your frontend URL (e.g., `https://your-app.vercel.app`)
2. Go back to Railway/Render
3. Update `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://your-app.vercel.app
   ```
4. Redeploy backend

## Step 5: Test Your Application

1. Visit your Vercel URL
2. Register a new account
3. Create a project
4. Create tickets and test the Kanban board

## Environment Variables Reference

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

### Backend (.env)
```bash
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net
DB_NAME=bugtracker_production
CORS_ORIGINS=https://your-frontend.vercel.app
JWT_SECRET=your-super-secret-jwt-key
```

## Generate JWT Secret

Run this command to generate a secure secret:
```bash
openssl rand -hex 32
```

Or use this online: https://generate-random.org/api-token-generator

## Troubleshooting

### Frontend can't connect to backend
- Verify `REACT_APP_BACKEND_URL` in Vercel environment variables
- Check backend is running on Railway/Render
- Verify CORS_ORIGINS includes your Vercel domain

### Database connection failed
- Check MongoDB Atlas IP whitelist includes 0.0.0.0/0
- Verify MONGO_URL connection string is correct
- Ensure database user has read/write permissions

### JWT Authentication errors
- Verify JWT_SECRET is set and matches between deployments
- Check JWT_SECRET is the same string across all backend instances

## Custom Domain (Optional)

### Vercel
1. Settings → Domains → Add Domain
2. Follow DNS configuration instructions

### Railway/Render
1. Settings → Custom Domain
2. Add your domain and configure DNS

## Monitoring

- **Frontend**: Vercel Dashboard → Analytics
- **Backend**: Railway/Render Dashboard → Logs
- **Database**: MongoDB Atlas → Metrics

## Cost Estimate

- MongoDB Atlas: **Free** (M0 tier, 512MB storage)
- Railway: **$5/month** (includes $5 credit)
- Render: **Free** (with limitations) or **$7/month**
- Vercel: **Free** (hobby plan)

**Total**: $0-5/month for hobby projects

---

## Quick Deploy Commands

```bash
# Clone repository
git clone <your-repo-url>
cd bugtracker

# Setup backend locally
cd backend
cp .env.example .env
# Edit .env with your values
pip install -r requirements.txt
uvicorn server:app --reload

# Setup frontend locally
cd ../frontend
cp .env.example .env.local
# Edit .env.local with your backend URL
yarn install
yarn start
```

## Support

For issues or questions:
- Check the logs in Railway/Render dashboard
- Check browser console for frontend errors
- Verify all environment variables are set correctly
