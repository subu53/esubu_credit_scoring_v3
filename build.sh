#!/bin/bash
# Render build script

echo "🚀 Starting Render deployment for Esubu Credit Scoring System..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify model file exists
if [ -f "lightgbm_model.pkl" ]; then
    echo "✅ Model file found"
else
    echo "❌ Model file missing - this may cause deployment issues"
fi

# Test import of main modules
echo "🧪 Testing imports..."
python -c "import streamlit, pandas, numpy, lightgbm, joblib; print('✅ All imports successful')"

echo "🎉 Build completed successfully!"
