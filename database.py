import sqlite3
from datetime import datetime

# ------------------- Initialize Database ------------------- #
def init_db():
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            plate TEXT,
            entry_time TEXT,
            exit_time TEXT
        )
    """)
    conn.commit()
    conn.close()

# Call DB init on import
init_db()


# ------------------- Start a session ------------------- #
def start_session(plate):
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sessions (plate, entry_time, exit_time)
        VALUES (?, ?, NULL)
    """, (plate, datetime.now().isoformat()))

    conn.commit()
    conn.close()


# ------------------- Get active (running) session ------------------- #
def get_active_session(plate):
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT plate, entry_time
        FROM sessions
        WHERE plate=? AND exit_time IS NULL
    """, (plate,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "plate": row[0],
            "entry_time": row[1]
        }
    return None


# ------------------- End session ------------------- #
def end_session(plate):
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET exit_time=?
        WHERE plate=? AND exit_time IS NULL
    """, (datetime.now().isoformat(), plate))

    conn.commit()
    conn.close()
