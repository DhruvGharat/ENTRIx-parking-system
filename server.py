from flask import Flask, render_template
from database import get_active_session
from datetime import datetime
import os

app = Flask(__name__)

@app.get("/session/<plate>")
def session_page(plate):

    # Get session from database
    session = get_active_session(plate)

    if not session:
        return "<h1>No active parking session found for this vehicle.</h1>", 404

    entry_time, image_path = session

    # Convert entry time from database
    entry_dt = datetime.fromisoformat(entry_time)
    now_dt = datetime.now()

    # Calculate duration in minutes
    duration = round((now_dt - entry_dt).total_seconds() / 60, 1)

    # Price Calculation → ₹1 per minute (you can change this later)
    current_bill = round(duration * 1, 2)

    # If no image stored, fallback
    if not image_path or not os.path.exists(image_path):
        image_path = "/static/output_detected.jpg"

    return render_template(
        "session.html",
        startup="ENTRIx",
        plate=plate,
        entry_time=entry_time,
        current_time=now_dt.isoformat(),
        duration=duration,
        current_bill=current_bill,
        plate_image=image_path
    )


if __name__ == "__main__":
    app.run(debug=True)
