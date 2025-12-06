import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),  # Required - set in .env file
    'database': os.getenv('DB_NAME', 'mooddj'),
    'connection_timeout': 100
}

# Connection pool configuration (separate from connection config)
POOL_CONFIG = {
    **DB_CONFIG,
    'pool_name': 'mooddj_pool',
    'pool_size': 5,
    'pool_reset_session': True
}

# Create connection pool
connection_pool = None
try:
    connection_pool = pooling.MySQLConnectionPool(**POOL_CONFIG)
    print("[INFO] Database connection pool created successfully")
except mysql.connector.Error as err:
    print(f"[ERROR] Error creating connection pool: {err}")
    print(f"        Host: {DB_CONFIG['host']}")
    print(f"        User: {DB_CONFIG['user']}")
    print(f"        Database: {DB_CONFIG['database']}")
    connection_pool = None

def get_db_connection():
    """Get a connection from the pool"""
    if connection_pool:
        return connection_pool.get_connection()
    else:
        # Fallback to direct connection
        return mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )

def execute_query(query, params=None, fetch=False):
    """Execute a query and return results if fetch=True"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
