#!/bin/bash

# Student Dropout Prediction Platform - Demo Script
# This script sets up the complete platform with sample data

set -e

echo "🚀 Student Dropout Prediction Platform - Demo Setup"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your email credentials for notifications."
fi

# Generate sample data
echo "📊 Generating sample data..."
cd sample-data
python generate_sample_data.py
cd ..

# Train ML model
echo "🤖 Training ML model..."
cd ml
python train_model.py
cd ..

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose down --volumes
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB is running"
else
    echo "❌ MongoDB failed to start"
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "❌ Backend API failed to start"
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend failed to start"
fi

echo ""
echo "🎉 Demo setup completed successfully!"
echo ""
echo "📱 Access the platform:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔐 Demo Credentials:"
echo "   Admin: admin@example.com / password123"
echo "   Mentor: mentor@example.com / password123"
echo "   Student: student@example.com / password123"
echo ""
echo "📚 Features to explore:"
echo "   • Student risk prediction with SHAP explanations"
echo "   • Real-time alerts and mentor notifications"
echo "   • Role-based dashboards (Student/Mentor/Admin)"
echo "   • 30-day risk timeline tracking"
echo "   • Performance analytics and insights"
echo ""
echo "🛠️  Useful commands:"
echo "   Stop services: docker-compose down"
echo "   View logs: docker-compose logs -f"
echo "   Restart: docker-compose restart"
echo ""
echo "Happy exploring! 🎓"
