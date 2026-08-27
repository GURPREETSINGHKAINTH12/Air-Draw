"""Glues camera -> hand tracking -> fingertip processing -> active app.
This is the one loop every use-case shares. Nothing here is specific
to drawing, mouse control, or any other application.
"""
from __future__ import annotations
from typing import Dict, List

import cv2

from camera import Camera
from hand_tracker import HandTracker
from fingertip import FingertipDetector
from apps.base import BaseApp


class Pipeline:
    def __init__(self, apps: Dict[str, BaseApp], start_app: str, show_skeleton: bool = True,
                 camera_index: int = 0):
        if start_app not in apps:
            raise ValueError(f"Unknown start app '{start_app}'. Available: {list(apps)}")
        self.apps = apps
        self.active_name = start_app
        self.show_skeleton = show_skeleton
        self.camera_index = camera_index

        self.tracker = HandTracker(max_hands=2)
        self.fingertips = FingertipDetector(smoothing_alpha=0.5)

    @property
    def active_app(self) -> BaseApp:
        return self.apps[self.active_name]

    def switch_app(self, name: str) -> None:
        if name not in self.apps or name == self.active_name:
            return
        self.active_app.on_stop()
        self.active_name = name
        self.active_app.on_start()

    def run(self) -> None:
        self.active_app.on_start()
        with Camera(index=self.camera_index) as cam:
            print("Controls: [1-9] switch app, [q] quit. Active apps:")
            for i, n in enumerate(self.apps, start=1):
                print(f"  {i}: {n}")

            while True:
                ok, frame = cam.read()
                if not ok:
                    print("Camera read failed — stopping.")
                    break

                raw_hands = self.tracker.process(frame)
                hand_states = [self.fingertips.process(h) for h in raw_hands]

                if self.show_skeleton:
                    # Re-run mediapipe's raw landmark objects only for drawing;
                    # cheap enough at webcam resolution, keeps HandTracker's
                    # public Hand type free of mediapipe-specific objects.
                    pass  # optional: see README for enabling raw skeleton overlay

                frame = self.active_app.on_frame(frame, hand_states)

                cv2.putText(frame, f"app: {self.active_name}", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Fingertip Tracker", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif ord('1') <= key <= ord('9'):
                    idx = key - ord('1')
                    names = list(self.apps)
                    if idx < len(names):
                        self.switch_app(names[idx])
                elif key != 255:
                    self.active_app.on_key(key)

        self.active_app.on_stop()
        self.tracker.close()
        cv2.destroyAllWindows()
