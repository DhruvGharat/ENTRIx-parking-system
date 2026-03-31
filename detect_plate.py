from ultralytics import YOLO
import cv2

# Load model directly from Ultralytics HUB (auto-download)
model = YOLO("ultralytics/license-plate-detection")

# Load your image
img = cv2.imread("car.jpg")

# Run detection
results = model(img)

# Draw boxes
for r in results:
    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

# Show output
cv2.imshow("Plate Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
                            