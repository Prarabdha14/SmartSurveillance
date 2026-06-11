from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import sys

# Import custom monitoring and drawing modules
from modules.config import MAX_TRACKING_AGE, MODEL_NAME, VIDEO_PATH, COLOR_DEFAULT
from modules.loitering import LoiteringDetector
from modules.intrusion import IntrusionDetector
from modules.counter import LineCrossCounter
from modules.drawing import draw_zones, draw_hud, draw_global_banners

# Initialize deep learning models and tracking configurations
model = YOLO(MODEL_NAME)
tracker = DeepSort(max_age=MAX_TRACKING_AGE)

# Open Video Feed
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"Error: Could not open video file at '{VIDEO_PATH}'. Please verify folder and format.")
    sys.exit(1)

# Retrieve Video Dimensions Dynamically
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Calculate zone limits dynamically based on frame dimensions
# Loiter Zone (Yellow) is mapped to the middle-left block
loiter_coords = (int(width * 0.1), int(height * 0.25), int(width * 0.5), int(height * 0.75))
# Restricted Area (Red) is mapped to the middle-right block
restricted_coords = (int(width * 0.55), int(height * 0.25), int(width * 0.9), int(height * 0.75))
# Virtual Crossing Line (Cyan) divides the screen horizontally
line_y = int(height * 0.5)

# Instantiate Stateful Analytics Modules
loitering_detector = LoiteringDetector()
intrusion_detector = IntrusionDetector()
crossing_counter = LineCrossCounter()

frame_count = 0
print("Starting modular security tracking engine. Press 'q' to quit...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # YOLOv8 Person Detection
    results = model(frame)[0]
    detections = []

    for box in results.boxes:
        cls = int(box.cls[0])
        # Class 0 represents 'person' in the COCO dataset
        if cls == 0:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            w = x2 - x1
            h = y2 - y1
            detections.append(([x1, y1, w, h], conf, "person"))

    # DeepSORT Multi Object Tracking
    tracks = tracker.update_tracks(detections, frame=frame)

    active_ids_this_frame = set()
    inside_loiter_this_frame = []
    inside_restricted_this_frame = []

    # Draw semi-transparent monitoring zones and line crossing boundaries
    draw_zones(frame, loiter_coords, restricted_coords, line_y, width)

    # Process all active tracks in the frame
    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        active_ids_this_frame.add(track_id)

        # Retrieve bounding box coordinates
        tx1, ty1, tx2, ty2 = map(int, track.to_ltrb())

        # Centroid Calculation (bottom-center representing foot contact point)
        cx = int((tx1 + tx2) / 2)
        cy = int(ty2)

        # Spatial check validation
        is_in_loiter = (loiter_coords[0] <= cx <= loiter_coords[2]) and (loiter_coords[1] <= cy <= loiter_coords[3])
        is_in_restricted = (restricted_coords[0] <= cx <= restricted_coords[2]) and (restricted_coords[1] <= cy <= restricted_coords[3])

        # Track rendering properties
        color = COLOR_DEFAULT
        status_text = f"ID {track_id}"
        local_alert_text = None

        # 1. Update Loitering Detector
        loiter_color, loiter_text, loiter_alert, elapsed = loitering_detector.update(track_id, is_in_loiter)
        if is_in_loiter:
            inside_loiter_this_frame.append(track_id)
            color = loiter_color
            status_text = loiter_text
            local_alert_text = loiter_alert

        # 2. Update Intrusion Detector
        intrusion_color, intrusion_alert = intrusion_detector.update(track_id, is_in_restricted)
        if is_in_restricted:
            inside_restricted_this_frame.append(track_id)
            color = intrusion_color
            local_alert_text = intrusion_alert

        # 3. Update Line Crossing Counter
        crossing_counter.update(track_id, cy, line_y)

        # Draw box and metadata labels on the frame
        cv2.rectangle(frame, (tx1, ty1), (tx2, ty2), color, 2)
        cv2.putText(
            frame, status_text, (tx1, ty1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA
        )

        if local_alert_text:
            cv2.putText(
                frame, local_alert_text, (tx1, ty1 - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA
            )

        # Render centroid dot
        cv2.circle(frame, (cx, cy), 4, color, -1)

    # Clean up states for tracks that disappeared from the camera view
    loitering_detector.cleanup(active_ids_this_frame)
    intrusion_detector.cleanup(active_ids_this_frame)
    crossing_counter.cleanup(active_ids_this_frame)

    # 4. Render Global Alerts & HUD Stats Overlay
    loiter_alert_active = len(loitering_detector.alerted_tracks) > 0
    intrusion_alert_active = len(intrusion_detector.intrusion_alerted) > 0
    draw_global_banners(frame, loiter_alert_active, intrusion_alert_active)

    occupancy = crossing_counter.get_occupancy()
    draw_hud(frame, crossing_counter.entry_count, crossing_counter.exit_count, occupancy, width)

    # Frame summary logs printed to console (debug logs)
    print(f"Frame: {frame_count}")
    print(f"Tracks: {list(active_ids_this_frame)}")
    print(f"Inside Zone: {inside_loiter_this_frame}")
    print(f"Restricted Zone Occupants: {inside_restricted_this_frame}")
    print("-" * 30)

    # Display window output
    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Modular Security Analytics pipeline closed successfully.")