import os
import sqlite3

def run_migration():
    """
    A one-time script to add new columns to the memories table.
    This is necessary to store media paths and flower model information.
    """
    # Define the database path for your local environment
    DB_PATH = os.path.join("data", "memoryscape.db")

    if not os.path.exists(DB_PATH):
        print(f"Database file not found at: {DB_PATH}. Please run your main app first to create it.")
        return

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if the 'memories' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories'")
        table_exists = cursor.fetchone()

        if not table_exists:
            print("Memories table does not exist. Please run your app to create it.")
            conn.close()
            return

        # Check if the 'media_path' column exists
        cursor.execute("PRAGMA table_info(memories)")
        columns = [info[1] for info in cursor.fetchall()]

        if 'media_path' not in columns:
            print("Adding 'media_path' column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN media_path TEXT")
        
        if 'media_type' not in columns:
            print("Adding 'media_type' column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN media_type TEXT")

        if 'model_path' not in columns:
            print("Adding 'model_path' column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN model_path TEXT")

        # Commit the changes
        conn.commit()
        print("Database migration complete. New columns added successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred during migration: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
