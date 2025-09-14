# Student Dropout Prediction & Counselling Platform

A production-ready platform that predicts student dropout risk using ML and provides counselling interventions through mentor assignments and automated alerts.

## 🚀 Tech Stack

- **Frontend**: React + JavaScript + Tailwind CSS + Framer Motion
- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas (async driver motor)
- **Email/Alerts**: FastAPI-Mail (SMTP)
- **ML**: scikit-learn + XGBoost + SHAP for explainability
- **Auth**: JWT-based role auth (student/mentor/admin)
- **Deployment**: Docker & docker-compose

## 🎯 Features

### Role-Based Access
- **Student**: View personal risk gauge, 30-day timeline, AI chatbot
- **Mentor**: Manage assigned students, respond to alerts, provide feedback
- **Admin**: Global analytics, mentor reassignment, recovery stats

### Dropout Risk Scoring
- XGBoost model outputs probability → scale 1–10
- 1-3: Low risk
- 4-6: Moderate (show mentor-connect popup)
- 7-10: High (email mentor immediately)

### Smart Interventions
- Mentor SLA: Auto-reassign if no response within 24h
- Time-series tracking: 30-day rolling risk scores
- SHAP explainability: Top 3 contributing factors per prediction

## 🏗️ Project Structure

```
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration, security
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Dashboard pages
│   │   ├── services/       # API calls
│   │   └── utils/          # Utilities
│   ├── package.json
│   └── Dockerfile
├── ml/                     # ML pipeline
│   ├── data/              # Data processing
│   ├── models/            # Model training
│   ├── evaluation/        # Model evaluation
│   └── inference/         # Prediction service
├── sample-data/           # Sample datasets
├── docker-compose.yml
└── demo.sh               # Demo script
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration:
# - MongoDB URI
# - SMTP credentials
# - JWT secret
```

### Run with Docker
```bash
# Start all services
docker-compose up -d

# Train initial model with sample data
./demo.sh
```

### Manual Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

#### ML Pipeline
```bash
cd ml
pip install -r requirements.txt
python train_model.py
```

## 📊 API Endpoints

### Students
- `POST /students/` - Add new student
- `GET /students/{id}` - Get student details
- `GET /students/{id}/timeline` - 30-day risk timeline

### Performance
- `POST /performance/` - Submit daily metrics
- `GET /performance/{student_id}` - Get performance history

### Predictions
- `POST /train` - Trigger model training
- `GET /predict/{student_id}` - Get risk prediction with SHAP features

### Mentoring
- `POST /mentor/assign` - Auto-assign or reassign mentor
- `POST /feedback` - Submit mentor feedback
- `GET /alerts/` - Get active alerts

## 🗄️ Database Schema

### Collections
- **students**: Student profiles and metadata
- **performance**: Daily metrics and academic data
- **alerts**: Risk alerts and mentor assignments
- **feedback**: Mentor interventions and outcomes

## 🤖 ML Pipeline

### Features
- Attendance percentage
- Average assignment scores
- Semester marks
- Engagement metrics
- Academic history
- Demographic factors

### Model
- XGBoost classifier for dropout prediction
- SHAP for feature importance and explainability
- Active learning from mentor feedback

## 🔧 Configuration

Key environment variables:
```
MONGODB_URI=mongodb://localhost:27017/dropout_prediction
JWT_SECRET=your-secret-key
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@domain.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# ML tests
cd ml
python -m pytest tests/
```

## 📈 Monitoring & Analytics

- Student risk distribution
- Intervention success rates
- Mentor response times
- Model performance metrics

## 🚀 Deployment

### Railway/Render
```bash
# Build and deploy
docker build -t dropout-prediction .
# Push to your container registry
```

### Local Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Sample Data

The platform includes:
- Fake data generator for testing
- Sample CSV datasets
- Integration with public datasets:
  - UCI Student Academic Performance Dataset
  - Kaggle Student Dropout & Academic Success

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review sample configurations

---

Built with ❤️ for educational institutions worldwide
