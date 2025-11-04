#!/usr/bin/env python3
import psycopg2
from psycopg2 import pool
import sys
import os

# Database configuration
HOST = "localhost"
PORT = 5432
USERNAME = "postgres"
PASSWORD = "123"  
DATABASE = "rfid_system"

def clear_database():
    """Clear all records from rfid_tags table"""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            user=USERNAME, 
            password=PASSWORD,
            database=DATABASE
        )
        
        cursor = conn.cursor()
        
        print("Clearing all records from rfid_tags table...")
        cursor.execute("DELETE FROM rfid_tags")
        rows_deleted = cursor.rowcount
        
        conn.commit()
        
        print(f"SUCCESS: Cleared {rows_deleted} records from rfid_tags table")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to clear database: {e}")
        return False

if __name__ == "__main__":
    success = clear_database()
    if success:
        print("Database cleared successfully!")
        sys.exit(0)
    else:
        print("Failed to clear database")
        sys.exit(1)