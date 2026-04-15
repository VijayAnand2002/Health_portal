import MySQLdb
import os
import sys
from dotenv import load_dotenv
import django

# Add parent directory to sys.path to find health_portal modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_portal.settings')
django.setup()

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), '.env'))

DB_NAME = os.getenv('DB_NAME', 'health_portal_db')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'vj1234')
DB_HOST = os.getenv('DB_HOST', 'localhost')

try:
    db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD)
    cursor = db.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"Database '{DB_NAME}' created or already exists.")
    db.close()
except Exception as e:
    print(f"Error creating database: {e}")
