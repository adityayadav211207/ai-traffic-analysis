from database.connection import get_connection

conn = get_connection()

cursor = conn.cursor()

# Create Tables
with open("database/schema.sql", "r") as f:

    cursor.executescript(f.read())

# Insert Default Users
with open("database/seed_data.sql", "r") as f:

    cursor.executescript(f.read())

conn.commit()

conn.close()

print("Database Initialized Successfully ✅")