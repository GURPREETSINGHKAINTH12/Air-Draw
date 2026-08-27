"""Turns raw hand landmarks into stable, usable fingertip signals:
- smoothed (x, y) pixel position per fingertip (reduces jitter)
- which fingers are "extended" vs "curled"
- pinch distance between thumb and any other fingertip

This is the layer most reusable across applications, so keep it
free of any app-specific logic (no drawing, no OS control here).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
import math

from hand_tracker import Hand, FINGER_TIPS

FINGER_PIP = {"thumb": 3, "index": 6, "middle": 10, "ring": 14, "pinky": 18}
FINGER_MCP = {"thumb": 2, "index": 5, "middle": 9, "ring": 13, "pinky": 17}


def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


@dataclass
class FingerState:
    tip_px: tuple
    extended: bool


@dataclass
class HandState:
    label: str
    fingers: Dict[str, FingerState]

    def tip(self, finger: str) -> tuple:
        return self.fingers[finger].tip_px

    def is_extended(self, finger: str) -> bool:
        return self.fingers[finger].extended

    def pinch_distance(self, finger_a: str = "thumb", finger_b: str = "index") -> float:
        return _dist(self.fingers[finger_a].tip_px, self.fingers[finger_b].tip_px)

    def extended_fingers(self) -> list:
        return [name for name, f in self.fingers.items() if f.extended]


class _EMASmoother:
    """Exponential moving average smoother, one per tracked point."""
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self._state: Dict[str, tuple] = {}

    def smooth(self, key: str, point: tuple) -> tuple:
        prev = self._state.get(key)
        if prev is None:
            self._state[key] = point
            return point
        a = self.alpha
        sm = (a * point[0] + (1 - a) * prev[0], a * point[1] + (1 - a) * prev[1])
        self._state[key] = sm
        return sm

    def reset(self, key: Optional[str] = None):
        if key is None:
            self._state.clear()
        else:
            self._state.pop(key, None)


class FingertipDetector:
    """Stateful across frames (keeps the smoother alive) — create one
    instance and reuse it for the life of the video stream.
    """
    def __init__(self, smoothing_alpha: float = 0.5):
        self._smoother = _EMASmoother(smoothing_alpha)

    def _finger_extended(self, hand: Hand, finger: str) -> bool:
        wrist = hand.point(0)
        tip = hand.point(FINGER_TIPS[finger])
        pip = hand.point(FINGER_PIP[finger])
        if finger == "thumb":
            # Thumb extends sideways, not up — compare horizontal distance
            # from the palm (MCP of index) instead of vertical.
            mcp = hand.point(FINGER_MCP["index"])
            return _dist(tip, mcp) > _dist(pip, mcp) * 1.15
        # For other fingers: extended if tip is farther from wrist than
        # the pip joint is (works regardless of hand rotation better
        # than a raw y-comparison).
        return _dist(tip, wrist) > _dist(pip, wrist) * 1.05

    def process(self, hand: Hand) -> HandState:
        fingers = {}
        for name in FINGER_TIPS:
            raw_tip = hand.point(FINGER_TIPS[name])[:2]
            smoothed = self._smoother.smooth(f"{hand.label}:{name}", raw_tip)
            fingers[name] = FingerState(
                tip_px=smoothed,
                extended=self._finger_extended(hand, name),
            )
        return HandState(label=hand.label, fingers=fingers)

    def reset(self):
        self._smoother.reset()
