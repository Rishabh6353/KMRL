#!/usr/bin/env python3
import sqlite3
import os

# Check if database exists
db_path = 'instance/documents.db'
if os.path.exists(db_path):
    print(f"✅ Database found: {db_path}")
    
    # Connect and check content
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table schema
    cursor.execute("PRAGMA table_info(document)")
    columns = cursor.fetchall()
    print("\n📋 Table schema:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check documents
    cursor.execute('SELECT id, original_filename, document_type, status, upload_date FROM document LIMIT 10')
    rows = cursor.fetchall()
    
    print(f"\n📄 Documents in database ({len(rows)} found):")
    for row in rows:
        print(f"  ID: {row[0]}, File: {row[1]}, Type: {row[2]}, Status: {row[3]}, Date: {row[4]}")
        
    conn.close()
else:
    print(f"❌ Database not found: {db_path}")