"""Wraps MediaPipe Hands. This is the ONLY file that imports mediapipe
directly. If you ever swap detection backends (e.g. a custom trained
model, MediaPipe Tasks API, or a cloud API), this is the only file
that changes.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

import cv2
import mediapipe as mp

# Landmark indices, per MediaPipe's hand model (21 points per hand).
WRIST = 0
THUMB_TIP, THUMB_IP, THUMB_MCP = 4, 3, 2
INDEX_TIP, INDEX_PIP, INDEX_MCP = 8, 6, 5
MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP = 12, 10, 9
RING_TIP, RING_PIP, RING_MCP = 16, 14, 13
PINKY_TIP, PINKY_PIP, PINKY_MCP = 20, 18, 17

FINGER_TIPS = {
    "thumb": THUMB_TIP,
    "index": INDEX_TIP,
    "middle": MIDDLE_TIP,
    "ring": RING_TIP,
    "pinky": PINKY_TIP,
}


@dataclass
class Hand:
    label: str                       # "Left" or "Right" (as seen by the camera)
    score: float                     # detection confidence
    landmarks_px: List[tuple]        # 21 x (x_px, y_px, z) in pixel space
    landmarks_norm: List[tuple] = field(default_factory=list)  # 21 x (x, y, z) normalized 0-1

    def point(self, idx: int) -> tuple:
        return self.landmarks_px[idx]

    def tip(self, finger: str) -> tuple:
        return self.point(FINGER_TIPS[finger])


class HandTracker:
    def __init__(self, max_hands: int = 2, detection_conf: float = 0.6, tracking_conf: float = 0.6):
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles

    def process(self, frame_bgr) -> List[Hand]:
        h, w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = self._hands.process(frame_rgb)

        hands: List[Hand] = []
        if not results.multi_hand_landmarks:
            return hands

        for lm_set, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label
            score = handedness.classification[0].score
            px = [(int(p.x * w), int(p.y * h), p.z) for p in lm_set.landmark]
            norm = [(p.x, p.y, p.z) for p in lm_set.landmark]
            hands.append(Hand(label=label, score=score, landmarks_px=px, landmarks_norm=norm))
        return hands

    def draw_landmarks(self, frame_bgr, hand_landmarks_raw) -> None:
        """Optional: draw MediaPipe's built-in skeleton overlay."""
        self.mp_drawing.draw_landmarks(
            frame_bgr, hand_landmarks_raw, self._mp_hands.HAND_CONNECTIONS,
            self.mp_styles.get_default_hand_landmarks_style(),
            self.mp_styles.get_default_hand_connections_style(),
        )

    def close(self):
        self._hands.close()
