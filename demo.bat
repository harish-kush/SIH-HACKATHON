@echo off
REM Student Dropout Prediction Platform - Demo Script for Windows
REM This script sets up the complete platform with sample data

echo 🚀 Student Dropout Prediction Platform - Demo Setup
echo ==================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✅ Created .env file. Please update it with your email credentials for notifications.
)

REM Generate sample data
echo 📊 Generating sample data...
cd sample-data
python generate_sample_data.py
if %errorlevel% neq 0 (
    echo ❌ Failed to generate sample data. Make sure Python is installed.
    pause
    exit /b 1
)
cd ..

REM Train ML model
echo 🤖 Training ML model...
cd ml
python train_model.py
if %errorlevel% neq 0 (
    echo ❌ Failed to train ML model. Check Python dependencies.
    pause
    exit /b 1
)
cd ..

REM Start services with Docker Compose
echo 🐳 Starting services with Docker Compose...
docker-compose down --volumes
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

echo 🔍 Checking service health...

REM Check if services are accessible
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is running
) else (
    echo ❌ Backend API may not be ready yet
)

curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is running
) else (
    echo ❌ Frontend may not be ready yet
)

echo.
echo 🎉 Demo setup completed successfully!
echo.
echo 📱 Access the platform:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 🔐 Demo Credentials:
echo    Admin: admin@example.com / password123
echo    Mentor: mentor@example.com / password123
echo    Student: student@example.com / password123
echo.
echo 📚 Features to explore:
echo    • Student risk prediction with SHAP explanations
echo    • Real-time alerts and mentor notifications
echo    • Role-based dashboards (Student/Mentor/Admin)
echo    • 30-day risk timeline tracking
echo    • Performance analytics and insights
echo.
echo 🛠️  Useful commands:
echo    Stop services: docker-compose down
echo    View logs: docker-compose logs -f
echo    Restart: docker-compose restart
echo.
echo Happy exploring! 🎓
pause
