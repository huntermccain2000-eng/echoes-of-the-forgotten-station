import sqlite3
import os


def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "game_history.db")


# ---------------- SAVE HISTORY ---------------- #
def save_game_history(player_name, ending, rooms_explored):

    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GameHistory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            ending TEXT,
            rooms_explored INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        INSERT INTO GameHistory (player_name, ending, rooms_explored)
        VALUES (?, ?, ?)
        """, (player_name, ending, rooms_explored))

        conn.commit()

    except Exception as e:
        print("Database error:", e)

    finally:
        conn.close()


# ---------------- SHOW HISTORY ---------------- #
def show_game_history():

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # ensure table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GameHistory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        ending TEXT,
        rooms_explored INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("SELECT * FROM GameHistory")
    rows = cursor.fetchall()

    print("\n--- GAME HISTORY ---")

    if not rows:
        print("No games played yet.")
    else:
        for row in rows:
            print(f"Player: {row[1]} | Ending: {row[2]} | Rooms: {row[3]} | Time: {row[4]}")

    conn.close()