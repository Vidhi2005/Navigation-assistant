import cv2

print("Testing webcam...")
print("Press 'q' to quit")

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

# Check if camera opened
if not cap.isOpened():
    print("ERROR: Cannot open webcam!")
    print("Solutions:")
    print("1. Check if another app is using camera")
    print("2. Try changing 0 to 1: cap = cv2.VideoCapture(1)")
    exit()

print("✅ Webcam working! Window should open...")

while True:
    # Read frame
    ret, frame = cap.read()
    
    if not ret:
        print("ERROR: Can't receive frame")
        break
    
    # Display frame
    cv2.imshow('Webcam Test - Press Q to quit', frame)
    
    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Test complete!")