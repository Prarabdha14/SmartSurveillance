from ultralytics import YOLO
import cv2
import sys

# Load YOLOv8 Nano model
model = YOLO("yolov8n.pt")

# Open video
video_path = "video/test.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video file at '{video_path}'. Please check the path and format.")
    sys.exit(1)

print("Processing video. Press 'q' to quit...")

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print("Reached the end of the video or failed to read frame.")
        break

    # Run detection (leveraging Apple Silicon GPU via device='mps' if supported)
    # YOLOv8 automatically falls back to CPU if MPS is unavailable.
    results = model(frame)

    # Draw boxes
    annotated_frame = results[0].plot()

    cv2.imshow("Smart Surveillance", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Video processing finished.")