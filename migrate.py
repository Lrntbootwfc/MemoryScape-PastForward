# migrate.py
import sqlite3
import os
import shutil

print("--- Starting Database Migration ---")

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "memoryscape.db")
BACKUP_PATH = os.path.join(DB_DIR, "memoryscape.db.backup")

def migrate():
    # 1. Check if the database exists
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file not found at {DB_PATH}. Nothing to migrate.")
        return

    # 2. Check if the column already exists to prevent running twice
    conn_check = sqlite3.connect(DB_PATH)
    cursor_check = conn_check.cursor()
    try:
        cursor_check.execute("SELECT model_path FROM memories LIMIT 1;")
        print("Database already has the 'model_path' column. No migration needed.")
        conn_check.close()
        return
    except sqlite3.OperationalError:
        # This is expected, means we need to migrate
        conn_check.close()
        pass

    # 3. Create a backup
    try:
        shutil.copyfile(DB_PATH, BACKUP_PATH)
        print(f"Successfully created a backup: {BACKUP_PATH}")
    except Exception as e:
        print(f"FATAL: Could not create database backup. Aborting. Error: {e}")
        return

    # 4. Perform the migration
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("Adding the 'model_path' column to the memories table...")
        cursor.execute("ALTER TABLE memories ADD COLUMN model_path TEXT")

        default_flower = "flower_optimized.glb" # A safe default for old memories
        print(f"Setting a default flower ('{default_flower}') for all existing memories...")
        cursor.execute("UPDATE memories SET model_path = ?", (default_flower,))

        conn.commit()
        conn.close()
        print("\nSUCCESS: Migration complete!")
        print("Your database is now up to date, and your memories are saved.")

    except Exception as e:
        print(f"\nFATAL: An error occurred during migration: {e}")
        print("The database has not been changed. Restore the backup if needed.")

if __name__ == "__main__":
    migrate()
    print("\nYou can now restart your server with the 'uvicorn' command.")