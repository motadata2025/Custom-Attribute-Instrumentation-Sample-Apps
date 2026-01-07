"""
Database connection and initialization module
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from config import Config

def get_db_connection():
    """
    Create and return a PostgreSQL database connection

    Returns:
        psycopg2.Connection: Database connection with RealDictCursor
    """
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    return conn

def create_database_if_not_exists():
    """
    Create the database if it doesn't exist
    """
    try:
        # Connect to default 'postgres' database to check/create our database
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database='postgres',
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (Config.DB_NAME,)
        )
        exists = cursor.fetchone()

        if not exists:
            print(f"Creating database '{Config.DB_NAME}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(Config.DB_NAME)
            ))
            print(f"✅ Database '{Config.DB_NAME}' created successfully!")
        else:
            print(f"✅ Database '{Config.DB_NAME}' already exists")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise

def init_db():
    """
    Initialize the database with schema from schema.sql
    Creates tables and populates with dummy data
    """
    try:
        # First, ensure database exists
        create_database_if_not_exists()

        # Connect to our database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if users table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'users'
            );
        """)
        table_exists = cursor.fetchone()['exists']

        if not table_exists:
            print("Initializing database schema...")
            with open(Config.SCHEMA_PATH, 'r') as f:
                cursor.execute(f.read())
            conn.commit()
            print("✅ Database schema initialized successfully!")
            print(f"📊 Database: {Config.DB_NAME}")
            print(f"🔗 Connection: {Config.DB_HOST}:{Config.DB_PORT}")
        else:
            print(f"✅ Database tables already exist")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

def close_db_connection(conn):
    """
    Close database connection

    Args:
        conn: Database connection to close
    """
    if conn:
        conn.close()

