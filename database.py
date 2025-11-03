#!/usr/bin/env python3
"""
RFID Database Manager - PostgreSQL Integration
Manages tag storage, retrieval, and writing operations
"""

import psycopg2
from psycopg2 import pool
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import threading

class RFIDDatabase:
    """PostgreSQL database manager for RFID tags"""
    
    def __init__(self, host='localhost', port=5432, username='postgres', password='123', database='rfid_system'):
        """Initialize database connection pool"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.connection_pool = None
        self.lock = threading.RLock()
        
        # Initialize connection pool
        self._initialize_pool()
        
        # Create tables if they don't exist
        self._create_tables()
    
    def _initialize_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            # First, try to connect to check if database exists
            temp_conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database='postgres'  # Connect to default database first
            )
            temp_conn.autocommit = True
            cursor = temp_conn.cursor()
            
            # Check if our database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            exists = cursor.fetchone()
            
            if not exists:
                # Create database if it doesn't exist
                cursor.execute(f'CREATE DATABASE {self.database}')
                print(f"✅ Created database: {self.database}")
            
            cursor.close()
            temp_conn.close()
            
            # Now create connection pool to our database
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,  # min and max connections
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database
            )
            print(f"✅ Database connection pool initialized: {self.database}")
            
        except Exception as e:
            print(f"❌ Failed to initialize database pool: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary database tables"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            # Create tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rfid_tags (
                    id SERIAL PRIMARY KEY,
                    tag_id VARCHAR(500) UNIQUE NOT NULL,
                    tag_data BYTEA,
                    item_name VARCHAR(255),
                    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    unwrite_date TIMESTAMP,
                    first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    detection_count INTEGER DEFAULT 1,
                    is_written BOOLEAN DEFAULT FALSE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on tag_id for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tag_id ON rfid_tags(tag_id)
            """)
            
            # Create index on write_date
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_write_date ON rfid_tags(write_date)
            """)
            
            # Create tag history table for tracking all detections
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tag_detection_history (
                    id SERIAL PRIMARY KEY,
                    tag_id VARCHAR(500) NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    signal_strength VARCHAR(50),
                    notes TEXT
                )
            """)
            
            # Create index on tag_id for history
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_tag_id ON tag_detection_history(tag_id)
            """)
            
            conn.commit()
            print("✅ Database tables created/verified successfully")
            
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def add_or_update_tag(self, tag_id: str, tag_data: bytes, item_name: Optional[str] = None) -> bool:
        """Add new tag or update existing tag in database"""
        conn = None
        try:
            with self.lock:
                conn = self.connection_pool.getconn()
                cursor = conn.cursor()
                
                # Check if tag exists
                cursor.execute("SELECT id, detection_count FROM rfid_tags WHERE tag_id = %s", (tag_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing tag
                    tag_db_id, current_count = existing
                    cursor.execute("""
                        UPDATE rfid_tags 
                        SET last_detected = CURRENT_TIMESTAMP,
                            detection_count = %s,
                            updated_at = CURRENT_TIMESTAMP,
                            tag_data = %s
                        WHERE tag_id = %s
                    """, (current_count + 1, psycopg2.Binary(tag_data), tag_id))
                else:
                    # Insert new tag
                    cursor.execute("""
                        INSERT INTO rfid_tags (tag_id, tag_data, item_name, is_written)
                        VALUES (%s, %s, %s, FALSE)
                    """, (tag_id, psycopg2.Binary(tag_data), item_name))
                
                # Add to detection history
                cursor.execute("""
                    INSERT INTO tag_detection_history (tag_id, detected_at)
                    VALUES (%s, CURRENT_TIMESTAMP)
                """, (tag_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Database error in add_or_update_tag: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def get_tag_info(self, tag_id: str) -> Optional[Dict]:
        """Get tag information from database"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tag_id, item_name, write_date, unwrite_date, 
                       first_detected, last_detected, detection_count, is_written, notes
                FROM rfid_tags
                WHERE tag_id = %s
            """, (tag_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'tag_id': row[0],
                    'item_name': row[1],
                    'write_date': row[2],
                    'unwrite_date': row[3],
                    'first_detected': row[4],
                    'last_detected': row[5],
                    'detection_count': row[6],
                    'is_written': row[7],
                    'notes': row[8]
                }
            return None
            
        except Exception as e:
            print(f"❌ Database error in get_tag_info: {e}")
            return None
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    

    
    def get_all_tags(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all tags from database with pagination"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tag_id, item_name, write_date, unwrite_date,
                       first_detected, last_detected, detection_count, is_written
                FROM rfid_tags
                ORDER BY last_detected DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            tags = []
            for row in cursor.fetchall():
                tags.append({
                    'tag_id': row[0],
                    'item_name': row[1],
                    'write_date': row[2],
                    'unwrite_date': row[3],
                    'first_detected': row[4],
                    'last_detected': row[5],
                    'detection_count': row[6],
                    'is_written': row[7]
                })
            
            return tags
            
        except Exception as e:
            print(f"❌ Database error in get_all_tags: {e}")
            return []
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def search_tags(self, search_term: str) -> List[Dict]:
        """Search tags by tag_id or item_name"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute("""
                SELECT tag_id, item_name, write_date, unwrite_date,
                       first_detected, last_detected, detection_count, is_written
                FROM rfid_tags
                WHERE tag_id ILIKE %s OR item_name ILIKE %s
                ORDER BY last_detected DESC
                LIMIT 50
            """, (search_pattern, search_pattern))
            
            tags = []
            for row in cursor.fetchall():
                tags.append({
                    'tag_id': row[0],
                    'item_name': row[1],
                    'write_date': row[2],
                    'unwrite_date': row[3],
                    'first_detected': row[4],
                    'last_detected': row[5],
                    'detection_count': row[6],
                    'is_written': row[7]
                })
            
            return tags
            
        except Exception as e:
            print(f"❌ Database error in search_tags: {e}")
            return []
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            # Total tags
            cursor.execute("SELECT COUNT(*) FROM rfid_tags")
            total_tags = cursor.fetchone()[0]
            
            # Written tags
            cursor.execute("SELECT COUNT(*) FROM rfid_tags WHERE is_written = TRUE")
            written_tags = cursor.fetchone()[0]
            
            # Total detections
            cursor.execute("SELECT SUM(detection_count) FROM rfid_tags")
            total_detections = cursor.fetchone()[0] or 0
            
            # Recent detections (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM tag_detection_history 
                WHERE detected_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
            """)
            recent_detections = cursor.fetchone()[0]
            
            return {
                'total_tags': total_tags,
                'written_tags': written_tags,
                'unwritten_tags': total_tags - written_tags,
                'total_detections': total_detections,
                'recent_detections_24h': recent_detections
            }
            
        except Exception as e:
            print(f"❌ Database error in get_statistics: {e}")
            return {
                'total_tags': 0,
                'written_tags': 0,
                'unwritten_tags': 0,
                'total_detections': 0,
                'recent_detections_24h': 0
            }
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag from the database"""
        conn = None
        try:
            with self.lock:
                conn = self.connection_pool.getconn()
                cursor = conn.cursor()
                
                # Check if tag exists first
                cursor.execute("SELECT id FROM rfid_tags WHERE tag_id = %s", (tag_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Delete from tag detection history first (foreign key constraint)
                    cursor.execute("DELETE FROM tag_detection_history WHERE tag_id = %s", (tag_id,))
                    
                    # Delete the main tag record
                    cursor.execute("DELETE FROM rfid_tags WHERE tag_id = %s", (tag_id,))
                    
                    conn.commit()
                    print(f"✅ Tag deleted successfully: {tag_id[:20]}...")
                    return True
                else:
                    print(f"⚠️  Tag not found in database: {tag_id[:20]}...")
                    return False
                    
        except Exception as e:
            print(f"❌ Database error in delete_tag: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def close(self):
        """Close all database connections"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ Database connections closed")


# Global database instance
_db_instance = None
_db_lock = threading.Lock()

def get_database() -> RFIDDatabase:
    """Get or create global database instance (singleton pattern)"""
    global _db_instance
    
    if _db_instance is None:
        with _db_lock:
            if _db_instance is None:
                _db_instance = RFIDDatabase(
                    host='localhost',
                    port=5432,
                    username='postgres',
                    password='123',
                    database='rfid_system'
                )
    
    return _db_instance
