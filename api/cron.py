import os
import psycopg2

def handler(request, response):
    # Get DATABASE_URL from environment variables
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return response.json({"status": "error", "message": "DATABASE_URL not set"})

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT 1")  # simple query to wake the DB
        cur.close()
        conn.close()
        return response.json({"status": "success", "message": "DB woke up"})
    except Exception as e:
        return response.json({"status": "error", "message": str(e)})