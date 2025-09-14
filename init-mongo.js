// MongoDB initialization script
db = db.getSiblingDB('dropout_prediction');

// Create collections
db.createCollection('users');
db.createCollection('students');
db.createCollection('performance');
db.createCollection('alerts');
db.createCollection('feedback');
db.createCollection('predictions');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.students.createIndex({ "scholar_id": 1 }, { unique: true });
db.students.createIndex({ "mentor_id": 1 });
db.performance.createIndex({ "student_id": 1, "date": -1 });
db.alerts.createIndex({ "student_id": 1, "created_at": -1 });
db.alerts.createIndex({ "mentor_id": 1, "status": 1 });
db.feedback.createIndex({ "student_id": 1, "mentor_id": 1 });
db.predictions.createIndex({ "student_id": 1, "created_at": -1 });

// Insert demo users
db.users.insertMany([
  {
    _id: "admin001",
    email: "admin@example.com",
    name: "System Administrator",
    role: "admin",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlUG", // password123
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: "mentor001",
    email: "mentor@example.com",
    name: "Dr. Sarah Johnson",
    role: "mentor",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlUG", // password123
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    _id: "student001",
    email: "student@example.com",
    name: "Alex Smith",
    role: "student",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PmvlUG", // password123
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print('Database initialized successfully with demo users');
print('Demo credentials:');
print('Admin: admin@example.com / password123');
print('Mentor: mentor@example.com / password123');
print('Student: student@example.com / password123');
