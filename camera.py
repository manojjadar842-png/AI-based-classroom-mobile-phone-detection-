import cv2
from ultralytics import YOLO
import requests
import time
import csv
import os
from datetime import datetime
import sys
import numpy as np

# Load the AI model
print("Loading YOLO model...")
model = YOLO("yolov8n.pt")
print("✓ YOLO model loaded successfully!")

# Open the webcam
print("\nAttempting to access camera (index 0)...")
cap = cv2.VideoCapture(0)
camera_works = cap.isOpened() if cap is not None else False

CSV_FILE = "phone_infractions.csv"
URL = "http://127.0.0.1:8080/"

last_log_time = 0
COOLDOWN_SECONDS = 5

if camera_works:
    print(f"✓ Camera ready! Logging detections to {CSV_FILE}")
else:
    cap = None
    print(f"✓ Fallback mode active. Logging to {CSV_FILE}")

def direct_local_log():
    """Write detections to CSV and fall back if the primary file path is locked or unwritable."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%I:%M %p")

    primary_path = os.path.abspath(CSV_FILE)
    fallback_path = os.path.join(os.path.expanduser("~"), "phone_infractions.csv")
    candidates = [primary_path, fallback_path]
    last_error = None

    for target_path in candidates:
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            file_exists = os.path.exists(target_path)
            with open(target_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Date", "Time Logged", "Target ID", "Captured Label", "Status"])
                writer.writerow([date_str, time_str, "AUTO_CAMERA_01", "Classroom Camera Zone 1", "Saved Locally"])
            print(f"📁 SUCCESS: Saved directly to {target_path}")
            return
        except PermissionError as exc:
            last_error = exc
            continue

    print(f"⚠️ Unable to write to CSV file. Last error: {last_error}")

print("\n🎥 NEW AI Camera Monitoring active... Press 'q' to stop.\n")

frame_count = 0
error_count = 0
test_frame_num = 0

while True:
    # Handle both real camera and fallback mode
    if cap is not None:
        # Real camera mode
        success, frame = cap.read()
        if not success:
            error_count += 1
            if error_count > 5:
                print(f"❌ Cannot read from camera (failed {error_count} times). Exiting.")
                break
            time.sleep(0.5)
            continue
        error_count = 0
    else:
        # Fallback/test mode - create synthetic frame
        test_frame_num += 1
        if test_frame_num % 50 == 0:
            # Create a test frame with some content every 50 frames
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "TEST MODE - No Camera Found", (100, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Connect a webcam to use real camera", (80, 280), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1)
        else:
            # Skip processing for empty frames in test mode
            if test_frame_num % 100 == 0:
                print(f"[TEST MODE] Frame {test_frame_num} - Ready for real camera")
            time.sleep(0.03)
            continue
    
    frame_count += 1

    # Run AI object detection
    results = model(frame, verbose=False)
    phone_detected = False

    for result in results:
        for box in result.boxes:
            obj_name = model.names[int(box.cls)]
            confidence = float(box.conf)

            if obj_name == "cell phone" and confidence > 0.4:
                phone_detected = True
                
                # FIXED MATRIX CONVERSION HERE: 
                # .xyxy[0].tolist() cleanly extracts the 4 bounding box coordinates
                try:
                    coords = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = map(int, coords)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                except Exception:
                    pass

    if phone_detected:
        current_time = time.time()
        if current_time - last_log_time > COOLDOWN_SECONDS:
            print("\n🚨 [AI ALERT] Phone detected!")
            
            # ALWAYS SAVE TO THE EXCEL FILE IMMEDIATELY
            direct_local_log()
            
            # Try to sync with server, but do NOT crash if it fails
            try:
                requests.post(URL, json={"student_id": "AUTO_CAMERA_01"}, timeout=1)
                print("📡 Server sync complete.")
            except Exception:
                print("📡 Server offline - skipping web sync.")
                
            last_log_time = current_time

    # Display the live video feed window safely
    try:
        cv2.imshow("Classroom AI Monitor", frame)
    except Exception:
        pass

    # Press 'q' on your keyboard while focusing on the video window to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Stopping script via 'q' key.")
        break

if cap is not None:
    cap.release()
cv2.destroyAllWindows()
print(f"\n✓ Monitoring stopped. Processed {frame_count} frames.")