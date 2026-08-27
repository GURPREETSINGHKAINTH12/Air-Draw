"""Control the OS mouse cursor with your index fingertip.
- Index extended -> move cursor (mapped from a central region of the
  frame to the full screen, so you don't need to reach the frame edges)
- Thumb+index pinch -> left click
Demonstrates: mapping camera space to screen space, and firing
discrete OS-level actions from a continuous gesture signal.

Requires: pip install pyautogui
"""
from __future__ import annotations
from typing import List

import cv2

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

from apps.base import BaseApp
from fingertip import HandState

# Active region inside the frame (as a fraction) that maps to the
# full screen — using the center of the frame instead of edge-to-edge
# makes the control feel less cramped.
FRAME_MARGIN = 0.15


class VirtualMouseApp(BaseApp):
    name = "virtual_mouse"

    def __init__(self, smoothing: float = 0.35, click_cooldown_frames: int = 12):
        self.screen_w, self.screen_h = (pyautogui.size() if pyautogui else (1920, 1080))
        self.smoothing = smoothing
        self.prev_screen_pt = None
        self.click_cooldown = 0
        self.click_cooldown_frames = click_cooldown_frames

    def on_start(self) -> None:
        if pyautogui is None:
            print("pyautogui not installed — virtual_mouse app will only preview, not move the cursor.")

    def _map_to_screen(self, pt, frame_w, frame_h):
        x0, x1 = frame_w * FRAME_MARGIN, frame_w * (1 - FRAME_MARGIN)
        y0, y1 = frame_h * FRAME_MARGIN, frame_h * (1 - FRAME_MARGIN)
        nx = min(max((pt[0] - x0) / (x1 - x0), 0), 1)
        ny = min(max((pt[1] - y0) / (y1 - y0), 0), 1)
        return nx * self.screen_w, ny * self.screen_h

    def on_frame(self, frame_bgr, hands: List[HandState]):
        h, w = frame_bgr.shape[:2]
        cv2.rectangle(frame_bgr, (int(w * FRAME_MARGIN), int(h * FRAME_MARGIN)),
                       (int(w * (1 - FRAME_MARGIN)), int(h * (1 - FRAME_MARGIN))), (80, 80, 80), 1)

        self.click_cooldown = max(0, self.click_cooldown - 1)

        if hands:
            hand = hands[0]
            if hand.is_extended("index"):
                pt = hand.tip("index")
                sx, sy = self._map_to_screen(pt, w, h)
                if self.prev_screen_pt is not None:
                    a = self.smoothing
                    sx = a * sx + (1 - a) * self.prev_screen_pt[0]
                    sy = a * sy + (1 - a) * self.prev_screen_pt[1]
                self.prev_screen_pt = (sx, sy)
                if pyautogui is not None:
                    pyautogui.moveTo(sx, sy)
                cv2.circle(frame_bgr, tuple(map(int, pt)), 10, (0, 200, 255), -1)

            if hand.pinch_distance("thumb", "index") < 30 and self.click_cooldown == 0:
                if pyautogui is not None:
                    pyautogui.click()
                self.click_cooldown = self.click_cooldown_frames
                cv2.putText(frame_bgr, "CLICK", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        return frame_bgr
