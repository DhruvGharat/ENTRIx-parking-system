import cv2
from ultralytics import YOLO
import easyocr
from database import start_session, get_active_session
import qrcode
import os
import threading
import time
import queue
import tkinter as tk
from PIL import Image, ImageTk


# =============== POPUP MESSAGE QUEUE =============== #
popup_queue = queue.Queue()


# =============== TKINTER THREAD =============== #
def tkinter_thread():
    """Runs a dedicated Tkinter loop to display popups safely."""
    root = tk.Tk()
    root.withdraw()  # hide main window

    def process_queue():
        try:
            while True:
                plate, qr_path = popup_queue.get_nowait()
                show_qr_popup(root, plate, qr_path)
        except queue.Empty:
            pass

        root.after(200, process_queue)

    process_queue()
    root.mainloop()


def show_qr_popup(root, plate, qr_path):
    """Create popup in Tkinter mainloop thread."""
    popup = tk.Toplevel(root)
    popup.title("ENTRIx - Entry QR Code")
    popup.geometry("350x450")
    popup.configure(bg="#0d1117")

    title = tk.Label(popup, text="Scan to Start Session",
                     font=("Arial", 16, "bold"),
                     bg="#0d1117", fg="#58a6ff")
    title.pack(pady=10)

    plate_label = tk.Label(popup, text=f"Plate: {plate}",
                           font=("Arial", 13),
                           bg="#0d1117", fg="white")
    plate_label.pack(pady=5)

    img = Image.open(qr_path).resize((260, 260))
    img_tk = ImageTk.PhotoImage(img)

    qr_label = tk.Label(popup, image=img_tk, bg="#0d1117")
    qr_label.image = img_tk
    qr_label.pack(pady=10)

    footer = tk.Label(popup, text="Scan QR to view live billing",
                      bg="#0d1117", fg="#2ecc71",
                      font=("Arial", 12))
    footer.pack(pady=5)

    popup.attributes("-topmost", True)

    # Auto-close after 8 seconds
    popup.after(8000, popup.destroy)


# Start Tkinter in its own thread
threading.Thread(target=tkinter_thread, daemon=True).start()


# =============== ML + OCR SYSTEM =============== #

model = YOLO("runs/detect/train/weights/best.pt")
reader = easyocr.Reader(['en'])

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

last_plate = None
os.makedirs("qr_codes", exist_ok=True)

print("\n🚗 ENTRIx Entry Gate Activated")
print("Waiting for vehicles...\n")


# =============== MAIN DETECTION LOOP =============== #
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠ Camera not available")
        break

    results = model(frame)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            crop = frame[y1:y2, x1:x2]

            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            ocr = reader.readtext(gray)

            if len(ocr) == 0:
                continue

            plate = ocr[0][1].replace(" ", "").upper()
            allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            plate = "".join(c for c in plate if c in allowed)

            if len(plate) < 6:
                continue

            if plate == last_plate:
                continue
            last_plate = plate

            print(f"\nENTRY Gate Detected Plate: {plate}")

            session = get_active_session(plate)
            if not session:
                start_session(plate)
                print(f"🟢 Session started for {plate}")

            # Generate QR
            billing_url = f"http://127.0.0.1:5000/live_bill/{plate}"
            qr_path = f"qr_codes/{plate}.png"
            qrcode.make(billing_url).save(qr_path)

            print("📱 Showing QR popup...")

            # SEND MESSAGE TO TKINTER THREAD
            popup_queue.put((plate, qr_path))

    cv2.imshow("ENTRIx Entry Gate Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
