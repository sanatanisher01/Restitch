# ReStitch - Render Deployment Guide

## Quick Deploy to Render

### 1. Prepare Repository
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
```

### 2. Push to GitHub (Private Repo)
1. Create private repository on GitHub
2. Push your code:
```bash
git remote add origin https://github.com/yourusername/restitch.git
git push -u origin main
```

### 3. Deploy on Render
1. Go to [render.com](https://render.com)
2. Connect your GitHub account
3. Click "New +" → "Web Service"
4. Select your repository
5. Configure:
   - **Name**: restitch
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn restitch:app`

### 4. Add Database
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Name: `restitch-db`
3. Copy the database URL

### 5. Environment Variables
Add these in Render dashboard:
```
SECRET_KEY=your-random-secret-key
DATABASE_URL=your-postgres-url-from-step-4
FLASK_ENV=production
```

### 6. Initialize Database
After first deployment, run in Render shell:
```bash
flask db upgrade
python seed.py
```

## Login Credentials
- **Admin**: admin@restitch.com / admin123
- **Designer**: designer@restitch.com / designer123
- **User**: priya@example.com / password123

## Custom Domain (Optional)
1. Buy domain from Namecheap/GoDaddy
2. In Render → Settings → Custom Domains
3. Add your domain and configure DNS

Your app will be live at: `https://restitch.onrender.com`