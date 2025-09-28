#!/usr/bin/env python3
"""
Database Migration Script for Intelligent Document Processing System
Adds missing columns to existing database schema.
"""

import sqlite3
import os
import sys
from pathlib import Path

def migrate_database():
    """Add missing columns to the document table."""
    
    # Database paths to check
    db_paths = [
        'documents.db',
        'instance/documents.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No database file found. Please run create_db.py first.")
        return False
    
    print(f"📁 Using database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(document)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Current columns: {columns}")
        
        # List of columns to add
        columns_to_add = [
            ('document_type', 'VARCHAR(100)'),
            ('confidence_score', 'FLOAT'),
            ('department', 'VARCHAR(100)')
        ]
        
        # Add missing columns
        for column_name, column_type in columns_to_add:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE document ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"ℹ️  Column {column_name} already exists")
                    else:
                        print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"ℹ️  Column {column_name} already exists")
        
        # Verify final schema
        cursor.execute("PRAGMA table_info(document)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Final columns: {final_columns}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed! You can now run the application.")
        sys.exit(0)
    else:
        print("\n💥 Migration failed. Please check the errors above.")
        sys.exit(1)