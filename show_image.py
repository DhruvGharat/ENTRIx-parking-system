import cv2

# Load the image
image = cv2.imread("car.jpg")

# Check if image loaded properly
if image is None:
    print("Image not found. Make sure car.jpg is in the folder.")
else:
    # Display the image
    cv2.imshow("Car Image", image)

    # Wait for any key to close the window
    cv2.waitKey(0)

    # Close all OpenCV windows
    cv2.destroyAllWindows()
