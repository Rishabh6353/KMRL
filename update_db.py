"""
Update database schema to add confidence_score column
"""
import sqlite3
import os

def update_database():
    db_path = os.path.join('instance', 'documents.db')
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if confidence_score column exists
        cursor.execute("PRAGMA table_info(document)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'confidence_score' not in columns:
            # Add confidence_score column
            cursor.execute('ALTER TABLE document ADD COLUMN confidence_score REAL')
            print("Added confidence_score column successfully")
        else:
            print("confidence_score column already exists")
            
        # Update existing records with default confidence score
        cursor.execute("""
            UPDATE document 
            SET confidence_score = 0.8 
            WHERE confidence_score IS NULL AND document_type IS NOT NULL
        """)
        
        affected = cursor.rowcount
        if affected > 0:
            print(f"Updated {affected} existing records with default confidence score")
            
        conn.commit()
        print("Database updated successfully")
        
    except Exception as e:
        print(f"Error updating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database()