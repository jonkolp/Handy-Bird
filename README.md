


# 🐦 Flappy Bird Using Hand Gestures

[![Python Version](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Unity Version](https://img.shields.io/badge/Unity-2021.3%2B-black.svg?logo=unity)](https://unity.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-00C4B4.svg)](https://developers.google.com/mediapipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive, computer-vision controlled **Flappy Bird** game that bridges **Google MediaPipe** and **OpenCV** in Python with the **Unity 2D Game Engine** via low-latency local TCP sockets.

Instead of tapping a screen or pressing a spacebar, the player controls the bird's flight in real time using intuitive **hand gestures** captured by a webcam.

---

## 🎮 How It Works

```
      ┌─────────────────────────┐
      │      Webcam Stream      │
      └────────────┬────────────┘
                   │ Video Frames (RGB)
                   ▼
      ┌─────────────────────────┐
      │     Python (MP.py)      │
      │  - MediaPipe Hands      │
      │  - Finger Counting      │
      │  - TCP Server (:65432)  │
      └────────────┬────────────┘
                   │ 1-Byte TCP Stream (1 = Jump, 0 = Glide)
                   ▼
      ┌─────────────────────────┐
      │      Unity Engine       │
      │  - Bird.cs (TCP Client) │
      │  - Rigidbody2D Physics  │
      │  - Assignment.unity     │
      └─────────────────────────┘
```

1. **Computer Vision Backend ([`MP.py`](MP.py))**:
   - Captures real-time frames from your webcam.
   - Detects 21 3D hand landmarks using **MediaPipe Hands**.
   - Evaluates extended fingers using relative landmark positions (Index, Middle, Ring, Pinky, and Thumb).
   - Draws a live debug HUD overlay with FPS, connection status, and detected gesture.
   - Streams control signals over a local TCP socket (`127.0.0.1:65432`).

2. **Game Client ([`Assets/Bird.cs`](Assets/Bird.cs))**:
   - Connects to the Python server as a TCP client with **automatic reconnection**.
   - Consumes and drains the socket stream to ensure zero input lag.
   - Applies responsive 2D physics impulses with debouncing and mid-fall flap recovery.

---

## ✋ Gesture Controls

| Gesture | Finger Count | Signal | Bird Action |
| :--- | :---: | :---: | :--- |
| **Open Palm / 3+ Fingers** | $\ge 3$ fingers | `1` | **Flap / Jump** (Applies upward force) |
| **Fist / 0–2 Fingers** | $< 3$ fingers | `0` | **Glide / Descend** (Moves forward under gravity) |

---

## ✨ Features

- **Real-Time Hand Tracking**: Fast, high-accuracy landmark detection powered by Google MediaPipe.
- **Robust Network Protocol**: Non-blocking TCP server and buffer-draining client eliminate lag and desync.
- **Flexible Startup Order**: Auto-reconnect on both sides allows starting either Unity or Python first without crashing.
- **On-Screen Display (HUD)**: Real-time visual feedback on the camera feed showing connection state, raised fingers, active action, and FPS.
- **Responsive Physics**: Configurable jump force, horizontal speed, jump cooldown, and mid-fall recovery.
- **Customizable Thresholds**: Easily configure port, host, camera device, and sensitivity via CLI arguments or Unity Inspector.

---

## 📋 Prerequisites

- **Python**: `3.8` to `3.12` *(MediaPipe currently supports up to Python 3.12)*
- **Unity**: `2021.3 LTS`, `2022.3 LTS`, or newer (Unity 2D workspace)
- **Webcam**: Any built-in or USB camera

---

## 🚀 Quick Start Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/jonkolp/Handy-Bird.git
cd "Handy-Bird"
```

### Step 2: Set Up Python Environment
Create and activate a virtual environment:

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Step 3: Launch the Computer Vision Server
```bash
python MP.py
```
*A camera window titled **"Flappy Bird Gesture Controller"** will appear displaying your webcam feed and hand tracking.*

### Step 4: Run the Unity Game
1. Open **Unity Hub** and add/open this project folder.
2. In the **Project** window, navigate to `Assets/` and double-click [`Assignment.unity`](Assets/Assignment.unity) to open the scene.
3. Click the **Play** button ▶️ at the top of the Unity Editor.
4. Watch the console or Python HUD switch to `Unity: CONNECTED`.
5. Raise 3 or more fingers to flap, and lower them to glide!

---

## ⚙️ Configuration & Tuning

### Python CLI Options ([`MP.py`](MP.py))

```bash
python MP.py [OPTIONS]
```

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--host` | `str` | `127.0.0.1` | Local IP address for TCP socket server. |
| `--port` | `int` | `65432` | TCP port for communication. |
| `--camera` | `int` | `0` | Webcam index (0 for default built-in camera). |
| `--threshold` | `int` | `3` | Minimum raised fingers required to trigger a jump. |
| `--detection-confidence` | `float` | `0.7` | MediaPipe minimum hand detection confidence. |
| `--tracking-confidence` | `float` | `0.7` | MediaPipe minimum landmark tracking confidence. |
| `--no-gui` | `flag` | `False` | Run in headless mode without showing the OpenCV window. |

### Unity Inspector Settings ([`Assets/Bird.cs`](Assets/Bird.cs))

Select the **Bird** GameObject in the Unity Hierarchy to adjust parameters in the Inspector:

- **Jump Force** (`float`, default `5.0`): Magnitude of upward impulse applied per flap.
- **Forward Speed** (`float`, default `1.0`): Continuous horizontal travel speed.
- **Jump Cooldown** (`float`, default `0.2s`): Minimum duration between flaps to avoid rapid fluttering.
- **Reset Vertical Velocity On Jump** (`bool`, default `true`): Eliminates downward momentum before flapping for crisp control.
- **Stop Forward On Jump** (`bool`, default `false`): Pause horizontal movement while flap gesture is held.
- **Reconnect Interval** (`float`, default `2.0s`): Retry period when looking for the Python server.
- **Enable Debug Logging** (`bool`, default `false`): Output network flags and jump events in the Unity Console.

---

## 📂 Project Structure

```
Flappy Bird Using Hand Gestures/
├── Assets/
│   ├── Assignment.unity           # Primary playable game scene
│   ├── Assignment.unity.meta
│   ├── Bird.cs                    # Bird controller & TCP client script
│   ├── Bird.cs.meta
│   ├── Flappy Bird Sprites.png    # Spritesheet (bird, pipes, background)
│   ├── Flappy Bird Sprites.png.meta
│   └── Scenes/
│       ├── SampleScene.unity      # Default template scene
│       └── SampleScene.unity.meta
├── Assignment 2.mp4               # Gameplay demonstration video
├── MP.py                          # Python MediaPipe & OpenCV server
├── requirements.txt               # Python package dependencies
├── .gitignore                     # Git ignore rules for Unity & Python
├── .gitattributes                 # Line endings and Unity merge settings
├── ROADMAP.md                     # Architecture plans and future milestones
├── LICENSE                        # MIT License
└── README.md                      # Project documentation
```

---

## 🔧 Troubleshooting

<details>
<summary><b>1. "No module named 'cv2'" or "No module named 'mediapipe'"</b></summary>
Ensure you have activated your virtual environment where the requirements were installed:
```bash
pip install -r requirements.txt
```
If using Python 3.13 or 3.14, MediaPipe binary wheels may not yet be published for that specific version. Use Python 3.10, 3.11, or 3.12.
</details>

<details>
<summary><b>2. "Failed to open camera device index 0"</b></summary>
- Check if another application (Zoom, Teams, Discord, or browser) is currently using the webcam.
- If using an external USB webcam, try running with `--camera 1`.
</details>

<details>
<summary><b>3. Unity console warns "Connection attempt failed"</b></summary>
- Ensure `MP.py` is currently running in your terminal.
- Verify that both `MP.py` and `Bird.cs` are set to the same port (default: `65432`).
- The game will automatically keep retrying every 2 seconds until the server is online.
</details>

<details>
<summary><b>4. Controls feel delayed or sluggish</b></summary>
- The updated [`Bird.cs`](Assets/Bird.cs) drains the TCP stream to always read the latest packet. Ensure you are using the updated script.
- Check camera frame rate on the HUD. Poor lighting can cause webcams to drop to 15 FPS; brighter lighting improves camera responsiveness.
</details>

---

## 🗺️ Future Work & Contributing

Contributions, issues, and feature requests are welcome!  
Please see [**ROADMAP.md**](ROADMAP.md) for planned features including:
- Two-way communication (Score and Game Over detection sent back to Python).
- Switching to UDP or WebSockets for lower latency.
- Dynamic pipe procedural generation and scoreboard UI.
- Multi-gesture combos (pinch, thumbs up, peace sign).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
