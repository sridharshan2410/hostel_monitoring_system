import cv2
import os
import time
import requests
from datetime import datetime, time as dt_time
from ultralytics import YOLO

# ==========================================
# CONFIGURATION
# ==========================================

CAMERA_ID = "CAM-01"
LOCATION = "Main Gate"

SERVER_URL = "http://127.0.0.1:5000/api/alerts"

START_TIME = dt_time(21,30)     # 9:30 PM
END_TIME = dt_time(5,0)         # 5:00 AM

CONFIDENCE = 0.50
COOLDOWN = 5

SAVE_FOLDER = "alerts"

# ==========================================
# CREATE FOLDER
# ==========================================

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# ==========================================
# LOAD MODEL
# ==========================================

model = YOLO("yolov8n.pt")

# ==========================================
# CAMERA
# ==========================================

cap = cv2.VideoCapture(0)

ret, frame = cap.read()

if not ret:
    print("Camera Not Found")
    exit()

h, w = frame.shape[:2]

# ==========================================
# RESTRICTED AREA
# ==========================================

rx1 = int(w*0.30)
ry1 = int(h*0.20)

rx2 = int(w*0.70)
ry2 = int(h*0.80)

# ==========================================
# COLORS
# ==========================================

GREEN = (0,255,0)
RED = (0,0,255)
BLUE = (255,0,0)
WHITE = (255,255,255)

last_capture = 0

# ==========================================
# TIME CHECK
# ==========================================

def restricted_time():

    now = datetime.now().time()

    if START_TIME <= now or now <= END_TIME:
        return True

    return False

# ==========================================
# SEND ALERT
# ==========================================
def send_alert(image_path):

    filename = os.path.basename(image_path)

    detected_time = datetime.now()

    data = {

        "alert_type": "Intruder",

        "location": LOCATION,

        "camera_id": CAMERA_ID,

        "severity": "HIGH",

        "description": "Unauthorized person detected",

        "date": detected_time.strftime("%d-%m-%Y"),

        "time": detected_time.strftime("%I:%M:%S %p"),

        "timestamp": detected_time.strftime("%Y-%m-%d %H:%M:%S"),

        "image": filename

    }

    try:

        response = requests.post(SERVER_URL, json=data)

        print(response.text)

    except Exception as e:

        print("Website Offline")

        print(e)

#=========================================
# START
# ==========================================

print("------------------------------------")
print("HOSTEL SECURITY SYSTEM")
print("Camera :",CAMERA_ID)
print("Restricted Time : 9:30 PM - 5:00 AM")
print("------------------------------------")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    current = datetime.now()

    current_time = current.strftime("%d-%m-%Y %I:%M:%S %p")

    cv2.putText(frame,current_time,
                (20,30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                WHITE,
                2)

    cv2.rectangle(frame,
                  (rx1,ry1),
                  (rx2,ry2),
                  BLUE,
                  2)

    cv2.putText(frame,
                "Restricted Area",
                (rx1,ry1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                BLUE,
                2)

    # --------------------------------------

    if not restricted_time():

        cv2.putText(frame,
                    "NORMAL HOURS (Detection OFF)",
                    (20,70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    GREEN,
                    2)

        cv2.imshow("Hostel Security",frame)

        if cv2.waitKey(1)==ord('q'):
            break

        continue

    cv2.putText(frame,
                "RESTRICTED HOURS (Detection ON)",
                (20,70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                RED,
                2)

    # --------------------------------------

    results = model(frame,verbose=False)

    intruder = False

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            label = model.names[cls]

            confidence = float(box.conf[0])

            if label!="person":
                continue

            if confidence<CONFIDENCE:
                continue

            x1,y1,x2,y2 = map(int,box.xyxy[0])

            cx = (x1+x2)//2
            cy = (y1+y2)//2

            color = GREEN

            text = "Person"

            if rx1<cx<rx2 and ry1<cy<ry2:

                color = RED

                text = "INTRUDER"

                intruder = True

            cv2.rectangle(frame,
                          (x1,y1),
                          (x2,y2),
                          color,
                          2)

            cv2.circle(frame,
                       (cx,cy),
                       5,
                       color,
                       -1)

            cv2.putText(frame,
                        f"{text} {confidence:.2f}",
                        (x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color,
                        2)

    # --------------------------------------

    if intruder:

        cv2.putText(frame,
                    "SECURITY ALERT",
                    (20,110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    RED,
                    3)

        now = time.time()

        if now-last_capture>COOLDOWN:

            filename = datetime.now().strftime("%Y%m%d_%H%M%S")

            filepath = os.path.join(
                SAVE_FOLDER,
                f"intruder_{filename}.jpg"
            )

            cv2.imwrite(filepath,frame)

            print("\n==============================")
            print("INTRUDER DETECTED")
            print(filepath)
            print("==============================")

            send_alert(filepath)

            last_capture = now

    cv2.imshow("Hostel Security",frame)

    if cv2.waitKey(1)==ord('q'):
        break

cap.release()

cv2.destroyAllWindows()