import cv2
from ultralytics import YOLO
import easyocr
from database import get_active_session, end_session
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import threading


# ---------------- Payment Popup (Threaded) ---------------- #
def show_payment_popup(plate, entry_time, exit_time, duration, total_bill):
    win = tk.Tk()
    win.title("ENTRIx - Final Bill")
    win.geometry("380x520")
    win.configure(bg="#0d1117")

    title = tk.Label(win, text="Final Bill", bg="#0d1117", fg="#4da6ff",
                     font=("Arial", 18, "bold"))
    title.pack(pady=10)

    info_text = f"""
Plate Number:  {plate}

Entry Time:    {entry_time}
Exit Time:     {exit_time}

Duration:      {duration:.1f} minutes
Total Bill:    ₹{total_bill:.2f}
"""
    info = tk.Label(win, text=info_text, justify="left",
                    bg="#0d1117", fg="white", font=("Arial", 12))
    info.pack()

    # Dummy payment QR
    img = Image.open("static/payment_qr.png")
    img = img.resize((260, 260))
    img_tk = ImageTk.PhotoImage(img)

    qr_label = tk.Label(win, image=img_tk, bg="#0d1117")
    qr_label.image = img_tk
    qr_label.pack(pady=10)

    footer = tk.Label(win, text="Scan to Pay & Exit",
                      bg="#0d1117", fg="#2ecc71", font=("Arial", 14))
    footer.pack(pady=5)

    win.attributes("-topmost", True)
    win.mainloop()


# ---------------- Load Models ---------------- #
model = YOLO("runs/detect/train/weights/best.pt")
reader = easyocr.Reader(['en'])

# ---------------- Camera Setup ---------------- #
# Try external cam first (1), fallback to internal (0)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("External camera unavailable. Switching to internal camera.")
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

last_plate = None

print("\n🚗 ENTRIx Exit Gate Activated")
print("Waiting for vehicles to exit...\n")


# ---------------- Main Loop ---------------- #
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠ Camera not found or disconnected.")
        break

    results = model(frame)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = frame[y1:y2, x1:x2]

            # Improve OCR read accuracy
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )
            thresh = cv2.resize(thresh, None, fx=2, fy=2,
                                interpolation=cv2.INTER_CUBIC)

            ocr = reader.readtext(thresh)
            if len(ocr) == 0:
                continue

            # Extract text
            plate = ocr[0][1].replace(" ", "").upper()
            allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            plate = "".join(ch for ch in plate if ch in allowed)

            if len(plate) < 6:
                continue

            # Prevent multiple triggers
            if plate == last_plate:
                continue
            last_plate = plate

            print(f"EXIT Gate Detected Plate: {plate}")

            # --- Check if car actually has an entry session ---
            session = get_active_session(plate)
            if not session:
                print("⚠ No active session found — ignoring.")
                continue

            entry_time = datetime.fromisoformat(session["entry_time"])
            exit_time_dt = datetime.now()
            duration = (exit_time_dt - entry_time).total_seconds() / 60

            rate = 1.0  # ₹ per minute
            total_bill = duration * rate

            end_session(plate)

            # Show final popup (threaded)
            threading.Thread(
                target=show_payment_popup,
                args=(plate,
                      session["entry_time"],
                      exit_time_dt.strftime("%Y-%m-%d %H:%M:%S"),
                      duration,
                      total_bill),
                daemon=True
            ).start()

            print("💰 Final Bill Popup Triggered.")

    cv2.imshow("ENTRIx Exit Gate Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
