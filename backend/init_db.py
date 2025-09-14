#!/usr/bin/env python3
"""
Database initialization script for the Student Dropout Prediction Platform
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import get_password_hash


async def init_database():
    """Initialize MongoDB database with demo users and collections"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Connected to MongoDB successfully!")
        
        # Create collections
        collections = ['users', 'students', 'performance', 'alerts', 'feedback', 'predictions']
        for collection in collections:
            try:
                await db.create_collection(collection)
                print(f"✓ Created collection: {collection}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"✓ Collection {collection} already exists")
                else:
                    print(f"✗ Error creating collection {collection}: {e}")
        
        # Create indexes
        indexes = [
            (db.users, [("email", 1)], {"unique": True}),
            (db.students, [("scholar_id", 1)], {"unique": True}),
            (db.students, [("mentor_id", 1)], {}),
            (db.performance, [("student_id", 1), ("date", -1)], {}),
            (db.alerts, [("student_id", 1), ("created_at", -1)], {}),
            (db.alerts, [("mentor_id", 1), ("status", 1)], {}),
            (db.feedback, [("student_id", 1), ("mentor_id", 1)], {}),
            (db.predictions, [("student_id", 1), ("created_at", -1)], {}),
        ]
        
        for collection, keys, options in indexes:
            try:
                await collection.create_index(keys, **options)
                print(f"✓ Created index on {collection.name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"✓ Index on {collection.name} already exists")
                else:
                    print(f"✗ Error creating index on {collection.name}: {e}")
        
        # Hash password for demo users
        hashed_password = get_password_hash("password123")
        current_time = datetime.utcnow()
        
        # Insert demo users
        demo_users = [
            {
                "_id": "admin001",
                "email": "admin@example.com",
                "name": "System Administrator",
                "role": "admin",
                "hashed_password": hashed_password,
                "is_active": True,
                "created_at": current_time,
                "updated_at": current_time
            },
            {
                "_id": "mentor001",
                "email": "mentor@example.com",
                "name": "Dr. Sarah Johnson",
                "role": "mentor",
                "hashed_password": hashed_password,
                "is_active": True,
                "created_at": current_time,
                "updated_at": current_time
            },
            {
                "_id": "student001",
                "email": "student@example.com",
                "name": "Alex Smith",
                "role": "student",
                "hashed_password": hashed_password,
                "is_active": True,
                "created_at": current_time,
                "updated_at": current_time
            }
        ]
        
        # Check if users already exist and insert if they don't
        for user in demo_users:
            existing_user = await db.users.find_one({"email": user["email"]})
            if not existing_user:
                await db.users.insert_one(user)
                print(f"✓ Created demo user: {user['email']}")
            else:
                print(f"✓ Demo user {user['email']} already exists")
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nDemo credentials:")
        print("Admin: admin@example.com / password123")
        print("Mentor: mentor@example.com / password123")
        print("Student: student@example.com / password123")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(init_database())
