# read_plate.py
from ultralytics import YOLO
import cv2
import easyocr

from session_manager import start_session
from qr_generator import create_qr

model = YOLO("runs/detect/train/weights/best.pt")
reader = easyocr.Reader(['en'])

IMAGE_PATH = "car.jpg"

# --------------------------
# 1. LOAD IMAGE
# --------------------------
img = cv2.imread(IMAGE_PATH)
if img is None:
    print("Error: Could not load image.")
    exit()

# --------------------------
# 2. DETECT PLATES
# --------------------------
results = model(img)

final_plate_text = None  # will store the chosen plate

for result in results:
    for box in result.boxes:
        # bounding box
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # crop plate region
        plate_crop = img[y1:y2, x1:x2]

        # --------------------------
        # 3. OCR ON CROP
        # --------------------------
        ocr_result = reader.readtext(plate_crop)

        if len(ocr_result) > 0:
            plate_text = ocr_result[0][1]  # extracted text
            plate_text_clean = plate_text.replace(" ", "").upper()

            print("Detected Plate Text:", plate_text_clean)

            # store first detected plate (you can make this smarter later)
            if final_plate_text is None:
                final_plate_text = plate_text_clean

            # draw bounding box on main image
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, plate_text_clean, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

# --------------------------
# 4. SAVE OUTPUT IMAGE
# --------------------------
cv2.imwrite("output_detected.jpg", img)
print("Saved output_detected.jpg")

# --------------------------
# 5. START SESSION + GENERATE QR
# --------------------------
if final_plate_text:
    session = start_session(final_plate_text)
    qr_path = create_qr(final_plate_text)

    print("\nSession started for:", final_plate_text)
    from database import create_session

    create_session(final_plate_text, "static/output_detected.jpg")
    print("Database updated for:", final_plate_text)
    print("QR generated at:", qr_path)
else:
    print("No plate detected. Session not started.")
