import sqlite3
import config
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


def save_message(sender, message, recipient=None):
    # Convert the UI string "Global Chat" to None for the database
    if recipient == "Global Chat":
        recipient = None

    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, message, recipient) VALUES (?, ?, ?)",
                   (sender, message, recipient))
    conn.commit()
    conn.close()


def get_history(target_peer=None):
    """
    target_peer is None for Global.
    target_peer is a string (e.g., 'Bob-a1b2') for Private.
    """
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    my_id = config.PEER_ID

    if target_peer is None:
        # Global Chat: Look for rows where recipient is null
        cursor.execute("SELECT sender, message FROM messages WHERE recipient IS NULL")
    else:
        # Private Chat: Messages between ME and TARGET
        # We need both directions to see a full conversation!
        cursor.execute("""
            SELECT sender, message FROM messages 
            WHERE (sender = ? AND recipient = ?) 
            OR (sender = ? AND recipient = ?)
            ORDER BY id ASC
        """, (my_id, target_peer, target_peer, my_id))

    rows = cursor.fetchall()
    conn.close()
    return rows