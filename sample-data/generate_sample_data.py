#!/usr/bin/env python3
"""
Sample Data Generator for Student Dropout Prediction System

Generates realistic sample data for students, performance records, and training data
for the ML model.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from faker import Faker
import random

fake = Faker()
np.random.seed(42)
random.seed(42)

# Configuration
NUM_STUDENTS = 1000
NUM_PERFORMANCE_RECORDS_PER_STUDENT = 30  # 30 days of data
DROPOUT_RATE = 0.15  # 15% dropout rate

# Define branches and years
BRANCHES = [
    "Computer Science Engineering",
    "Electronics and Communication Engineering", 
    "Electrical and Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Information Technology"
]

YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year"]

def generate_students():
    """Generate sample student data"""
    students = []
    
    for i in range(NUM_STUDENTS):
        student = {
            'student_id': f"STU{i+1:04d}",
            'name': fake.name(),
            'scholar_id': f"2023{random.randint(1000, 9999)}",
            'email': fake.email(),
            'parent_email': fake.email(),
            'branch': random.choice(BRANCHES),
            'year': random.choice(YEARS),
            'phone': fake.phone_number()[:10],
            'parent_phone': fake.phone_number()[:10],
            'address': fake.address().replace('\n', ', '),
            'has_mentor': random.choice([0, 1]),
            'created_at': fake.date_between(start_date='-2y', end_date='today')
        }
        students.append(student)
    
    return pd.DataFrame(students)

def generate_performance_data(students_df):
    """Generate performance data for students"""
    performance_records = []
    
    for _, student in students_df.iterrows():
        # Generate base performance characteristics for this student
        base_attendance = np.random.normal(75, 15)
        base_assignment_score = np.random.normal(70, 15)
        base_semester_marks = np.random.normal(70, 15)
        base_engagement = np.random.normal(6, 2)
        
        # Determine if student will dropout (affects performance trajectory)
        will_dropout = np.random.random() < DROPOUT_RATE
        
        # Generate 30 days of performance data
        for day in range(NUM_PERFORMANCE_RECORDS_PER_STUDENT):
            record_date = date.today() - timedelta(days=NUM_PERFORMANCE_RECORDS_PER_STUDENT - day)
            
            # Add some trend and noise
            trend_factor = 1.0
            if will_dropout:
                # Declining performance over time
                trend_factor = 1.0 - (day * 0.02)  # Gradual decline
            else:
                # Stable or slightly improving
                trend_factor = 1.0 + (day * 0.005)  # Slight improvement
            
            # Add random noise
            noise_factor = np.random.normal(1.0, 0.1)
            
            attendance = np.clip(base_attendance * trend_factor * noise_factor, 0, 100)
            assignment_score = np.clip(base_assignment_score * trend_factor * noise_factor, 0, 100)
            semester_marks = np.clip(base_semester_marks * trend_factor * noise_factor, 0, 100)
            engagement = np.clip(base_engagement * trend_factor * noise_factor, 0, 10)
            
            record = {
                'student_id': student['student_id'],
                'date': record_date,
                'attendance_percentage': round(attendance, 2),
                'assignment_scores': {
                    'math': round(assignment_score + np.random.normal(0, 5), 2),
                    'physics': round(assignment_score + np.random.normal(0, 5), 2),
                    'programming': round(assignment_score + np.random.normal(0, 5), 2)
                },
                'semester_marks': {
                    'math': round(semester_marks + np.random.normal(0, 8), 2),
                    'physics': round(semester_marks + np.random.normal(0, 8), 2),
                    'programming': round(semester_marks + np.random.normal(0, 8), 2)
                },
                'engagement_score': round(engagement, 2),
                'library_hours': max(0, round(np.random.exponential(3), 2)),
                'extracurricular_participation': random.randint(0, 5),
                'disciplinary_issues': random.choices([0, 1, 2], weights=[0.8, 0.15, 0.05])[0]
            }
            performance_records.append(record)
    
    return pd.DataFrame(performance_records)

def create_training_dataset(students_df, performance_df):
    """Create training dataset for ML model"""
    training_data = []
    
    for _, student in students_df.iterrows():
        student_id = student['student_id']
        student_performance = performance_df[performance_df['student_id'] == student_id]
        
        if len(student_performance) == 0:
            continue
        
        # Calculate aggregated features
        avg_attendance = student_performance['attendance_percentage'].mean()
        
        # Calculate average assignment scores
        all_assignment_scores = []
        for _, record in student_performance.iterrows():
            if isinstance(record['assignment_scores'], dict):
                all_assignment_scores.extend(record['assignment_scores'].values())
        avg_assignment_score = np.mean(all_assignment_scores) if all_assignment_scores else 70
        
        # Calculate average semester marks
        all_semester_marks = []
        for _, record in student_performance.iterrows():
            if isinstance(record['semester_marks'], dict):
                all_semester_marks.extend(record['semester_marks'].values())
        avg_semester_marks = np.mean(all_semester_marks) if all_semester_marks else 70
        
        avg_engagement = student_performance['engagement_score'].mean()
        total_library_hours = student_performance['library_hours'].sum()
        avg_extracurricular = student_performance['extracurricular_participation'].mean()
        total_disciplinary = student_performance['disciplinary_issues'].sum()
        
        # Determine trend
        recent_performance = student_performance.tail(7)['attendance_percentage'].mean()
        older_performance = student_performance.head(7)['attendance_percentage'].mean()
        
        trend_improving = 1 if recent_performance > older_performance * 1.05 else 0
        trend_declining = 1 if recent_performance < older_performance * 0.95 else 0
        
        # Determine dropout based on performance indicators
        risk_factors = []
        if avg_attendance < 60:
            risk_factors.append(1)
        if avg_assignment_score < 50:
            risk_factors.append(1)
        if avg_semester_marks < 50:
            risk_factors.append(1)
        if avg_engagement < 4:
            risk_factors.append(1)
        if total_disciplinary > 2:
            risk_factors.append(1)
        if trend_declining:
            risk_factors.append(1)
        
        # Higher risk = higher chance of dropout
        dropout_probability = min(0.8, len(risk_factors) * 0.15)
        dropout = 1 if np.random.random() < dropout_probability else 0
        
        # Create training record
        training_record = {
            'student_id': student_id,
            'attendance_percentage': round(avg_attendance, 2),
            'avg_assignment_score': round(avg_assignment_score, 2),
            'avg_semester_marks': round(avg_semester_marks, 2),
            'engagement_score': round(avg_engagement, 2),
            'library_hours_per_week': round(total_library_hours / 4, 2),  # 4 weeks
            'extracurricular_participation': round(avg_extracurricular, 2),
            'disciplinary_issues': total_disciplinary,
            'trend_improving': trend_improving,
            'trend_declining': trend_declining,
            'has_mentor': student['has_mentor'],
            'branch': student['branch'].lower().replace(' ', '_'),
            'year': student['year'].split()[0].lower(),  # '1st' -> '1'
            'dropout': dropout
        }
        training_data.append(training_record)
    
    return pd.DataFrame(training_data)

def save_datasets(students_df, performance_df, training_df, output_dir="./sample-data"):
    """Save generated datasets"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save students data
    students_df.to_csv(os.path.join(output_dir, 'students.csv'), index=False)
    print(f"Saved {len(students_df)} students to students.csv")
    
    # Save performance data (simplified for CSV)
    performance_simple = performance_df.copy()
    performance_simple['avg_assignment_score'] = performance_df['assignment_scores'].apply(
        lambda x: np.mean(list(x.values())) if isinstance(x, dict) else 70
    )
    performance_simple['avg_semester_marks'] = performance_df['semester_marks'].apply(
        lambda x: np.mean(list(x.values())) if isinstance(x, dict) else 70
    )
    performance_simple = performance_simple.drop(['assignment_scores', 'semester_marks'], axis=1)
    
    performance_simple.to_csv(os.path.join(output_dir, 'performance.csv'), index=False)
    print(f"Saved {len(performance_simple)} performance records to performance.csv")
    
    # Save training data
    training_df.to_csv(os.path.join(output_dir, 'training_data.csv'), index=False)
    print(f"Saved {len(training_df)} training samples to training_data.csv")
    
    # Print statistics
    print(f"\nDataset Statistics:")
    print(f"- Total students: {len(students_df)}")
    print(f"- Dropout rate: {training_df['dropout'].mean():.2%}")
    print(f"- Branch distribution:")
    for branch, count in students_df['branch'].value_counts().items():
        print(f"  {branch}: {count}")
    print(f"- Year distribution:")
    for year, count in students_df['year'].value_counts().items():
        print(f"  {year}: {count}")

def main():
    """Main data generation pipeline"""
    print("=== Sample Data Generator for Student Dropout Prediction ===")
    print(f"Generating data for {NUM_STUDENTS} students...")
    
    # Generate students
    print("Generating student profiles...")
    students_df = generate_students()
    
    # Generate performance data
    print("Generating performance records...")
    performance_df = generate_performance_data(students_df)
    
    # Create training dataset
    print("Creating ML training dataset...")
    training_df = create_training_dataset(students_df, performance_df)
    
    # Save datasets
    print("Saving datasets...")
    save_datasets(students_df, performance_df, training_df)
    
    print("\n=== Data generation completed! ===")
    print("You can now train the ML model using:")
    print("python ml/train_model.py")

if __name__ == "__main__":
    main()
