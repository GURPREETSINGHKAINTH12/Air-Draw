"""Minimal template app: just prints which fingers are extended and
the current pinch distance on-screen. Good starting point to copy
when building a brand-new use-case (volume control, slide-deck
navigation, sign-language letter classifier, etc.) — start here,
then replace the on_frame body with your own logic.
"""
from __future__ import annotations
from typing import List

import cv2

from apps.base import BaseApp
from fingertip import HandState


class PinchGestureApp(BaseApp):
    name = "gesture_readout"

    def on_frame(self, frame_bgr, hands: List[HandState]):
        y = 60
        if not hands:
            cv2.putText(frame_bgr, "No hand detected", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame_bgr

        for hand in hands:
            extended = ", ".join(hand.extended_fingers()) or "none"
            dist = hand.pinch_distance("thumb", "index")
            cv2.putText(frame_bgr, f"{hand.label} hand | extended: {extended}", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y += 30
            cv2.putText(frame_bgr, f"pinch dist (thumb-index): {dist:.0f}px", (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y += 40
            pt = tuple(map(int, hand.tip("index")))
            cv2.circle(frame_bgr, pt, 6, (255, 0, 255), -1)

        return frame_bgr
