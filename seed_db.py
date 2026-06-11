import psycopg
import sys
import os

DSN = "postgresql://postgres:Aarokek@127.0.0.1:5432/postgres"

files_to_run = [
    "sample-db/schema/schema.sql",
    "sample-db/seed/seed.sql",
    "sample-db/docker/04_triggers.sql"
]

try:
    with psycopg.connect(DSN, autocommit=True) as conn:
        print("Connected to local PostgreSQL!", flush=True)
        with conn.cursor() as cur:
            print("Wiping existing schema to reset sequences...", flush=True)
            cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
            
            for file_path in files_to_run:
                if not os.path.exists(file_path):
                    print(f"Skipping {file_path}, not found.", flush=True)
                    continue
                print(f"Executing {file_path}...", flush=True)
                with open(file_path, "r", encoding="utf-8") as f:
                    sql = f.read()
                try:
                    cur.execute(sql)
                    print(f"Successfully executed {file_path}", flush=True)
                except Exception as e:
                    print(f"Error executing {file_path}: {e}")
                    # continue to next file
                    
        print("Database seeded successfully!")
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
