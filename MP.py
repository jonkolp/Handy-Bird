#!/usr/bin/env python3
"""
Flappy Bird Hand Gesture Controller (MediaPipe Backend)
======================================================
Captures real-time webcam video, processes hand landmarks using Google MediaPipe,
computes raised finger counts, and streams control signals to Unity over a local TCP socket.

Controls:
  - Raised fingers >= 3: Flap / Jump signal (Flag 1)
  - Raised fingers <  3: Cruise / Fall signal (Flag 0)
  - Press 'q' or 'ESC' to exit.
"""

import argparse
import socket
import sys
import time
import math
cv2 = None
mp = None


def ensure_dependencies():
    """Ensure optional heavy libraries (cv2, mediapipe) are installed."""
    global cv2, mp
    if cv2 is not None and mp is not None:
        return
    try:
        import cv2 as _cv2
        import mediapipe as _mp
        cv2 = _cv2
        mp = _mp
    except ImportError as err:
        print(f"\n[Error] Missing required Python package: {err.name}")
        print("Please install the dependencies via:")
        print("    pip install -r requirements.txt\n")
        sys.exit(1)


def parse_arguments():
    """Parse command line arguments with sensible defaults."""
    parser = argparse.ArgumentParser(
        description="Hand gesture controller for Flappy Bird Unity game."
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind the TCP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=65432,
        help="Port number to bind the TCP server (default: 65432)",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Webcam device index (default: 0)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=3,
        help="Minimum number of raised fingers to trigger a jump (default: 3)",
    )
    parser.add_argument(
        "--detection-confidence",
        type=float,
        default=0.7,
        help="MediaPipe minimum detection confidence (default: 0.7)",
    )
    parser.add_argument(
        "--tracking-confidence",
        type=float,
        default=0.7,
        help="MediaPipe minimum tracking confidence (default: 0.7)",
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run without displaying the OpenCV debug window",
    )
    return parser.parse_args()


def count_raised_fingers(hand_landmarks, handedness="Right"):
    """
    Count the number of raised fingers on a detected hand.

    Args:
        hand_landmarks: MediaPipe normalized hand landmarks.
        handedness: "Right" or "Left" label (from mirrored perspective).

    Returns:
        int: Number of raised fingers (0 to 5).
    """
    landmarks = hand_landmarks.landmark
    mp_hands = mp.solutions.hands

    # Define tip and PIP (proximal interphalangeal) joints for 4 fingers
    fingers = [
        (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP),
    ]

    count = 0

    # 1. Check 4 fingers (tip higher than PIP joint in image coordinates where y=0 is top)
    for tip, pip in fingers:
        if landmarks[tip].y < landmarks[pip].y:
            count += 1

    # 2. Check Thumb
    # Using relative distance to Pinky MCP joint:
    # When thumb is extended outward, thumb tip distance to pinky knuckle is significantly
    # larger than thumb IP (interphalangeal) joint distance to pinky knuckle.
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp_hands.HandLandmark.THUMB_IP]
    pinky_mcp = landmarks[mp_hands.HandLandmark.PINKY_MCP]

    dist_tip_to_pinky = math.hypot(thumb_tip.x - pinky_mcp.x, thumb_tip.y - pinky_mcp.y)
    dist_ip_to_pinky = math.hypot(thumb_ip.x - pinky_mcp.x, thumb_ip.y - pinky_mcp.y)

    if dist_tip_to_pinky > dist_ip_to_pinky * 1.1:
        count += 1

    return count


def draw_hud(frame, fingers_count, jump_flag, is_connected, fps):
    """Draw a clean visual heads-up display (HUD) on the video frame."""
    h, w, _ = frame.shape

    # Draw dark translucent header bar for text readability
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (320, 130), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    # Connection status indicator
    if is_connected:
        status_text = "Unity: CONNECTED"
        status_color = (0, 255, 0)  # Green
    else:
        status_text = "Unity: WAITING..."
        status_color = (0, 200, 255)  # Amber/Yellow

    cv2.putText(
        frame, status_text, (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2
    )

    # Finger count display
    finger_text = f"Fingers Raised: {fingers_count if fingers_count is not None else 0} / 5"
    cv2.putText(
        frame, finger_text, (20, 68),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
    )

    # Action badge
    if jump_flag == 1:
        action_text = "FLAP / JUMP [Active]"
        action_color = (50, 255, 50)
    else:
        action_text = "CRUISE / GLIDE"
        action_color = (180, 180, 180)

    cv2.putText(
        frame, action_text, (20, 102),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, action_color, 2
    )

    # FPS counter in bottom-left
    cv2.putText(
        frame, f"FPS: {fps:.0f}", (20, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1
    )

    # Help prompt in bottom-right
    cv2.putText(
        frame, "Press 'q' to quit", (w - 160, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1
    )


def setup_server_socket(host, port):
    """Initialize a non-blocking TCP server socket with SO_REUSEADDR."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    server.setblocking(False)
    return server


def main():
    args = parse_arguments()
    ensure_dependencies()

    print("=" * 60)
    print("Flappy Bird Hand Gesture Controller (MediaPipe)")
    print(f"Server binding: {args.host}:{args.port}")
    print(f"Jump trigger: >= {args.threshold} raised fingers")
    print("=" * 60)

    # Initialize non-blocking TCP Server
    server_socket = setup_server_socket(args.host, args.port)
    client_conn = None

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=args.detection_confidence,
        min_tracking_confidence=args.tracking_confidence,
    )

    # Initialize Video Capture
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"[Error] Failed to open camera device index {args.camera}.")
        sys.exit(1)

    prev_time = time.time()
    fps = 0.0

    print("[Ready] Camera initialized. Waiting for Unity to connect...")

    try:
        while cap.isOpened():
            # 1. Non-blocking check for new Unity connection
            if client_conn is None:
                try:
                    client_conn, client_addr = server_socket.accept()
                    client_conn.setblocking(False)
                    print(f"[Network] Unity connected from {client_addr}")
                except BlockingIOError:
                    pass

            # 2. Read webcam frame
            success, frame = cap.read()
            if not success:
                continue

            # Mirror frame horizontally for intuitive interaction
            frame = cv2.flip(frame, 1)

            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            results = hands.process(rgb_frame)
            rgb_frame.flags.writeable = True

            fingers_count = None
            jump_flag = 0

            # 3. Analyze hand landmarks if detected
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    handedness_label = "Right"
                    if results.multi_handedness and idx < len(results.multi_handedness):
                        handedness_label = results.multi_handedness[idx].classification[0].label

                    fingers_count = count_raised_fingers(hand_landmarks, handedness_label)
                    jump_flag = 1 if fingers_count >= args.threshold else 0

                    if not args.no_gui:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing.DrawingSpec(color=(40, 200, 40), thickness=2, circle_radius=2),
                            mp_drawing.DrawingSpec(color=(255, 200, 50), thickness=2, circle_radius=2),
                        )

            # 4. Transmit gesture signal to Unity if connected
            if client_conn is not None:
                try:
                    client_conn.sendall(bytes([jump_flag]))
                except (BrokenPipeError, ConnectionResetError, OSError):
                    print("[Network] Unity client disconnected. Waiting for reconnection...")
                    try:
                        client_conn.close()
                    except Exception:
                        pass
                    client_conn = None

            # 5. Calculate FPS
            curr_time = time.time()
            dt = curr_time - prev_time
            prev_time = curr_time
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt)

            # 6. Render HUD & display window
            if not args.no_gui:
                draw_hud(
                    frame,
                    fingers_count,
                    jump_flag,
                    is_connected=(client_conn is not None),
                    fps=fps,
                )
                cv2.imshow("Flappy Bird Gesture Controller", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:  # 'q' or ESC
                    print("\n[Exit] User requested termination.")
                    break

    except KeyboardInterrupt:
        print("\n[Exit] Interrupted by user.")
    finally:
        # Cleanup resources gracefully
        print("[Cleanup] Releasing camera, windows, and network sockets...")
        cap.release()
        cv2.destroyAllWindows()
        hands.close()

        if client_conn is not None:
            try:
                client_conn.close()
            except Exception:
                pass

        try:
            server_socket.close()
        except Exception:
            pass
        print("[Done] Shutdown complete.")


if __name__ == "__main__":
    main()
