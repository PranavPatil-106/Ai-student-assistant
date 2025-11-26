
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "student_assistant")

def init_database():
    """Initialize MySQL database"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        print(f"✓ Database '{MYSQL_DATABASE}' created or already exists")
        
        cursor.close()
        connection.close()
        
        # Now create tables using SQLAlchemy
        from db import init_db
        init_db()
        print("✓ Tables created successfully")
        
        print("\n✅ Database initialization complete!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        print("\nMake sure:")
        print("1. MySQL server is running")
        print("2. Credentials in .env file are correct")
        print("3. MySQL user has CREATE DATABASE privileges")

if __name__ == "__main__":
    print("🚀 Initializing database...")
    init_database()
