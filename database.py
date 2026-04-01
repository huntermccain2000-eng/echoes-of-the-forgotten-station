import sqlite3

def save_game_history(player_name, ending, rooms_explored):

    try:
        conn = sqlite3.connect("game_history.db")
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

def show_game_history():

    conn = sqlite3.connect("game_history.db")
    cursor = conn.cursor()

    # ✅ ENSURE TABLE EXISTS
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