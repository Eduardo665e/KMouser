# KMouser

**KMouser** is a computer-vision-based spatial interaction system for Windows, designed to enable contactless computer control through hand gestures, body tracking, and depth-aware interaction.

The project combines computer vision, personalized spatial calibration, and gesture recognition to transform natural hand movements into virtual cursor control and Windows interface actions.

> **Status:** 🚧 Active development

---

## ✨ Features

### Current

- 📷 Webcam-based hand tracking
- 🖐️ Real-time hand landmark detection
- 👤 Head position tracking
- 🎯 Personalized screen calibration
- 🖱️ Virtual cursor visualization
- 📐 Perspective-based spatial mapping
- 🔄 Automatic camera reconnection
- 🧩 Modular sensor architecture

### Planned

- 🎮 Xbox 360 Kinect support
- 📏 Real-time 3D hand tracking
- 🧠 Depth-aware cursor positioning
- 🖱️ Native Windows mouse control
- ✋ Advanced gesture recognition
- 🪟 Gesture-based window management
- 🔄 Automatic Kinect tilt adjustment
- 👥 Improved multi-hand interaction

---

## 🧠 How It Works

KMouser separates sensing, interpretation, and interaction into independent layers.

```text
┌─────────────────────────────┐
│        Sensor Layer         │
├─────────────┬───────────────┤
│   Webcam    │    Kinect     │
│     2D      │   RGB + Depth │
└──────┬──────┴───────┬───────┘
       │              │
       └──────┬───────┘
              ▼
       ┌──────────────┐
       │ Gesture      │
       │ Engine       │
       └──────┬───────┘
              ▼
       ┌──────────────┐
       │ Spatial      │
       │ Interaction  │
       └──────┬───────┘
              ▼
       ┌──────────────┐
       │   Windows    │
       │   Interface  │
       └──────────────┘
```

The webcam mode uses 2D computer vision combined with personalized calibration to estimate the relationship between the user's hand position and the physical display.

Kinect mode is designed to use actual depth information, allowing KMouser to operate in three-dimensional space.

---

## 🎯 Calibration

Because camera placement, user position, and viewing angle vary between setups, KMouser uses a personalized calibration process.

The current calibration uses five reference points:

```text
●────────────────────●
│                    │
│         ●          │
│                    │
●────────────────────●
```

- Top-left
- Top-right
- Center
- Bottom-left
- Bottom-right

Each calibration point records the relationship between the screen position, the user's finger position, and the user's head position.

The calibration data is stored in:

```text
calibration.json
```

This allows the system to reproduce the spatial mapping during cursor testing.

---

## 🖱️ Virtual Cursor

The current development stage focuses on a **virtual cursor** rather than directly controlling the Windows mouse.

The tracking pipeline is approximately:

```text
Hand Detection
      ↓
Index Finger
      ↓
Head Position
      ↓
Relative Finger Position
      ↓
Spatial Transformation
      ↓
Screen Coordinates
      ↓
Virtual Cursor
```

This makes it possible to evaluate tracking accuracy before introducing actual Windows mouse input.

---

## 🎮 Kinect Integration

KMouser is designed to support the **Xbox 360 Kinect** as an optional high-precision sensor.

Unlike a conventional webcam, Kinect provides depth information that can be used to obtain real-world 3D coordinates.

```text
             Kinect
                │
        ┌───────┴───────┐
        ▼               ▼
       RGB            Depth
        │               │
        └───────┬───────┘
                ▼
          3D Position
          X / Y / Z
                │
                ▼
        Spatial Interaction
```

The Kinect's motorized tilt can also be used for adaptive framing.

If the user's hands move toward the edge of the sensor's vertical field of view, KMouser can potentially adjust the sensor orientation to keep the relevant body landmarks inside the tracking region.

---

## 🖥️ Windows Integration

The long-term goal is to translate spatial gestures into native Windows interactions.

Potential interactions include:

| Gesture | Action |
|---|---|
| ☝️ Index finger | Cursor movement |
| ✋ Hand movement | Scrolling |
| 👋 Rapid lateral movement | Window switching |
| 👉 Directional gesture | Window snapping |
| 🖐️ Multiple fingers | Additional interaction modes |

These interactions are part of the development roadmap and may change as the tracking system evolves.

---

## 🛠️ Technology Stack

- **Python**
- **OpenCV**
- **MediaPipe**
- **MediaPipe Tasks**
- **NumPy**
- **Xbox 360 Kinect** *(optional / planned)*

### Computer Vision

OpenCV is used for camera capture and image processing.

MediaPipe provides hand and face landmark detection.

The Kinect integration is intended to provide depth-aware tracking and 3D spatial coordinates.

---

## 📁 Project Structure

```text
KMouser/
│
├── main.py
├── calibration.py
├── cursor_test.py
├── KMouser.bat
├── calibration.json
│
├── models/
│   ├── hand_landmarker.task
│   └── face_landmarker.task
│
└── README.md
```

---

## 💻 Requirements

### Webcam Mode

- Windows
- Python 3.14+
- Functional webcam
- OpenCV
- MediaPipe
- NumPy

### Kinect Mode

Additionally requires:

- Xbox 360 Kinect sensor
- Kinect-to-PC power/data adapter
- Compatible Kinect drivers/runtime
- USB connection

---

## 🚀 Running

Clone the repository:

```bash
git clone https://github.com/USERNAME/KMouser.git
cd KMouser
```

Install the Python dependencies:

```bash
python -m pip install opencv-python mediapipe numpy
```

Then launch:

```text
KMouser.bat
```

The launcher provides the main development options:

```text
========================================
              KMouser
========================================

  [1] Start KMouser
  [2] Calibrate system
  [3] Test cursor
  [4] Exit
```

---

## ⚠️ Development Status

KMouser is currently an experimental project.

The webcam tracking pipeline is functional, including:

- hand landmark detection;
- face/head tracking;
- personalized calibration;
- virtual cursor mapping.

Native Windows mouse control and Kinect-based 3D tracking are still under development.

The current implementation is primarily intended for experimentation, calibration, and evaluation of spatial tracking accuracy.

---

## 🗺️ Roadmap

### Phase 1 — Vision Foundation
- [x] Webcam capture
- [x] Hand tracking
- [x] Face/head tracking
- [x] Calibration system
- [x] Virtual cursor
- [x] Camera reconnection

### Phase 2 — Spatial Interaction
- [ ] Improve calibration accuracy
- [ ] Adaptive smoothing
- [ ] Better depth estimation
- [ ] Gesture recognition
- [ ] Cursor stability improvements

### Phase 3 — Kinect
- [ ] Kinect connection
- [ ] RGB + depth integration
- [ ] Real 3D coordinates
- [ ] Kinect skeletal tracking
- [ ] Adaptive sensor tilt

### Phase 4 — Windows Control
- [ ] Native cursor control
- [ ] Mouse buttons
- [ ] Scrolling
- [ ] Window management
- [ ] Advanced gesture commands

---

## 📜 License

License information will be added as the project approaches a stable release.

---

## 👨‍💻 Project

**KMouser** is an experimental project exploring the use of computer vision and spatial tracking as an alternative interaction method for Windows.

The project is being developed incrementally, starting with accessible webcam hardware and progressively expanding toward depth-aware 3D interaction using Kinect.