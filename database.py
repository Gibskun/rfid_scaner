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
        """Create necessary database tables if they don't exist"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            # Check if tables exist first
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'rfid_tags'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                print("✅ Database tables already exist - preserving existing data")
                
                # Check if we need to add new columns for historical data support
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'rfid_tags' AND table_schema = 'public'
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
                
                # Migrate schema if needed (add id column if missing)
                if 'id' not in existing_columns:
                    print("🔄 Migrating schema to support historical data...")
                    
                    # Add id column as serial primary key
                    cursor.execute("ALTER TABLE rfid_tags ADD COLUMN id SERIAL")
                    
                    # Remove old primary key constraint on tag_id
                    cursor.execute("ALTER TABLE rfid_tags DROP CONSTRAINT IF EXISTS rfid_tags_pkey")
                    
                    # Set new primary key
                    cursor.execute("ALTER TABLE rfid_tags ADD PRIMARY KEY (id)")
                    
                    print("✅ Schema migration completed - historical data support added")
                
            else:
                print("📋 Creating new database tables...")
                
                # Create new tags table with historical data support
                cursor.execute("""
                    CREATE TABLE rfid_tags (
                        id SERIAL PRIMARY KEY,
                        tag_id VARCHAR(500) NOT NULL,
                        rf_id VARCHAR(255),
                        palette_number INTEGER,
                        name VARCHAR(255),
                        status VARCHAR(50) DEFAULT 'active',
                        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        deleted TIMESTAMP NULL
                    )
                """)
                
                print("✅ New database tables created successfully")
            
            # Create/update indexes for faster lookups (these are safe to run multiple times)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tag_id ON rfid_tags(tag_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rf_id ON rfid_tags(rf_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_palette_number ON rfid_tags(palette_number)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON rfid_tags(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tag_status ON rfid_tags(tag_id, status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created ON rfid_tags(created)
            """)
            
            conn.commit()
            print("✅ Database indexes verified/created")
            
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def add_or_update_tag(self, tag_id: str, rf_id: str = None, palette_number: int = None, name: str = None) -> bool:
        """Add new tag registration (backward compatible with old and new schema)"""
        conn = None
        try:
            with self.lock:
                conn = self.connection_pool.getconn()
                cursor = conn.cursor()
                
                # Check if we have the 'id' column (new schema) or not (old schema)
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'rfid_tags' AND table_schema = 'public' AND column_name = 'id'
                """)
                has_id_column = cursor.fetchone() is not None
                
                if has_id_column:
                    # New schema - always create new records for history
                    # Check if tag has existing records
                    cursor.execute("""
                        SELECT id, status, rf_id, palette_number, name, created, deleted
                        FROM rfid_tags 
                        WHERE tag_id = %s 
                        ORDER BY created DESC 
                        LIMIT 1
                    """, (tag_id,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        existing_id, current_status, existing_rf_id, existing_palette, existing_name, existing_created, existing_deleted = existing
                        
                        if current_status == 'active':
                            # Tag is currently active - check if this is just an update with same data
                            if (existing_rf_id == rf_id and 
                                existing_palette == palette_number and 
                                existing_name == name):
                                print(f"⚠️ Tag already registered with same data: {tag_id[:20]}...")
                                return True
                            else:
                                # Different data provided for active tag - create new record anyway for history
                                print(f"🔄 Creating new record for active tag with updated data: {tag_id[:20]}...")
                        
                        elif current_status == 'non_active':
                            # Tag was unregistered - create new registration record
                            print(f"🔄 Re-registering previously unregistered tag: {tag_id[:20]}...")
                        
                        else:
                            # Other status (deleted, etc.) - allow new registration
                            print(f"🔄 Registering tag with previous status {current_status}: {tag_id[:20]}...")
                    
                    # Always insert new record to preserve historical data
                    cursor.execute("""
                        INSERT INTO rfid_tags (tag_id, rf_id, palette_number, name, status)
                        VALUES (%s, %s, %s, %s, 'active')
                    """, (tag_id, rf_id, palette_number, name))
                    
                    registration_type = "re-registered" if existing else "registered"
                    print(f"✅ Tag {registration_type}: {tag_id[:20]}... → New record created")
                
                else:
                    # Old schema - update existing or insert new (original behavior)
                    cursor.execute("SELECT tag_id, status FROM rfid_tags WHERE tag_id = %s", (tag_id,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        current_status = existing[1]
                        
                        # If tag is non_active, allow re-registration with new data
                        if current_status == 'non_active':
                            # Re-register tag: update with new data, set status to active, clear deleted timestamp
                            update_fields = ['status = %s', 'deleted = NULL']
                            update_values = ['active']
                            
                            if rf_id is not None:
                                update_fields.append("rf_id = %s")
                                update_values.append(rf_id)
                            if palette_number is not None:
                                update_fields.append("palette_number = %s")
                                update_values.append(palette_number)
                            if name is not None:
                                update_fields.append("name = %s")
                                update_values.append(name)
                            
                            update_values.append(tag_id)
                            cursor.execute(f"""
                                UPDATE rfid_tags 
                                SET {', '.join(update_fields)}
                                WHERE tag_id = %s
                            """, tuple(update_values))
                            print(f"✅ Tag re-registered (old schema): {tag_id[:20]}... (non_active → active)")
                            
                        else:
                            # Update existing active tag (only update non-None values)
                            update_fields = []
                            update_values = []
                            
                            if rf_id is not None:
                                update_fields.append("rf_id = %s")
                                update_values.append(rf_id)
                            if palette_number is not None:
                                update_fields.append("palette_number = %s")
                                update_values.append(palette_number)
                            if name is not None:
                                update_fields.append("name = %s")
                                update_values.append(name)
                            
                            if update_fields:
                                update_values.append(tag_id)
                                cursor.execute(f"""
                                    UPDATE rfid_tags 
                                    SET {', '.join(update_fields)}
                                    WHERE tag_id = %s
                                """, tuple(update_values))
                                print(f"✅ Tag updated (old schema): {tag_id[:20]}...")
                    else:
                        # Insert new tag
                        cursor.execute("""
                            INSERT INTO rfid_tags (tag_id, rf_id, palette_number, name, status)
                            VALUES (%s, %s, %s, %s, 'active')
                        """, (tag_id, rf_id, palette_number, name))
                        print(f"✅ New tag registered (old schema): {tag_id[:20]}...")
                
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
        """Get most recent tag information from database (backward compatible)"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            # Check if we have the 'id' column (new schema) or not (old schema)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'rfid_tags' AND table_schema = 'public' AND column_name = 'id'
            """)
            has_id_column = cursor.fetchone() is not None
            
            if has_id_column:
                # New schema with historical records
                cursor.execute("""
                    SELECT id, tag_id, rf_id, palette_number, name, status, created, deleted
                    FROM rfid_tags
                    WHERE tag_id = %s
                    ORDER BY created DESC
                    LIMIT 1
                """, (tag_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'tag_id': row[1],
                        'rf_id': row[2],
                        'palette_number': row[3],
                        'name': row[4],
                        'status': row[5],
                        'created': row[6],
                        'deleted': row[7]
                    }
            else:
                # Old schema without id column
                cursor.execute("""
                    SELECT tag_id, rf_id, palette_number, name, status, created, deleted
                    FROM rfid_tags
                    WHERE tag_id = %s
                """, (tag_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': None,  # No id in old schema
                        'tag_id': row[0],
                        'rf_id': row[1],
                        'palette_number': row[2],
                        'name': row[3],
                        'status': row[4],
                        'created': row[5],
                        'deleted': row[6]
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Database error in get_tag_info: {e}")
            return None
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    

    
    def get_all_tags(self, limit: int = 100, offset: int = 0, include_inactive: bool = True) -> List[Dict]:
        """Get most recent record for each unique tag from database with pagination"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            if include_inactive:
                # Get most recent record for each unique tag_id (exclude only permanently deleted ones)
                cursor.execute("""
                    SELECT DISTINCT ON (tag_id) 
                           id, tag_id, rf_id, palette_number, name, status, created, deleted
                    FROM rfid_tags
                    WHERE status != 'deleted'
                    ORDER BY tag_id, created DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            else:
                # Only most recent active records for each tag
                cursor.execute("""
                    SELECT DISTINCT ON (tag_id) 
                           id, tag_id, rf_id, palette_number, name, status, created, deleted
                    FROM rfid_tags
                    WHERE status = 'active'
                    ORDER BY tag_id, created DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            
            tags = []
            for row in cursor.fetchall():
                tags.append({
                    'id': row[0],
                    'tag_id': row[1],
                    'rf_id': row[2],
                    'palette_number': row[3],
                    'name': row[4],
                    'status': row[5],
                    'created': row[6],
                    'deleted': row[7]
                })
            
            return tags
            
        except Exception as e:
            print(f"❌ Database error in get_all_tags: {e}")
            return []
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def get_tag_history(self, tag_id: str) -> List[Dict]:
        """Get complete history for a specific tag (backward compatible)"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            # Check if we have the 'id' column (new schema) or not (old schema)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'rfid_tags' AND table_schema = 'public' AND column_name = 'id'
            """)
            has_id_column = cursor.fetchone() is not None
            
            if has_id_column:
                # New schema - can get full history
                cursor.execute("""
                    SELECT id, tag_id, rf_id, palette_number, name, status, created, deleted
                    FROM rfid_tags
                    WHERE tag_id = %s
                    ORDER BY created DESC
                """, (tag_id,))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'id': row[0],
                        'tag_id': row[1],
                        'rf_id': row[2],
                        'palette_number': row[3],
                        'name': row[4],
                        'status': row[5],
                        'created': row[6],
                        'deleted': row[7]
                    })
            else:
                # Old schema - only one record per tag_id
                cursor.execute("""
                    SELECT tag_id, rf_id, palette_number, name, status, created, deleted
                    FROM rfid_tags
                    WHERE tag_id = %s
                """, (tag_id,))
                
                history = []
                row = cursor.fetchone()
                if row:
                    history.append({
                        'id': None,  # No ID in old schema
                        'tag_id': row[0],
                        'rf_id': row[1],
                        'palette_number': row[2],
                        'name': row[3],
                        'status': row[4],
                        'created': row[5],
                        'deleted': row[6]
                    })
            
            return history
            
        except Exception as e:
            print(f"❌ Database error in get_tag_history: {e}")
            return []
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def search_tags(self, search_term: str) -> List[Dict]:
        """Search tags by tag_id, rf_id, or name - returns most recent record for each matching tag"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute("""
                SELECT DISTINCT ON (tag_id) 
                       id, tag_id, rf_id, palette_number, name, status, created, deleted
                FROM rfid_tags
                WHERE status != 'deleted'
                  AND (tag_id ILIKE %s OR rf_id ILIKE %s OR name ILIKE %s)
                ORDER BY tag_id, created DESC
                LIMIT 50
            """, (search_pattern, search_pattern, search_pattern))
            
            tags = []
            for row in cursor.fetchall():
                tags.append({
                    'id': row[0],
                    'tag_id': row[1],
                    'rf_id': row[2],
                    'palette_number': row[3],
                    'name': row[4],
                    'status': row[5],
                    'created': row[6],
                    'deleted': row[7]
                })
            
            return tags
            
        except Exception as e:
            print(f"❌ Database error in search_tags: {e}")
            return []
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def get_statistics(self) -> Dict:
        """Get database statistics based on most recent record for each unique tag"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            cursor = conn.cursor()
            
            # Get unique tags with their most recent status
            cursor.execute("""
                SELECT COUNT(DISTINCT tag_id) as unique_tags,
                       COUNT(CASE WHEN latest.status = 'active' THEN 1 END) as active_tags,
                       COUNT(CASE WHEN latest.status = 'non_active' THEN 1 END) as non_active_tags,
                       COUNT(CASE WHEN latest.status = 'deleted' THEN 1 END) as deleted_tags,
                       COUNT(CASE WHEN latest.status = 'active' AND latest.palette_number IS NOT NULL THEN 1 END) as assigned_tags,
                       COUNT(*) as total_records
                FROM (
                    SELECT DISTINCT ON (tag_id) tag_id, status, palette_number
                    FROM rfid_tags
                    ORDER BY tag_id, created DESC
                ) latest
                WHERE latest.status != 'deleted'
            """)
            
            row = cursor.fetchone()
            if row:
                unique_tags, active_tags, non_active_tags, deleted_tags, assigned_tags, total_records = row
                
                # Total records in database
                cursor.execute("SELECT COUNT(*) FROM rfid_tags")
                total_records = cursor.fetchone()[0]
                
                return {
                    'unique_tags': unique_tags or 0,
                    'total_records': total_records or 0,
                    'active_tags': active_tags or 0,
                    'non_active_tags': non_active_tags or 0,
                    'deleted_tags': deleted_tags or 0,
                    'assigned_tags': assigned_tags or 0,
                    'unassigned_tags': (active_tags or 0) - (assigned_tags or 0),
                    'can_reregister': non_active_tags or 0  # Tags that can be re-registered
                }
            else:
                return {
                    'unique_tags': 0,
                    'total_records': 0,
                    'active_tags': 0,
                    'non_active_tags': 0,
                    'deleted_tags': 0,
                    'assigned_tags': 0,
                    'unassigned_tags': 0,
                    'can_reregister': 0
                }
            
        except Exception as e:
            print(f"❌ Database error in get_statistics: {e}")
            return {
                'unique_tags': 0,
                'total_records': 0,
                'active_tags': 0,
                'non_active_tags': 0,
                'deleted_tags': 0,
                'assigned_tags': 0,
                'unassigned_tags': 0,
                'can_reregister': 0
            }
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def delete_tag(self, tag_id: str) -> bool:
        """Soft delete a tag from the database (mark as deleted)"""
        conn = None
        try:
            with self.lock:
                conn = self.connection_pool.getconn()
                cursor = conn.cursor()
                
                # Check if tag exists and is not already deleted
                cursor.execute("SELECT tag_id FROM rfid_tags WHERE tag_id = %s AND deleted IS NULL", (tag_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Soft delete - set deleted timestamp
                    cursor.execute("""
                        UPDATE rfid_tags 
                        SET deleted = CURRENT_TIMESTAMP, status = 'deleted'
                        WHERE tag_id = %s
                    """, (tag_id,))
                    
                    conn.commit()
                    print(f"✅ Tag soft deleted successfully: {tag_id[:20]}...")
                    return True
                else:
                    print(f"⚠️  Tag not found or already deleted: {tag_id[:20]}...")
                    return False
                    
        except Exception as e:
            print(f"❌ Database error in delete_tag: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def unregister_tag(self, tag_id: str) -> bool:
        """Unregister a tag (set status to non_active and fill deleted timestamp - backward compatible)"""
        conn = None
        try:
            with self.lock:
                conn = self.connection_pool.getconn()
                cursor = conn.cursor()
                
                # Check if we have the 'id' column (new schema) or not (old schema)
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'rfid_tags' AND table_schema = 'public' AND column_name = 'id'
                """)
                has_id_column = cursor.fetchone() is not None
                
                if has_id_column:
                    # New schema - find the most recent active record for this tag
                    cursor.execute("""
                        SELECT id, status FROM rfid_tags 
                        WHERE tag_id = %s AND status = 'active'
                        ORDER BY created DESC
                        LIMIT 1
                    """, (tag_id,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        record_id, current_status = existing
                        # Unregister - set status to non_active and set deleted timestamp on this specific record
                        cursor.execute("""
                            UPDATE rfid_tags 
                            SET deleted = CURRENT_TIMESTAMP, status = 'non_active'
                            WHERE id = %s
                        """, (record_id,))
                        
                        print(f"✅ Tag unregistered (new schema): {tag_id[:20]}... (record ID: {record_id}, status: active → non_active)")
                    else:
                        print(f"⚠️  No active records found for tag: {tag_id[:20]}...")
                        return False
                        
                else:
                    # Old schema - update tag directly
                    cursor.execute("""
                        UPDATE rfid_tags 
                        SET deleted = CURRENT_TIMESTAMP, status = 'non_active'
                        WHERE tag_id = %s AND status = 'active'
                    """, (tag_id,))
                    
                    if cursor.rowcount > 0:
                        print(f"✅ Tag unregistered (old schema): {tag_id[:20]}... (status: active → non_active)")
                    else:
                        print(f"⚠️  No active records found for tag: {tag_id[:20]}...")
                        return False
                
                conn.commit()
                return True
                    
        except Exception as e:
            print(f"❌ Database error in unregister_tag: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def restore_tag(self, tag_id: str) -> bool:
        """Restore a soft-deleted tag"""
        conn = None
        try:
            with self.lock:
                conn = self.connection_pool.getconn()
                cursor = conn.cursor()
                
                # Check if tag exists and is deleted
                cursor.execute("SELECT tag_id FROM rfid_tags WHERE tag_id = %s AND deleted IS NOT NULL", (tag_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Restore tag - clear deleted timestamp and reset status
                    cursor.execute("""
                        UPDATE rfid_tags 
                        SET deleted = NULL, status = 'active'
                        WHERE tag_id = %s
                    """, (tag_id,))
                    
                    conn.commit()
                    print(f"✅ Tag restored successfully: {tag_id[:20]}...")
                    return True
                else:
                    print(f"⚠️  Tag not found or not deleted: {tag_id[:20]}...")
                    return False
                    
        except Exception as e:
            print(f"❌ Database error in restore_tag: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def update_tag_status(self, tag_id: str, status: str) -> bool:
        """Update tag status (active, inactive, etc.)"""
        conn = None
        try:
            with self.lock:
                conn = self.connection_pool.getconn()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE rfid_tags 
                    SET status = %s
                    WHERE tag_id = %s AND deleted IS NULL
                """, (status, tag_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"✅ Tag status updated: {tag_id[:20]}... → {status}")
                    return True
                else:
                    print(f"⚠️  Tag not found or already deleted: {tag_id[:20]}...")
                    return False
                    
        except Exception as e:
            print(f"❌ Database error in update_tag_status: {e}")
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
