"""Thin wrapper around cv2.VideoCapture so the rest of the code
never talks to OpenCV's camera API directly. Swapping this out
(e.g. for an IP camera, a video file, or a different resolution
policy) never requires touching detection or app code.
"""
from __future__ import annotations
import cv2


class Camera:
    def __init__(self, index: int = 0, width: int = 1280, height: int = 720, mirror: bool = True):
        self.cap = cv2.VideoCapture(index)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Could not open camera index {index}. "
                "Check that no other app is using the webcam and that "
                "OS camera permissions are granted."
            )
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.mirror = mirror

    def read(self):
        """Returns (success, frame_bgr) or (False, None)."""
        ok, frame = self.cap.read()
        if not ok:
            return False, None
        if self.mirror:
            frame = cv2.flip(frame, 1)  # selfie-view feels natural for gesture apps
        return True, frame

    def release(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.release()
