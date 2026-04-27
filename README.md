# 🤖 AI Tracking Car with Raspberry Pi + ESP32 + Ultrasonic Motor Control

This project is a **smart tracking car** that follows a person using computer vision.

It combines:
- A **Raspberry Pi 4B** with camera for AI-based person detection
- An **ESP32** for real-time motor control
- An **L293D motor driver** controlling TT motors

The system detects a person, determines their position and distance, and moves the car accordingly.

---

## 🎯 Features

- Real-time person detection using AI (MobileNet SSD)
- Automatic tracking (left, center, right)
- Distance-based movement (forward, backward, stop)
- WiFi communication between Raspberry Pi and ESP32
- HTTP-based command system
- Autonomous movement logic

---

## 🧩 Components

- Raspberry Pi 4B
- Raspberry Pi Camera Rev 1.3
- ESP32
- L293D motor driver
- 2x TT DC motors
- Power supply (battery pack)
- Chassis (car frame)

---

## 🧠 How It Works

1. The Raspberry Pi camera captures video frames
2. A neural network detects the person in the frame
3. The system determines:
   - Horizontal position → LEFT / CENTER / RIGHT
   - Distance → FAR / MEDIUM / NEAR
4. A message is generated (example: `SINISTRA_LONTANA`)
5. The message is sent via HTTP to the ESP32
6. The ESP32 interprets the message and controls the motors

---

## 📡 Communication

- Protocol: HTTP (GET request)
- Endpoint: http://esp32.local/cmd?msg=VALUE

### Example messages:

- `SINISTRA_LONTANA`
- `DESTRA_VICINA`
- `CENTRO_MEDIA`
- `NESSUNA_PERSONA`

---

## 🚗 Movement Logic

### CENTER
- FAR → move forward
- NEAR → move backward
- MEDIUM → stop

### LEFT
- Activate right motors to turn toward the person

### RIGHT
- Activate left motors to turn toward the person

### NO PERSON
- Stop all motors

---

## 🔌 Hardware Connections (ESP32 + L293D)

| L293D | ESP32 |
|------|------|
| IN1  | GPIO 25 |
| IN2  | GPIO 33 |
| IN3  | GPIO 32 |
| IN4  | GPIO 26 |

- IN1/IN2 → left motor
- IN3/IN4 → right motor

---

## 📷 AI Detection (Raspberry Pi)

- Model: MobileNet SSD (Caffe)
- Input resolution: 640x480
- Only the **person** class is used
- Confidence threshold filtering applied
- Bounding box size used to estimate distance

---

## 🌐 Network Requirements

- Raspberry Pi and ESP32 must be on the same WiFi network
- ESP32 is accessible via: http://esp32.local

(mDNS enabled)

---

## ⚙️ Configuration

Before running the project:

- Set WiFi credentials on ESP32
- Configure ESP32 endpoint URL in Raspberry Pi script
- Ensure correct model paths on Raspberry Pi
- Power the motors properly (external supply recommended)

---

## 🚀 Getting Started

1. Upload the firmware to the ESP32  
2. Connect ESP32 to WiFi  
3. Assemble the car (motors + driver + power)  
4. Connect Raspberry Pi camera  
5. Run the Python tracking script on Raspberry Pi  
6. Place a person in front of the camera  

The car will start following automatically.

---

## ⚠️ Notes

- Motor direction depends on wiring  
  → If motors spin in the wrong direction, swap HIGH/LOW logic in the motor control pins  

- It is normal that:
  - One motor spins forward
  - The other spins backward  

  This depends entirely on how motors are connected

- Detection accuracy depends on:
  - Lighting conditions
  - Camera angle
  - Distance from subject

- Avoid obstacles in front of the car

---

## 📊 Possible Improvements

- Add obstacle avoidance (ultrasonic sensors)
- Use PWM for speed control
- Add object tracking instead of detection
- Implement smoother movement (PID control)
- Add battery monitoring system
- Create web dashboard

---

## 👨‍💻 Matteo Dalla Pozza

AI-powered tracking car built with Raspberry Pi, ESP32, and computer vision.
