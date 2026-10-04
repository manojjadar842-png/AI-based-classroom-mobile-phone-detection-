# AI Classroom Monitor

 AI-Based Mobile Phone Detection for Classrooms

AI Classroom Monitor is a computer-vision-based classroom monitoring system that detects mobile phone usage through a webcam and automatically alerts the teacher.

The system uses YOLOv8 for object detection, OpenCV for camera processing, Flask for communication between the AI camera and server, and CSV logging for maintaining an incident history.

---

🎯 Problem Statement

Mobile phone usage during classroom sessions can distract students and affect the learning environment.

Teachers cannot continuously monitor every student while simultaneously conducting a class. Manual monitoring is also difficult and does not provide a structured record of incidents.

There is a need for a simple AI-based system that can automatically detect mobile phones and notify the teacher.

---

Our Solution

AI Classroom Monitor uses a classroom webcam and YOLOv8 object detection to identify mobile phones.

When a phone is detected:

1. The AI camera detects the phone.
2. The system checks the detection confidence.
3. A phone-use event is generated.
4. The event is sent to a Flask server.
5. The teacher receives a desktop notification.
6. The incident is recorded in a CSV file.
7. The record includes date, time, subject, period and classroom information.

---

 System Workflow

```text
Classroom Webcam
       ↓
   OpenCV
       ↓
    YOLOv8
       ↓
Phone Detection
       ↓
   Flask Server
       ↓
Teacher Notification
       ↓
   Incident Log
       ↓
      CSV
