# backend/migrate.py
import os
import sqlite3
import random
import json
from typing import List, Tuple, Optional

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "memoryscape.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def migrate_memories():
    print("Starting database migration...")
    
    try:
        with get_conn() as conn:
            # Step 1: Add a new column for position if it doesn't exist
            conn.execute("ALTER TABLE memories ADD COLUMN position TEXT;")
            print("Added 'position' column to 'memories' table.")
            conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'position' already exists. Skipping migration.")
            return
        else:
            print(f"An error occurred: {e}")
            return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    # Step 2: Get all memories that need a position
    with get_conn() as conn:
        cur = conn.execute("SELECT id FROM memories WHERE position IS NULL;")
        memories_to_migrate = cur.fetchall()

        if not memories_to_migrate:
            print("No memories found that need a position. Migration finished.")
            return

        print(f"Found {len(memories_to_migrate)} memories to update.")

        # Step 3: Generate and save a random position for each memory
        for memory_id_tuple in memories_to_migrate:
            memory_id = memory_id_tuple[0]
            # Generate a random position
            position = [random.uniform(-20, 20), 0.0, random.uniform(-20, 20)]
            # Convert the list to a JSON string for storage
            position_json = json.dumps(position)
            
            conn.execute(
                "UPDATE memories SET position = ? WHERE id = ?;",
                (position_json, memory_id)
            )
        
        conn.commit()
        print("Successfully updated all memories with new positions.")
        
if __name__ == "__main__":
    migrate_memories()