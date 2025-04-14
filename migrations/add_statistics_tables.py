import sys
import os
import datetime
import sqlite3
from pathlib import Path

# Get the project root directory (parent of the migrations directory)
ROOT_DIR = Path(__file__).parent.parent
DB_PATH = ROOT_DIR / "db.sqlite3"

print(f"Database path: {DB_PATH}")
print(f"Database exists: {DB_PATH.exists()}")

# Connect to the SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(column[1] == column_name for column in columns)

def run_migration():
    # Check if the users table exists
    if not check_table_exists('users'):
        print("Error: 'users' table does not exist. The database may not be initialized properly.")
        return False
    
    # Check if the last_active column exists in the users table
    if not check_column_exists('users', 'last_active'):
        print("Adding 'last_active' column to users table...")
        # Add column without default value
        cursor.execute("ALTER TABLE users ADD COLUMN last_active TIMESTAMP")
        
        # Update all existing rows with current timestamp
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(f"UPDATE users SET last_active = '{current_time}'")
        
        conn.commit()
        print("Added 'last_active' column to users table and set current timestamp for existing users")
    else:
        print("'last_active' column already exists in users table")
    
    # Create command_logs table if it doesn't exist
    if not check_table_exists('command_logs'):
        print("Creating command_logs table...")
        cursor.execute('''
        CREATE TABLE command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            command TEXT NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        print("Created command_logs table")
    else:
        print("command_logs table already exists")
    
    # Create user_sessions table if it doesn't exist
    if not check_table_exists('user_sessions'):
        print("Creating user_sessions table...")
        cursor.execute('''
        CREATE TABLE user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_end TIMESTAMP,
            duration_seconds INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        print("Created user_sessions table")
    else:
        print("user_sessions table already exists")
    
    # Create daily_statistics table if it doesn't exist
    if not check_table_exists('daily_statistics'):
        print("Creating daily_statistics table...")
        cursor.execute('''
        CREATE TABLE daily_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active_users INTEGER DEFAULT 0,
            new_users INTEGER DEFAULT 0,
            words_added INTEGER DEFAULT 0,
            words_learned INTEGER DEFAULT 0,
            total_commands INTEGER DEFAULT 0
        )
        ''')
        print("Created daily_statistics table")
    else:
        print("daily_statistics table already exists")
    
    conn.commit()
    return True

if __name__ == "__main__":
    try:
        if run_migration():
            print("Migration completed successfully")
        else:
            print("Migration failed")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()
