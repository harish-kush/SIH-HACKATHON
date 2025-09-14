import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
import xgboost as xgb

from app.core.config import settings
from app.models.prediction import ShapFeature, PredictionResponse
from app.services.performance import performance_service
from app.services.student import student_service


class MLPredictionService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.shap_explainer = None
        self.model_version = "1.0.0"
        self.load_model()
    
    def load_model(self):
        """Load trained model and preprocessors"""
        try:
            if os.path.exists(settings.MODEL_PATH):
                model_data = joblib.load(settings.MODEL_PATH)
                self.model = model_data.get('model')
                self.scaler = model_data.get('scaler')
                self.feature_names = model_data.get('feature_names')
                self.model_version = model_data.get('version', '1.0.0')
                print(f"Loaded model version {self.model_version}")
            
            if os.path.exists(settings.SHAP_EXPLAINER_PATH):
                self.shap_explainer = joblib.load(settings.SHAP_EXPLAINER_PATH)
                print("Loaded SHAP explainer")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    async def predict_dropout_risk(self, student_id: str) -> Optional[PredictionResponse]:
        """Predict dropout risk for a student"""
        if not self.model:
            raise Exception("Model not loaded. Please train the model first.")
        
        # Get student features
        features = await self._get_student_features(student_id)
        if not features:
            return None
        
        # Prepare features for prediction
        feature_array = self._prepare_features(features)
        if feature_array is None:
            return None
        
        # Make prediction
        risk_prob = self.model.predict_proba(feature_array)[0][1]  # Probability of dropout
        risk_score_1_10 = int(np.clip(risk_prob * 10, 1, 10))
        
        # Determine risk bucket
        if risk_score_1_10 <= settings.MODERATE_RISK_THRESHOLD:
            risk_bucket = "low"
        elif risk_score_1_10 < settings.HIGH_RISK_THRESHOLD:
            risk_bucket = "moderate"
        else:
            risk_bucket = "high"
        
        # Get SHAP explanations
        shap_features = self._get_shap_explanations(feature_array, features)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_bucket, shap_features)
        
        # Calculate confidence score
        confidence_score = max(risk_prob, 1 - risk_prob)
        
        return PredictionResponse(
            student_id=student_id,
            risk_score_0_1=risk_prob,
            risk_score_1_10=risk_score_1_10,
            risk_bucket=risk_bucket,
            top_risk_factors=shap_features[:3],  # Top 3 factors
            recommendations=recommendations,
            confidence_score=confidence_score,
            prediction_date=datetime.utcnow()
        )
    
    async def _get_student_features(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get all features for a student"""
        # Get student basic info
        student = await student_service.get_student_by_id(student_id)
        if not student:
            return None
        
        # Get performance features
        performance_features = await performance_service.get_latest_performance_features(student_id)
        
        # Combine all features
        features = {
            # Demographic features
            "branch_cse": 1 if student.branch == "Computer Science Engineering" else 0,
            "branch_ece": 1 if student.branch == "Electronics and Communication Engineering" else 0,
            "branch_eee": 1 if student.branch == "Electrical and Electronics Engineering" else 0,
            "branch_mech": 1 if student.branch == "Mechanical Engineering" else 0,
            "branch_civil": 1 if student.branch == "Civil Engineering" else 0,
            "branch_it": 1 if student.branch == "Information Technology" else 0,
            
            "year_1": 1 if student.year == "1st Year" else 0,
            "year_2": 1 if student.year == "2nd Year" else 0,
            "year_3": 1 if student.year == "3rd Year" else 0,
            "year_4": 1 if student.year == "4th Year" else 0,
            
            "has_mentor": 1 if student.mentor_id else 0,
            
            # Performance features (with defaults)
            "attendance_percentage": performance_features.get("attendance_percentage", 75.0),
            "avg_assignment_score": performance_features.get("avg_assignment_score", 70.0),
            "avg_semester_marks": performance_features.get("avg_semester_marks", 70.0),
            "engagement_score": performance_features.get("engagement_score", 5.0),
            "library_hours_per_week": performance_features.get("library_hours_per_week", 5.0),
            "extracurricular_participation": performance_features.get("extracurricular_participation", 2),
            "disciplinary_issues": performance_features.get("disciplinary_issues", 0),
            "trend_improving": performance_features.get("trend_improving", 0),
            "trend_declining": performance_features.get("trend_declining", 0),
        }
        
        return features
    
    def _prepare_features(self, features: Dict[str, Any]) -> Optional[np.ndarray]:
        """Prepare features for model prediction"""
        if not self.feature_names:
            # Default feature order for new models
            self.feature_names = [
                "attendance_percentage", "avg_assignment_score", "avg_semester_marks",
                "engagement_score", "library_hours_per_week", "extracurricular_participation",
                "disciplinary_issues", "trend_improving", "trend_declining", "has_mentor",
                "branch_cse", "branch_ece", "branch_eee", "branch_mech", "branch_civil", "branch_it",
                "year_1", "year_2", "year_3", "year_4"
            ]
        
        try:
            # Create feature array in correct order
            feature_array = np.array([[features.get(name, 0) for name in self.feature_names]])
            
            # Scale features if scaler is available
            if self.scaler:
                feature_array = self.scaler.transform(feature_array)
            
            return feature_array
        except Exception as e:
            print(f"Error preparing features: {e}")
            return None
    
    def _get_shap_explanations(self, feature_array: np.ndarray, features: Dict[str, Any]) -> List[ShapFeature]:
        """Get SHAP explanations for the prediction"""
        shap_features = []
        
        try:
            if self.shap_explainer and self.feature_names:
                shap_values = self.shap_explainer.shap_values(feature_array)
                
                # Handle different SHAP output formats
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]  # For binary classification, take positive class
                
                # Create SHAP features
                for i, feature_name in enumerate(self.feature_names):
                    shap_value = shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i]
                    
                    shap_features.append(ShapFeature(
                        feature_name=feature_name,
                        feature_value=features.get(feature_name, 0),
                        shap_value=float(shap_value),
                        contribution="positive" if shap_value > 0 else "negative"
                    ))
                
                # Sort by absolute SHAP value (importance)
                shap_features.sort(key=lambda x: abs(x.shap_value), reverse=True)
        
        except Exception as e:
            print(f"Error generating SHAP explanations: {e}")
        
        return shap_features
    
    def _generate_recommendations(self, risk_bucket: str, shap_features: List[ShapFeature]) -> List[str]:
        """Generate recommendations based on risk level and contributing factors"""
        recommendations = []
        
        if risk_bucket == "high":
            recommendations.extend([
                "Immediate intervention required - schedule urgent meeting with student",
                "Contact parents/guardians to discuss student's situation",
                "Consider academic support programs or tutoring",
                "Evaluate personal circumstances that may be affecting performance"
            ])
        elif risk_bucket == "moderate":
            recommendations.extend([
                "Schedule regular check-ins with the student",
                "Monitor academic progress closely",
                "Provide additional academic resources if needed",
                "Encourage participation in support groups"
            ])
        else:
            recommendations.extend([
                "Continue current support level",
                "Maintain regular monitoring",
                "Recognize and encourage good performance"
            ])
        
        # Add specific recommendations based on top risk factors
        for shap_feature in shap_features[:3]:
            if shap_feature.contribution == "positive":  # Contributing to dropout risk
                if "attendance" in shap_feature.feature_name.lower():
                    recommendations.append("Focus on improving attendance - identify barriers to regular attendance")
                elif "assignment" in shap_feature.feature_name.lower():
                    recommendations.append("Provide additional academic support for assignments")
                elif "engagement" in shap_feature.feature_name.lower():
                    recommendations.append("Work on increasing student engagement in class activities")
                elif "library" in shap_feature.feature_name.lower():
                    recommendations.append("Encourage more study time and library usage")
                elif "disciplinary" in shap_feature.feature_name.lower():
                    recommendations.append("Address behavioral issues through counseling")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def train_model(self, training_data: pd.DataFrame, target_column: str = "dropout"):
        """Train the dropout prediction model"""
        try:
            # Prepare features and target
            X = training_data.drop(columns=[target_column, "student_id"], errors="ignore")
            y = training_data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train XGBoost model
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            self.model.fit(X_train_scaled, y_train)
            self.feature_names = list(X.columns)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
            
            print("Model Performance:")
            print(classification_report(y_test, y_pred))
            print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.3f}")
            
            # Create SHAP explainer
            self.shap_explainer = shap.TreeExplainer(self.model)
            
            # Save model
            self._save_model()
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def _save_model(self):
        """Save trained model and preprocessors"""
        try:
            # Create models directory if it doesn't exist
            os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
            
            # Save model and preprocessors
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'version': self.model_version,
                'trained_at': datetime.utcnow()
            }
            
            joblib.dump(model_data, settings.MODEL_PATH)
            joblib.dump(self.shap_explainer, settings.SHAP_EXPLAINER_PATH)
            
            print(f"Model saved to {settings.MODEL_PATH}")
            
        except Exception as e:
            print(f"Error saving model: {e}")


ml_prediction_service = MLPredictionService()
