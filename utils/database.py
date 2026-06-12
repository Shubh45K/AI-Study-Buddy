import sqlite3

def create_db():

    conn = sqlite3.connect(
        "database/chat_history.db"
    )

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        bot_response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_chat(user, bot):

    conn = sqlite3.connect(
        "database/chat_history.db"
    )

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO chats
        (user_message, bot_response)
        VALUES (?,?)
        """,
        (user, bot)
    )

    conn.commit()
    conn.close()