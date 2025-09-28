import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/bowling")

try:
    # Connect
    conn = psycopg2.connect(POSTGRES_URL)
    cur = conn.cursor()

    # Run a quick check
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("✅ Connected to Postgres!")
    print("Server version:", version[0])

    # List databases
    cur.execute("SELECT datname FROM pg_database;")
    dbs = cur.fetchall()
    print("\n📂 Databases:", [d[0] for d in dbs])

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Connection failed!")
    print(e)
