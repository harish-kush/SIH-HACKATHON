#!/usr/bin/env python3
"""
ML Model Training Script for Student Dropout Prediction

This script trains an XGBoost model to predict student dropout risk
using academic performance and demographic data.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_training_data(data_path="./sample-data/training_data.csv"):
    """Load and prepare training data"""
    try:
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} training samples")
        return df
    except FileNotFoundError:
        print(f"Training data not found at {data_path}")
        print("Please run the sample data generator first:")
        print("python sample-data/generate_sample_data.py")
        return None

def prepare_features(df):
    """Prepare features for model training"""
    # Define feature columns
    feature_columns = [
        'attendance_percentage', 'avg_assignment_score', 'avg_semester_marks',
        'engagement_score', 'library_hours_per_week', 'extracurricular_participation',
        'disciplinary_issues', 'trend_improving', 'trend_declining', 'has_mentor',
        'branch_cse', 'branch_ece', 'branch_eee', 'branch_mech', 'branch_civil', 'branch_it',
        'year_1', 'year_2', 'year_3', 'year_4'
    ]
    
    # Create branch dummy variables
    branch_dummies = pd.get_dummies(df['branch'], prefix='branch')
    year_dummies = pd.get_dummies(df['year'], prefix='year')
    
    # Combine features
    features_df = df[['attendance_percentage', 'avg_assignment_score', 'avg_semester_marks',
                     'engagement_score', 'library_hours_per_week', 'extracurricular_participation',
                     'disciplinary_issues', 'trend_improving', 'trend_declining', 'has_mentor']].copy()
    
    # Add dummy variables
    for col in ['branch_cse', 'branch_ece', 'branch_eee', 'branch_mech', 'branch_civil', 'branch_it']:
        features_df[col] = 0
    
    for col in ['year_1', 'year_2', 'year_3', 'year_4']:
        features_df[col] = 0
    
    # Set appropriate dummy variables
    for idx, row in df.iterrows():
        branch_col = f"branch_{row['branch'].lower().replace(' ', '_')}"
        if branch_col in features_df.columns:
            features_df.loc[idx, branch_col] = 1
        
        year_col = f"year_{row['year']}"
        if year_col in features_df.columns:
            features_df.loc[idx, year_col] = 1
    
    # Ensure all feature columns exist
    for col in feature_columns:
        if col not in features_df.columns:
            features_df[col] = 0
    
    return features_df[feature_columns]

def train_model(X, y):
    """Train XGBoost model with hyperparameter tuning"""
    print("Training XGBoost model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train XGBoost model
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    # Fit model
    model.fit(
        X_train_scaled, y_train,
        eval_set=[(X_test_scaled, y_test)],
        verbose=False
    )
    
    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    print("\n=== Model Performance ===")
    print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
    print(f"\nCross-validation AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n=== Top 10 Feature Importances ===")
    print(feature_importance.head(10))
    
    return model, scaler, feature_importance

def create_shap_explainer(model, X_sample):
    """Create SHAP explainer for model interpretability"""
    print("Creating SHAP explainer...")
    
    # Use a sample of data for SHAP explainer (for performance)
    sample_size = min(100, len(X_sample))
    X_sample_small = X_sample.sample(n=sample_size, random_state=42)
    
    explainer = shap.TreeExplainer(model)
    
    print(f"SHAP explainer created with {sample_size} background samples")
    return explainer

def save_model(model, scaler, feature_names, explainer, model_dir="./models"):
    """Save trained model and components"""
    os.makedirs(model_dir, exist_ok=True)
    
    # Save model and preprocessors
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'version': '1.0.0',
        'trained_at': datetime.utcnow()
    }
    
    model_path = os.path.join(model_dir, 'dropout_model.joblib')
    explainer_path = os.path.join(model_dir, 'shap_explainer.joblib')
    
    joblib.dump(model_data, model_path)
    joblib.dump(explainer, explainer_path)
    
    print(f"Model saved to {model_path}")
    print(f"SHAP explainer saved to {explainer_path}")

def plot_feature_importance(feature_importance, save_path="./models/feature_importance.png"):
    """Plot and save feature importance"""
    plt.figure(figsize=(10, 8))
    sns.barplot(data=feature_importance.head(15), x='importance', y='feature')
    plt.title('Top 15 Feature Importances - Dropout Prediction Model')
    plt.xlabel('Feature Importance')
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Feature importance plot saved to {save_path}")

def main():
    """Main training pipeline"""
    print("=== Student Dropout Prediction Model Training ===")
    print(f"Started at: {datetime.now()}")
    
    # Load data
    df = load_training_data()
    if df is None:
        return
    
    # Prepare features
    print("\nPreparing features...")
    X = prepare_features(df)
    y = df['dropout']
    
    print(f"Features shape: {X.shape}")
    print(f"Target distribution: {y.value_counts().to_dict()}")
    
    # Train model
    model, scaler, feature_importance = train_model(X, y)
    
    # Create SHAP explainer
    explainer = create_shap_explainer(model, X)
    
    # Save model
    save_model(model, scaler, list(X.columns), explainer)
    
    # Plot feature importance
    plot_feature_importance(feature_importance)
    
    print(f"\n=== Training completed at: {datetime.now()} ===")
    print("Model is ready for predictions!")

if __name__ == "__main__":
    main()
