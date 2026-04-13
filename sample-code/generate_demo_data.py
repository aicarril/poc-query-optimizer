"""Generate sample event data for Athena demo. Creates partitioned CSV files."""

import csv
import io
import random
import subprocess
from datetime import datetime, timedelta

USERS = [
    {"id": f"user_{i:03d}", "user_name": f"dev_{i}", "email": f"dev_{i}@example.com", "team": random.choice(["platform", "frontend", "backend", "data"])}
    for i in range(1, 51)
]

EVENT_TYPES = ["page_view", "api_call", "login", "logout", "error", "deploy", "query", "upload", "download", "alert"]

def generate_events(date_str: str, count: int) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["event_id", "event_type", "user_id", "duration_ms", "status_code", "endpoint", "created_at"])
    for i in range(count):
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        ts = f"{date_str}T{hour:02d}:{minute:02d}:{second:02d}Z"
        user = random.choice(USERS)
        event_type = random.choice(EVENT_TYPES)
        duration = random.randint(5, 5000) if event_type in ["api_call", "query"] else random.randint(1, 200)
        status = random.choice([200, 200, 200, 200, 201, 400, 404, 500]) if event_type == "api_call" else 200
        endpoint = random.choice(["/api/search", "/api/users", "/api/orders", "/api/reports", "/api/dashboard"])
        writer.writerow([f"evt_{date_str}_{i:05d}", event_type, user["id"], duration, status, endpoint, ts])
    return buf.getvalue()

def generate_users() -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "user_name", "email", "team", "created_at"])
    for u in USERS:
        writer.writerow([u["id"], u["user_name"], u["email"], u["team"], "2025-01-15T00:00:00Z"])
    return buf.getvalue()

if __name__ == "__main__":
    # Upload users table
    users_csv = generate_users()
    with open("/tmp/users.csv", "w") as f:
        f.write(users_csv)
    subprocess.run(["aws", "s3", "cp", "/tmp/users.csv", "s3://aicarril-athena-demo-data/users/users.csv", "--region", "us-east-1"], check=True)
    print("Uploaded users.csv")

    # Upload events partitioned by date (last 7 days)
    base = datetime(2026, 4, 13)
    for day_offset in range(7):
        d = base - timedelta(days=day_offset)
        date_str = d.strftime("%Y-%m-%d")
        events_csv = generate_events(date_str, 500)
        local_path = f"/tmp/events_{date_str}.csv"
        s3_path = f"s3://aicarril-athena-demo-data/events/partition_date={date_str}/events.csv"
        with open(local_path, "w") as f:
            f.write(events_csv)
        subprocess.run(["aws", "s3", "cp", local_path, s3_path, "--region", "us-east-1"], check=True)
        print(f"Uploaded events for {date_str} (500 rows)")

    print("\nDone! Data uploaded to s3://aicarril-athena-demo-data/")
