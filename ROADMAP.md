# 🗺️ Project Roadmap & Future Work

This document outlines architectural improvements, planned features, and research directions for the **Flappy Bird Hand Gesture Project**. It serves as a guide for future contributors and developers extending this codebase.

---

## 🎯 Milestones Overview

- [x] **Phase 1: Proof of Concept & Foundation** *(Completed)*
  - Real-time hand landmark detection using MediaPipe.
  - Local TCP socket bridge between Python and Unity.
  - Basic bird jumping and physics simulation.
- [ ] **Phase 2: Game Loop Completion & Audio** *(Planned)*
  - Procedural obstacle generation, score counter, death states, and retro sound effects.
- [ ] **Phase 3: Network Protocol Upgrade (UDP & Bidirectional Sync)** *(Planned)*
  - Low-latency UDP streaming, bidirectional telemetry, and HUD sync.
- [ ] **Phase 4: Advanced Gesture Interaction & Accessibility** *(Planned)*
  - Multi-gesture recognition (dive, glide, restart), auto-calibration, and multi-player support.
- [ ] **Phase 5: Packaging & Web Deployment** *(Future)*
  - Standalone single-click installer and browser-based WebGL/WebAssembly edition.

---

## 🏗️ Detailed Work Items

### 1. Game Loop & Gameplay Mechanics (Unity)

The current Unity scene ([`Assignment.unity`](Assets/Assignment.unity)) demonstrates character movement with static obstacle sprites. The next step is a complete, self-sustaining game loop:

#### A. Procedural Pipe Spawner
- **Problem**: Static pipes limit replayability.
- **Task**: Create a `PipeSpawner.cs` script that periodically instantiates pipe pairs with randomized vertical offsets:
  ```csharp
  // Suggested architecture:
  public class PipeSpawner : MonoBehaviour
  {
      public GameObject pipePrefab;
      public float spawnRate = 1.5f;
      public float heightRange = 1.2f;
      // Object pooling for performance optimization
  }
  ```
- **Object Pooling**: Implement an object pool for pipe GameObjects to avoid garbage collection spikes in 2D physics.

#### B. Score Tracking & UI
- Add trigger colliders midway through pipe gaps.
- When the bird passes the trigger, increment the score.
- Render the score using the retro digit sprites available in [`Flappy Bird Sprites.png`](Assets/Flappy%20Bird%20Sprites.png).
- Store `HighScore` using Unity's `PlayerPrefs`.

#### C. Collision & Game Over State Machine
- Implement state transitions: `Ready` ➔ `Playing` ➔ `GameOver`.
- Add collision callbacks (`OnCollisionEnter2D`) on ground and pipe colliders.
- Render a "Game Over" canvas displaying Current Score, Best Score, and a "Show Thumbs-Up to Restart" prompt.

#### D. Audio Feedback
- Add `AudioSource` triggers for:
  - Wing flap sound (`sfx_wing.wav`).
  - Score increment chime (`sfx_point.wav`).
  - Collision impact sound (`sfx_hit.wav`).
  - Fall sound (`sfx_die.wav`).

---

### 2. Network Architecture & Protocol Evolution

Currently, control signals are transferred via a one-way raw byte stream over TCP. While robust with buffer-draining, further refinements include:

```
┌─────────────────────────┐               ┌─────────────────────────┐
│     Python Backend      │   UDP Stream  │      Unity Client       │
│  - Gesture Telemetry    ├──────────────►│  - Low-Latency Controls │
│  - On-Screen Stats      │◄──────────────┤  - Game State & Score   │
└─────────────────────────┘  Telemetry    └─────────────────────────┘
```

#### A. Transition to UDP (User Datagram Protocol)
- **Rationale**: For real-time gesture input, timely delivery is far more important than guaranteed delivery. TCP's retransmission overhead is unnecessary for continuous 60 FPS sensor data.
- **Task**:
  - Python: Use `socket(AF_INET, SOCK_DGRAM)` to send packets.
  - Unity: Use `UdpClient` with a non-blocking `BeginReceive` callback.

#### B. Bidirectional Telemetry (Two-Way Communication)
- **Goal**: Enable Unity to send game state back to Python:
  - Current Game State: `START`, `PLAYING`, `GAMEOVER`.
  - Player Score: Update Python's on-screen OpenCV HUD to display live score and game over notifications.
- **Protocol Format**: Adopt a compact JSON or binary struct:
  ```json
  // Python -> Unity
  {
    "action": "jump",
    "fingers": 4,
    "confidence": 0.94,
    "timestamp": 1729000000
  }

  // Unity -> Python
  {
    "state": "playing",
    "score": 14,
    "high_score": 28
  }
  ```

---

### 3. Gesture Recognition & Computer Vision (Python)

#### A. Rich Multi-Gesture Control Set

Expand beyond binary (Jump / Glide) by supporting expressive gesture primitives:

| Gesture | Landmark Rule | Action |
| :--- | :--- | :--- |
| **Open Palm ($\ge 4$ Fingers)** | All fingertips above joints | Regular Flap |
| **Pinch (Thumb + Index)** | Tip Euclidean distance $< 0.05$ | Fast Dive / Downward Dash |
| **Thumbs Up** | Thumb extended, 4 fingers folded | Restart Game (on Game Over) |
| **Fist ($\le 1$ Finger)** | All fingertips folded | Pause Game |

#### B. Dynamic User Calibration
- Hand sizes and distances from the webcam vary between users.
- Add an initial 3-second calibration phase where the user opens and closes their hand to calculate personalized baseline joint distances.

#### C. Two-Player Mode (Dual Hand Tracking)
- Set `max_num_hands=2` in MediaPipe.
- Map the left hand to **Player 1** (Red Bird) and right hand to **Player 2** (Blue Bird) for local co-op or versus mode.

---

### 4. Packaging & Portability

#### A. Single-Click Launch Scripts
Create desktop launcher scripts so non-technical users can launch the game without using a terminal:
- `start_game.bat` (Windows): Launches virtual environment, starts `MP.py` in the background, and launches the Unity standalone `.exe`.
- `start_game.sh` (macOS/Linux): Bash equivalent.

#### B. WebGL / In-Browser Edition
- Port the MediaPipe backend to **MediaPipe JavaScript Solutions** (`@mediapipe/camera_utils`, `@mediapipe/hands`).
- Build Unity for **WebGL**.
- Execute both the CV pipeline and game inside the browser with zero installation!

---

## 💡 How to Contribute

Interested in implementing any of these features?
1. Check the [open issues](https://github.com/your-username/flappy-bird-hand-gestures/issues) or open a new issue proposing your implementation.
2. Fork the repository and create a feature branch (`git checkout -b feature/procedural-spawner`).
3. Commit your changes with clear, descriptive commit messages.
4. Open a Pull Request referencing the roadmap item.
