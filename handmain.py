# import cv2
# import mediapipe as mp
# import numpy as np
# import math
# import random
# import os
# import urllib.request

# # ==========================================
# # 1. SETUP & MODEL DOWNLOAD
# # ==========================================
# # Model URL for MediaPipe Hand Landmarker
# MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
# MODEL_PATH = "hand_landmarker.task"

# def download_model():
#     """Downloads the hand landmarker model if not present."""
#     if not os.path.exists(MODEL_PATH):
#         print("Downloading hand landmarker model...")
#         urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
#         print("Download complete.")

# download_model()

# # Import MediaPipe Tasks API (Current API for Python 3.12+)
# BaseOptions = mp.tasks.BaseOptions
# HandLandmarker = mp.tasks.vision.HandLandmarker
# HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
# VisionRunningMode = mp.tasks.vision.RunningMode

# # ==========================================
# # 2. FILTER & DRAWING FUNCTIONS
# # ==========================================

# # Fingertip indices in MediaPipe (Thumb, Index, Middle, Ring, Pinky)
# FINGERTIPS = [4, 8, 12, 16, 20]

# # Connections for drawing the skeleton (Pairs of indices)
# HAND_CONNECTIONS = [
#     (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
#     (0, 5), (5, 6), (6, 7), (7, 8),        # Index
#     (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
#     (9, 13), (13, 14), (14, 15), (15, 16), # Ring
#     (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
#     (0, 17)                                # Palm base
# ]

# # Particle storage for sparkle effect
# particles = []

# def get_pixel_coords(landmark, w, h):
#     """Converts normalized landmark to pixel coordinates."""
#     return int(landmark.x * w), int(landmark.y * h)

# def draw_fingertip_circles(frame, hand_landmarks, w, h):
#     """Filter 1: Colorful circles on fingertips."""
#     for idx in FINGERTIPS:
#         lm = hand_landmarks[idx]
#         cx, cy = get_pixel_coords(lm, w, h)
#         # Random vibrant color for each tip
#         color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
#         cv2.circle(frame, (cx, cy), 15, color, -1)
#         cv2.circle(frame, (cx, cy), 20, (255, 255, 255), 2)

# def draw_neon_outline(frame, hand_landmarks, w, h):
#     """Filter 2: Glowing/Neon outline around the hand."""
#     # Create a temporary overlay for the glow
#     overlay = frame.copy()
    
#     # Draw thick colored lines to create a glow base
#     for start_idx, end_idx in HAND_CONNECTIONS:
#         p1 = get_pixel_coords(hand_landmarks[start_idx], w, h)
#         p2 = get_pixel_coords(hand_landmarks[end_idx], w, h)
#         # Neon Green/Cyan color
#         cv2.line(overlay, p1, p2, (255, 255, 0), 12)
    
#     # Blend the overlay with the original frame for a glow effect
#     cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    
#     # Draw thin white core lines for the neon look
#     for start_idx, end_idx in HAND_CONNECTIONS:
#         p1 = get_pixel_coords(hand_landmarks[start_idx], w, h)
#         p2 = get_pixel_coords(hand_landmarks[end_idx], w, h)
#         cv2.line(frame, p1, p2, (255, 255, 255), 2)

# def draw_skeleton(frame, hand_landmarks, w, h):
#     """Filter 3: Standard colorful hand skeleton."""
#     # Draw connections
#     for start_idx, end_idx in HAND_CONNECTIONS:
#         p1 = get_pixel_coords(hand_landmarks[start_idx], w, h)
#         p2 = get_pixel_coords(hand_landmarks[end_idx], w, h)
#         cv2.line(frame, p1, p2, (0, 255, 0), 3)
        
#     # Draw joints
#     for lm in hand_landmarks:
#         cx, cy = get_pixel_coords(lm, w, h)
#         cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

# def create_sparkles(frame, hand_landmarks, w, h):
#     """Particle effect around fingertips."""
#     global particles
    
#     # Spawn new particles at fingertips
#     for idx in FINGERTIPS:
#         lm = hand_landmarks[idx]
#         cx, cy = get_pixel_coords(lm, w, h)
        
#         # Create 2-3 particles per tip per frame
#         for _ in range(3):
#             particles.append({
#                 'x': cx, 'y': cy,
#                 'vx': random.uniform(-3, 3),
#                 'vy': random.uniform(-3, 3),
#                 'life': random.randint(10, 20),
#                 'color': (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
#             })

#     # Update and draw particles
#     for p in particles[:]:
#         p['x'] += p['vx']
#         p['y'] += p['vy']
#         p['life'] -= 1
        
#         if p['life'] <= 0:
#             particles.remove(p)
#         else:
#             # Draw particle (size based on life)
#             size = max(1, p['life'] // 5)
#             cv2.circle(frame, (int(p['x']), int(p['y'])), size, p['color'], -1)

# # ==========================================
# # 3. MAIN APPLICATION LOGIC
# # ==========================================
# def main():
#     # Open Webcam
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("Error: Could not open webcam. Please check your camera connection.")
#         return

#     # Initialize Hand Landmarker (Tasks API)
#     # LIVE_STREAM mode is required for video processing
#     options = HandLandmarkerOptions(
#         base_options=BaseOptions(model_asset_path=MODEL_PATH),
#         running_mode=VisionRunningMode.LIVE_STREAM,
#         num_hands=2, # Support both hands
#         min_hand_detection_confidence=0.5,
#         min_hand_presence_confidence=0.5,
#         min_tracking_confidence=0.5,
#         result_callback=lambda result, output_image, timestamp_ms: None 
#         # Note: For simplicity in this script, we process synchronously using detect_for_video 
#         # (see below) rather than async callback to keep code beginner-friendly.
#     )
    
#     # We use VIDEO mode for synchronous processing inside the loop for simplicity
#     options = HandLandmarkerOptions(
#         base_options=BaseOptions(model_asset_path=MODEL_PATH),
#         running_mode=VisionRunningMode.VIDEO,
#         num_hands=2,
#         min_hand_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     )

#     filter_mode = 0 # 0=Off, 1=Circles, 2=Neon, 3=Skeleton
#     timestamp = 0

#     with HandLandmarker.create_from_options(options) as landmarker:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 print("Failed to grab frame.")
#                 break

#             # Flip the frame horizontally for a mirror view (more intuitive)
#             frame = cv2.flip(frame, 1)
#             h, w, _ = frame.shape

#             # Convert BGR to RGB for MediaPipe
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
#             # Create MediaPipe Image object
#             mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
#             # Process the frame
#             timestamp += 1 # In a real app, use actual time in ms
#             detection_result = landmarker.detect_for_video(mp_image, timestamp)

#             hand_detected = False

#             # Draw filters if hands are detected
#             if detection_result.hand_landmarks:
#                 hand_detected = True
#                 for hand_landmarks in detection_result.hand_landmarks:
#                     # Apply selected filter
#                     if filter_mode == 1:
#                         draw_fingertip_circles(frame, hand_landmarks, w, h)
#                     elif filter_mode == 2:
#                         draw_neon_outline(frame, hand_landmarks, w, h)
#                     elif filter_mode == 3:
#                         draw_skeleton(frame, hand_landmarks, w, h)
                    
#                     # Always add sparkles (or add a toggle for this if preferred)
#                     if filter_mode != 0:
#                         create_sparkles(frame, hand_landmarks, w, h)

#             # Draw particles even if hand is lost (so they fade out naturally)
#             if filter_mode != 0:
#                 # Update particles only (no new spawns if no hand)
#                 for p in particles[:]:
#                     p['x'] += p['vx']
#                     p['y'] += p['vy']
#                     p['life'] -= 1
#                     if p['life'] <= 0:
#                         particles.remove(p)
#                     else:
#                         cv2.circle(frame, (int(p['x']), int(p['y'])), max(1, p['life']//5), p['color'], -1)

#             # UI Messages
#             status_text = "Hand Detected - Filter ON" if hand_detected else "Show Your Hand"
#             if filter_mode == 0 and hand_detected:
#                 status_text = "Hand Detected - Filter OFF"
            
#             cv2.putText(frame, status_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0) if hand_detected else (0, 0, 255), 2)
#             cv2.putText(frame, f"Mode: {filter_mode} (1/2/3/0)", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

#             # Show result
#             cv2.imshow('Hand Filter Application', frame)

#             # Keyboard Controls
#             key = cv2.waitKey(1) & 0xFF
#             if key == ord('q') or key == 27: # Q or ESC
#                 break
#             elif key == ord('1'):
#                 filter_mode = 1
#                 print("Filter 1: Fingertip Circles")
#             elif key == ord('2'):
#                 filter_mode = 2
#                 print("Filter 2: Neon Outline")
#             elif key == ord('3'):
#                 filter_mode = 3
#                 print("Filter 3: Skeleton")
#             elif key == ord('0'):
#                 filter_mode = 0
#                 particles.clear() # Clear particles when turning off
#                 print("Filter Off")

#     # Release resources
#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()


import cv2
import mediapipe as mp
import numpy as np
import math
import random
import os
import urllib.request
import time

# ==========================================
# 1. SETUP & MODEL DOWNLOAD
# ==========================================
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = "hand_landmarker.task"

def download_model():
    """Downloads the hand landmarker model if not present."""
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand landmarker model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Download complete.")

download_model()

# Import MediaPipe Tasks API (Current API for Python 3.12+)
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# ==========================================
# 2. ORIGINAL FILTERS & HELPERS (PRESERVED)
# ==========================================
FINGERTIPS = [4, 8, 12, 16, 20]

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

particles = []

def get_pixel_coords(landmark, w, h):
    return int(landmark.x * w), int(landmark.y * h)

def draw_fingertip_circles(frame, hand_landmarks, w, h):
    for idx in FINGERTIPS:
        lm = hand_landmarks[idx]
        cx, cy = get_pixel_coords(lm, w, h)
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        cv2.circle(frame, (cx, cy), 15, color, -1)
        cv2.circle(frame, (cx, cy), 20, (255, 255, 255), 2)

def draw_neon_outline(frame, hand_landmarks, w, h):
    overlay = frame.copy()
    for start_idx, end_idx in HAND_CONNECTIONS:
        p1 = get_pixel_coords(hand_landmarks[start_idx], w, h)
        p2 = get_pixel_coords(hand_landmarks[end_idx], w, h)
        cv2.line(overlay, p1, p2, (255, 255, 0), 12)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    for start_idx, end_idx in HAND_CONNECTIONS:
        p1 = get_pixel_coords(hand_landmarks[start_idx], w, h)
        p2 = get_pixel_coords(hand_landmarks[end_idx], w, h)
        cv2.line(frame, p1, p2, (255, 255, 255), 2)

def draw_skeleton(frame, hand_landmarks, w, h):
    for start_idx, end_idx in HAND_CONNECTIONS:
        p1 = get_pixel_coords(hand_landmarks[start_idx], w, h)
        p2 = get_pixel_coords(hand_landmarks[end_idx], w, h)
        cv2.line(frame, p1, p2, (0, 255, 0), 3)
    for lm in hand_landmarks:
        cx, cy = get_pixel_coords(lm, w, h)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

def create_sparkles(frame, hand_landmarks, w, h):
    global particles
    for idx in FINGERTIPS:
        lm = hand_landmarks[idx]
        cx, cy = get_pixel_coords(lm, w, h)
        for _ in range(3):
            particles.append({
                'x': cx, 'y': cy,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': random.randint(10, 20),
                'color': (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            })
    for p in particles[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['life'] -= 1
        if p['life'] <= 0:
            particles.remove(p)
        else:
            size = max(1, p['life'] // 5)
            cv2.circle(frame, (int(p['x']), int(p['y'])), size, p['color'], -1)


# ==========================================
# 3. NEW: FINGER-COUNT-AWARE BRIDGE FILTER
# ==========================================
RAINBOW_COLORS = [
    (0, 0, 255),     # Red     -> Thumb
    (0, 165, 255),   # Orange  -> Index
    (0, 255, 255),   # Yellow  -> Middle
    (0, 255, 0),     # Green   -> Ring
    (255, 0, 0)      # Blue    -> Pinky
]

def get_pinch_distance(hand_landmarks):
    """Normalized distance between thumb tip and index tip of one hand."""
    thumb = hand_landmarks[4]
    index = hand_landmarks[8]
    dx = thumb.x - index.x
    dy = thumb.y - index.y
    return math.hypot(dx, dy)

def get_extended_fingers(hand_landmarks, w, h):
    """
    Returns a list of fingertip landmark indices that are currently
    extended/up. Order is fixed as [thumb(4), index(8), middle(12),
    ring(16), pinky(20)] so pairing is stable and predictable.

    Detection logic (uses only landmark geometry — no extra model):
      - Index / Middle / Ring / Pinky: tip is further from wrist
        than the middle joint (PIP). This works regardless of hand
        rotation because the finger straightens away from the wrist.
      - Thumb: tip is further from the wrist than the thumb's IP joint
        AND further from the index MCP than the thumb's MCP is.
    """
    wrist = get_pixel_coords(hand_landmarks[0], w, h)
    extended = []

    # --- Thumb (4) ---
    thumb_tip = get_pixel_coords(hand_landmarks[4], w, h)
    thumb_ip  = get_pixel_coords(hand_landmarks[3], w, h)
    thumb_mcp = get_pixel_coords(hand_landmarks[2], w, h)
    index_mcp = get_pixel_coords(hand_landmarks[5], w, h)
    d_tip_wrist  = math.hypot(thumb_tip[0] - wrist[0], thumb_tip[1] - wrist[1])
    d_ip_wrist   = math.hypot(thumb_ip[0] - wrist[0],  thumb_ip[1] - wrist[1])
    d_tip_index  = math.hypot(thumb_tip[0] - index_mcp[0], thumb_tip[1] - index_mcp[1])
    d_mcp_index  = math.hypot(thumb_mcp[0] - index_mcp[0], thumb_mcp[1] - index_mcp[1])
    if d_tip_wrist > d_ip_wrist * 1.15 and d_tip_index > d_mcp_index * 0.9:
        extended.append(4)

    # --- Index / Middle / Ring / Pinky ---
    # (tip, pip) pairs: (8,6), (12,10), (16,14), (20,18)
    finger_pairs = [(8, 6), (12, 10), (16, 14), (20, 18)]
    for tip_idx, pip_idx in finger_pairs:
        tip = get_pixel_coords(hand_landmarks[tip_idx], w, h)
        pip = get_pixel_coords(hand_landmarks[pip_idx], w, h)
        d_tip = math.hypot(tip[0] - wrist[0], tip[1] - wrist[1])
        d_pip = math.hypot(pip[0] - wrist[0], pip[1] - wrist[1])
        if d_tip > d_pip * 1.15:
            extended.append(tip_idx)

    return extended

def draw_quadratic_bezier(img, p0, p1, p2, color, thickness=4, segments=28):
    """Smooth quadratic Bezier curve from p0 to p2, curved through p1."""
    pts = []
    for i in range(segments + 1):
        t = i / segments
        x = int((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0])
        y = int((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])
        pts.append((x, y))
    arr = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(img, [arr], isClosed=False, color=color,
                  thickness=thickness, lineType=cv2.LINE_AA)

def draw_count_aware_bridge(frame, lms_a, lms_b, w, h, active):
    """
    Draws one rainbow bridge line per matched extended finger pair.

    Steps:
      1. Detect extended fingertips on each hand.
      2. Intersect the two lists by landmark index so the same
         anatomical finger is paired (thumb->thumb, index->index,
         etc.). This keeps the lines meaningful even if the user
         raises them in a weird order.
      3. For each matched pair, draw a curved rainbow line with a
         neon glow, spanning from hand A's fingertip to hand B's.

    Returns the number of lines actually drawn (used by the UI).
    """
    ext_a = set(get_extended_fingers(lms_a, w, h))
    ext_b = set(get_extended_fingers(lms_b, w, h))

    # Match by landmark index (anatomically correct pairing).
    # FINGERTIPS order (4,8,12,16,20) makes the color assignment
    # consistent: thumb always red, index always orange, etc.
    matched = [tip for tip in FINGERTIPS if tip in ext_a and tip in ext_b]

    if active:
        core_thickness = 4
        glow_thickness = 16
        glow_alpha = 0.75
    else:
        core_thickness = 1
        glow_thickness = 4
        glow_alpha = 0.25

    glow_layer = np.zeros_like(frame)

    # Midpoint of both palms — used for the curve control point so the
    # lines arc nicely between the hands
    palm_a = get_pixel_coords(lms_a[9], w, h)
    palm_b = get_pixel_coords(lms_b[9], w, h)
    mid_palm = ((palm_a[0] + palm_b[0]) // 2, (palm_a[1] + palm_b[1]) // 2)

    for tip_idx in matched:
        # Map landmark index -> color index (0..4)
        color = RAINBOW_COLORS[FINGERTIPS.index(tip_idx)]

        p_a = get_pixel_coords(lms_a[tip_idx], w, h)
        p_b = get_pixel_coords(lms_b[tip_idx], w, h)

        # Curved control point pulled toward the shared palm midpoint
        ctrl = (
            int((p_a[0] + p_b[0]) / 2 + (mid_palm[0] - (p_a[0] + p_b[0]) / 2) * 0.30),
            int((p_a[1] + p_b[1]) / 2 + (mid_palm[1] - (p_a[1] + p_b[1]) / 2) * 0.30)
        )

        draw_quadratic_bezier(glow_layer, p_a, ctrl, p_b, color,
                              thickness=glow_thickness, segments=32)
        draw_quadratic_bezier(frame, p_a, ctrl, p_b, color,
                              thickness=core_thickness, segments=32)
        draw_quadratic_bezier(frame, p_a, ctrl, p_b, (255, 255, 255),
                              thickness=max(1, core_thickness - 2), segments=32)

        if active:
            for p in (p_a, p_b):
                cv2.circle(frame, p, 7, color, -1, cv2.LINE_AA)
                cv2.circle(frame, p, 9, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.addWeighted(glow_layer, glow_alpha, frame, 1.0, 0, frame)
    return len(matched)

def draw_gesture_indicator(frame, active, count_a, count_b, bridged):
    """On-screen status pill showing pinch state and detected finger counts."""
    color = (0, 255, 0) if active else (0, 0, 255)
    label = "BRIDGE: ON (pinch)" if active else "BRIDGE: OFF (pinch to activate)"
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    cv2.rectangle(frame, (6, 116), (6 + tw + 22, 120 + th + 2), (0, 0, 0), -1)
    cv2.circle(frame, (16, 120 + th // 2 - 2), 5, color, -1)
    cv2.putText(frame, label, (28, 120 + th - 2), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, color, 1, cv2.LINE_AA)

    # Show finger counts + bridged line count
    info = f"L:{count_a}  R:{count_b}  Lines: {bridged}"
    cv2.putText(frame, info, (10, 120 + th + 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)


# ==========================================
# 4. MAIN
# ==========================================
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam. Please check your camera connection.")
        return

    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    filter_mode = 0
    PINCH_ON = 0.06
    PINCH_OFF = 0.09
    bridge_active = False

    start_time = time.time()
    last_ts = 0

    with HandLandmarker.create_from_options(options) as landmarker:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            ts = int((time.time() - start_time) * 1000)
            if ts <= last_ts:
                ts = last_ts + 1
            last_ts = ts
            detection_result = landmarker.detect_for_video(mp_image, ts)

            hand_detected = False
            bridged_lines = 0
            count_left = 0
            count_right = 0
            bridge_drawn = False

            # Classify hands by handedness, sort by confidence
            hands_list = []
            if detection_result.hand_landmarks:
                handedness_list = detection_result.handedness or [None] * len(detection_result.hand_landmarks)
                for lm_list, handed in zip(detection_result.hand_landmarks, handedness_list):
                    if handed and len(handed) > 0:
                        label = handed[0].category_name
                        score = handed[0].score
                    else:
                        label, score = "Unknown", 0.0
                    hands_list.append((label, score, lm_list))

            if hands_list:
                hand_detected = True
                hands_list.sort(key=lambda t: t[1], reverse=True)
                primary = hands_list[0]
                secondary = hands_list[1] if len(hands_list) > 1 else None

                # ----- PRIMARY HAND: original selected filter -----
                primary_lms = primary[2]
                if filter_mode == 1:
                    draw_fingertip_circles(frame, primary_lms, w, h)
                elif filter_mode == 2:
                    draw_neon_outline(frame, primary_lms, w, h)
                elif filter_mode == 3:
                    draw_skeleton(frame, primary_lms, w, h)
                if filter_mode != 0:
                    create_sparkles(frame, primary_lms, w, h)

                # ----- BOTH HANDS: count-aware rainbow bridge -----
                if secondary is not None:
                    secondary_lms = secondary[2]

                    # Pinch gesture on the secondary hand for on/off
                    dist = get_pinch_distance(secondary_lms)
                    if not bridge_active and dist < PINCH_ON:
                        bridge_active = True
                    elif bridge_active and dist > PINCH_OFF:
                        bridge_active = False

                    # Draw bridge lines only for currently-extended finger pairs
                    bridged_lines = draw_count_aware_bridge(
                        frame, primary_lms, secondary_lms, w, h, bridge_active
                    )
                    bridge_drawn = True

                    # Update counts for the UI
                    count_left = len(get_extended_fingers(primary_lms, w, h))
                    count_right = len(get_extended_fingers(secondary_lms, w, h))

                    draw_gesture_indicator(frame, bridge_active,
                                           count_left, count_right, bridged_lines)
            else:
                bridge_active = False

            # Fade out leftover sparkles
            if filter_mode != 0:
                for p in particles[:]:
                    p['x'] += p['vx']
                    p['y'] += p['vy']
                    p['life'] -= 1
                    if p['life'] <= 0:
                        particles.remove(p)
                    else:
                        cv2.circle(frame, (int(p['x']), int(p['y'])),
                                   max(1, p['life'] // 5), p['color'], -1)

            # UI
            status_text = "Hand Detected - Filter ON" if hand_detected else "Show Your Hand"
            if filter_mode == 0 and hand_detected:
                status_text = "Hand Detected - Filter OFF"

            cv2.putText(frame, status_text, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 255, 0) if hand_detected else (0, 0, 255), 2)
            cv2.putText(frame, f"Mode: {filter_mode} (1/2/3/0)",
                        (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (255, 255, 255), 1)

            if hand_detected and not bridge_drawn:
                cv2.putText(frame, "Show second hand -> raise fingers to bridge them",
                            (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (200, 200, 0), 1, cv2.LINE_AA)

            cv2.imshow('Hand Filter Application', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('1'):
                filter_mode = 1
                print("Filter 1: Fingertip Circles")
            elif key == ord('2'):
                filter_mode = 2
                print("Filter 2: Neon Outline")
            elif key == ord('3'):
                filter_mode = 3
                print("Filter 3: Skeleton")
            elif key == ord('0'):
                filter_mode = 0
                particles.clear()
                print("Filter Off")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()