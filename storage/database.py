import sqlite3

conn = sqlite3.connect("chat.db", check_same_thread=False, timeout=10)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    message TEXT
)
""")

conn.commit()

def save_message(sender, message):

    cursor.execute("""
    INSERT INTO messages(sender, message)
    VALUES (?, ?)
    """, (sender, message))

    conn.commit()