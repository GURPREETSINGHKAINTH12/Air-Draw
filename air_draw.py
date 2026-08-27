"""Draw on screen by moving your index fingertip in the air.
- Index finger extended alone -> draw
- All fingers extended (open palm) -> lift pen (stop drawing)
- Thumb+index pinch -> clear canvas
Demonstrates: continuous position tracking + simple gesture rules.
"""
from __future__ import annotations
from typing import List

import cv2
import numpy as np

from apps.base import BaseApp
from fingertip import HandState

COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255)]


class AirDrawApp(BaseApp):
    name = "air_draw"

    def __init__(self):
        self.canvas = None
        self.prev_point = None
        self.color_idx = 0
        self.pinch_cooldown = 0

    def on_start(self) -> None:
        self.prev_point = None

    def _ensure_canvas(self, frame):
        if self.canvas is None or self.canvas.shape[:2] != frame.shape[:2]:
            self.canvas = np.zeros_like(frame)

    def on_frame(self, frame_bgr, hands: List[HandState]):
        self._ensure_canvas(frame_bgr)

        if hands:
            hand = hands[0]
            extended = set(hand.extended_fingers())

            if hand.pinch_distance("thumb", "index") < 35 and self.pinch_cooldown == 0:
                self.canvas[:] = 0
                self.pinch_cooldown = 15  # frames, avoid repeated clears
            self.pinch_cooldown = max(0, self.pinch_cooldown - 1)

            drawing = extended == {"index"}
            if drawing:
                pt = tuple(map(int, hand.tip("index")))
                if self.prev_point is not None:
                    cv2.line(self.canvas, self.prev_point, pt, COLORS[self.color_idx], 6)
                self.prev_point = pt
                cv2.circle(frame_bgr, pt, 8, COLORS[self.color_idx], -1)
            else:
                self.prev_point = None
        else:
            self.prev_point = None

        out = cv2.addWeighted(frame_bgr, 1.0, self.canvas, 1.0, 0)
        cv2.putText(out, "index=draw  open-palm=lift  pinch=clear  'c'=color",
                    (10, out.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return out

    def on_key(self, key: int) -> None:
        if key == ord('c'):
            self.color_idx = (self.color_idx + 1) % len(COLORS)
