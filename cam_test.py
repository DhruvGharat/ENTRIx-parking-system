import cv2

cap = cv2.VideoCapture(1)  # change 1 to 2 or 3 if needed

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read from webcam")
        break

    cv2.imshow("Exit Cam Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
