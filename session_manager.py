import json
from datetime import datetime

SESSION_FILE = "sessions.json"

def load_sessions():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=4)

def start_session(plate_number):
    sessions = load_sessions()
    sessions[plate_number] = {
        "entry_time": datetime.now().isoformat(),
        "active": True
    }
    save_sessions(sessions)
    return sessions[plate_number]

def get_session(plate_number):
    sessions = load_sessions()
    return sessions.get(plate_number, None)

def end_session(plate_number):
    sessions = load_sessions()
    if plate_number not in sessions or not sessions[plate_number]["active"]:
        return None
    sessions[plate_number]["active"] = False
    sessions[plate_number]["exit_time"] = datetime.now().isoformat()
    save_sessions(sessions)
    return sessions[plate_number]

def calculate_bill(entry_time_iso, exit_time_iso, rate_per_minute=1):
    entry = datetime.fromisoformat(entry_time_iso)
    exit = datetime.fromisoformat(exit_time_iso)
    minutes = (exit - entry).total_seconds() / 60
    return round(minutes * rate_per_minute, 2)
