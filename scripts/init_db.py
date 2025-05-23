import sys
import os

# Correctly set up PYTHONPATH before other imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(str(project_root))

from alembic.config import Config
from alembic import command
from mcp.db.session import DB_CONFIG
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Create the database if it doesn't exist."""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Create a cursor
    cur = conn.cursor()
    
    try:
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        exists = cur.fetchone()
        
        if not exists:
            # Create database
            cur.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"Database {DB_CONFIG['database']} created successfully.")
        else:
            print(f"Database {DB_CONFIG['database']} already exists.")
            
    except Exception as e:
        print(f"Error creating database: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def run_migrations():
    """Run database migrations using Alembic."""
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("Database migrations completed successfully.")
    except Exception as e:
        print(f"Error running migrations: {e}")
        raise

def main():
    """Initialize the database and run migrations."""
    print("Initializing database...")
    create_database()
    
    print("Running migrations...")
    run_migrations()
    
    print("Database initialization completed successfully.")

if __name__ == "__main__":
    main() 