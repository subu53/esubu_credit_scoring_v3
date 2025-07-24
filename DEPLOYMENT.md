# 🚀 Render Deployment Guide

## Quick Deploy to Render

### 1. Prerequisites
- GitHub repository with your code
- Render account (free tier available)
- Model file (`lightgbm_model.pkl`) in your repository

### 2. Render Configuration
- **Service Type**: Web Service
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- **Environment**: Python 3.9

### 3. One-Click Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### 4. Manual Deployment Steps

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   ```
   Name: esubu-credit-scoring
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **Environment Variables** (if needed)
   ```
   PYTHON_VERSION=3.9
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment

### 5. Expected Issues & Solutions

#### Common Deployment Errors:
1. **Model file not found**
   - Ensure `lightgbm_model.pkl` is in repository
   - Check file size limits

2. **Memory issues**
   - Upgrade to paid plan for larger models
   - Optimize model size

3. **Port binding issues**
   - Ensure using `--server.port=$PORT`

4. **Package version conflicts**
   - Pin specific versions in requirements.txt

### 6. Health Check
Once deployed, your app will be available at:
```
https://esubu-credit-scoring.onrender.com
```

### 7. Monitoring
- Check Render logs for errors
- Monitor memory usage
- Set up uptime monitoring
