import sqlite3

def save_game_history(player_name, ending, rooms_explored):

    conn = sqlite3.connect("game_history.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GameHistory(
        player_name TEXT,
        ending TEXT,
        rooms_explored INTEGER
    )
    """)

    cursor.execute("""
    INSERT INTO GameHistory VALUES (?, ?, ?)
    """, (player_name, ending, rooms_explored))

    conn.commit()
    conn.close()