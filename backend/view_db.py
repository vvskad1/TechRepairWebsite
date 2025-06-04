import sqlite3

conn = sqlite3.connect('fixit.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# Example: View all bookings
try:
    cursor.execute("SELECT * FROM bookings;")
    print("Bookings:", cursor.fetchall())
except Exception as e:
    print("No bookings table or error:", e)

# Example: View all contacts
try:
    cursor.execute("SELECT * FROM contacts;")
    print("Contacts:", cursor.fetchall())
except Exception as e:
    print("No contacts table or error:", e)

conn.close()
