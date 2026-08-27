"""Every new use-case (drawing, mouse control, sign language, games...)
implements this interface. The pipeline knows nothing about what a
specific app does — it just calls these hooks each frame. This is
the extension point: adding a new capability means adding a new
file in apps/ and registering it in main.py, nothing else changes.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from fingertip import HandState


class BaseApp(ABC):
    name: str = "base"

    def on_start(self) -> None:
        """Called once when the app becomes active."""

    def on_stop(self) -> None:
        """Called once when the app is deactivated (e.g. user switches app)."""

    @abstractmethod
    def on_frame(self, frame_bgr, hands: List[HandState]):
        """Called every frame. `hands` is the list of tracked HandState
        objects (empty list if no hand detected). Return the frame,
        optionally with your own overlay drawn on it (draw on a copy
        or in-place — either is fine, just return it).
        """
        raise NotImplementedError

    def on_key(self, key: int) -> None:
        """Optional: react to a key press (from cv2.waitKey)."""
