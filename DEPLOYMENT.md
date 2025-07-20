# 🚀 Deployment Guide - Esubu AI Credit Scoring System

This guide provides step-by-step instructions for deploying the Esubu AI Credit Scoring System to various platforms.

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- All required dependencies (see `requirements.txt`)

## 🔧 Production Setup

### 1. Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your production values:
   ```bash
   # IMPORTANT: Change these values in production!
   SECRET_KEY=your-super-secret-production-key-here
   DEFAULT_ADMIN_USERNAME=your_admin_username
   DEFAULT_ADMIN_PASSWORD=your_secure_admin_password
   
   # Optional configurations
   DB_FILE=production_users.db
   LOG_LEVEL=INFO
   APP_TITLE=🏦 Your Company Credit Scoring System
   ```

### 2. Security Checklist

- ✅ Change default admin credentials
- ✅ Use strong SECRET_KEY (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- ✅ Enable HTTPS in production
- ✅ Set appropriate file permissions
- ✅ Regular security updates

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Production-ready deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set environment variables in Streamlit Cloud dashboard
   - Deploy!

3. **Environment Variables in Streamlit Cloud:**
   ```
   SECRET_KEY = your-production-secret-key
   DEFAULT_ADMIN_USERNAME = your_admin
   DEFAULT_ADMIN_PASSWORD = your_secure_password
   ```

### Option 2: Heroku

1. **Install Heroku CLI and login:**
   ```bash
   heroku login
   ```

2. **Create Heroku app:**
   ```bash
   heroku create your-credit-scoring-app
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-production-secret-key
   heroku config:set DEFAULT_ADMIN_USERNAME=your_admin
   heroku config:set DEFAULT_ADMIN_PASSWORD=your_secure_password
   ```

4. **Create Procfile:**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

5. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Option 3: Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Set environment variables in Railway dashboard**

### Option 4: Google Cloud Run

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8080
   CMD streamlit run app.py --server.port=8080 --server.address=0.0.0.0
   ```

2. **Build and deploy:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/credit-scoring
   gcloud run deploy --image gcr.io/PROJECT-ID/credit-scoring --platform managed
   ```

## 🔍 Local Development

1. **Clone repository:**
   ```bash
   git clone https://github.com/subu53/esubu_credit_scoring_v2.git
   cd esubu_credit_scoring_v2
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

4. **Run application:**
   ```bash
   streamlit run app.py
   ```

## 📊 Application Features

### User Roles
- **Admin**: Full access to user management and loan applications
- **Officer**: Access to loan applications and decision overrides

### Default Credentials
- Username: `admin` (configurable via environment)
- Password: `admin123` (MUST be changed in production)

### Security Features
- ✅ Password hashing with bcrypt
- ✅ Role-based access control
- ✅ Session management
- ✅ Audit logging
- ✅ Input validation
- ✅ Environment-based configuration

## 🛠 Maintenance

### Database Backup
```bash
# Backup SQLite database
cp users.db users_backup_$(date +%Y%m%d).db
```

### Log Monitoring
- Check `app.log` for application logs
- Monitor user activities and system errors
- Set up log rotation for production

### Updates
```bash
git pull origin main
pip install -r requirements.txt --upgrade
streamlit run app.py
```

## 🆘 Troubleshooting

### Common Issues

1. **Model files not found:**
   - Ensure `credit_scoring_stacked_model.pkl` and `preprocessing_pipeline.pkl` are in the app directory

2. **Database errors:**
   - Check file permissions
   - Verify SQLite installation
   - Check disk space

3. **Import errors:**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

4. **Authentication issues:**
   - Verify environment variables are set
   - Check password hashing configuration

### Support
- Check application logs in `app.log`
- Review Streamlit logs for deployment issues
- Ensure all environment variables are properly set

## 📈 Performance Optimization

- Use caching for model loading (`@st.cache_resource`)
- Optimize database queries
- Monitor memory usage with large datasets
- Consider using PostgreSQL for high-traffic deployments

## 🔒 Security Best Practices

1. **Never commit sensitive data to version control**
2. **Use environment variables for all secrets**
3. **Enable HTTPS in production**
4. **Regular security updates**
5. **Monitor access logs**
6. **Implement rate limiting if needed**

---

**Ready to deploy!** 🎉 Your credit scoring application is production-ready with enhanced security, logging, and configuration management.
