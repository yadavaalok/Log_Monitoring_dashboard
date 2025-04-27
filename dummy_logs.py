import sqlite3
import random
import json
from datetime import datetime, timedelta

# Connect DB
conn = sqlite3.connect('logs.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        api_endpoint TEXT,
        status_code INTEGER,
        request_payload TEXT,
        response_payload TEXT,
        error_message TEXT
    )
''')

conn.commit()

# Dummy data
endpoints = ['/login', '/signup', '/payment', '/profile/update', '/order/create']
status_codes = [200, 201, 400, 401, 500]
success_messages = ["Request successful", "User created", "Payment processed", "Profile updated", "Order placed"]
error_messages = ["Invalid credentials", "Missing parameters", "Payment failed", "Unauthorized access",
                  "Internal server error"]

# Insert dummy logs
for _ in range(500):
    ts = datetime.now() - timedelta(minutes=random.randint(0, 1440))
    endpoint = random.choice(endpoints)
    status = random.choice(status_codes)
    request_payload = json.dumps({"user_id": random.randint(1000, 9999)})

    if status >= 400:
        response_payload = json.dumps({"error": random.choice(error_messages)})
        error_message = random.choice(error_messages)
    else:
        response_payload = json.dumps({"message": random.choice(success_messages)})
        error_message = None

    cursor.execute('''
        INSERT INTO api_logs (timestamp, api_endpoint, status_code, request_payload, response_payload, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ts.strftime('%Y-%m-%d %H:%M:%S'), endpoint, status, request_payload, response_payload, error_message))

conn.commit()
conn.close()

print("API Logs created successfully.")
