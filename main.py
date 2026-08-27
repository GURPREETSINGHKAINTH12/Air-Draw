"""Entry point. Registers every available app and starts the pipeline.

Run:
    python main.py                  # starts with air_draw, press 1/2/3 to switch
    python main.py --app virtual_mouse
    python main.py --camera 1       # use a different webcam index

To add a new use-case:
    1. Create apps/your_app.py subclassing BaseApp (see apps/pinch_gesture.py
       for the minimal template).
    2. Import it below and add it to APPS with a short key.
That's it — the pipeline, camera handling, and hand tracking are unchanged.
"""
from __future__ import annotations
import argparse

from pipeline import Pipeline
from apps.air_draw import AirDrawApp
from apps.virtual_mouse import VirtualMouseApp
from apps.pinch_gesture import PinchGestureApp

APPS = {
    "air_draw": AirDrawApp(),
    "virtual_mouse": VirtualMouseApp(),
    "gesture_readout": PinchGestureApp(),
}


def main():
    parser = argparse.ArgumentParser(description="Fingertip detection framework")
    parser.add_argument("--app", default="air_draw", choices=list(APPS),
                         help="Which app to start with (switch live with number keys 1-9)")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    args = parser.parse_args()

    pipeline = Pipeline(apps=APPS, start_app=args.app, camera_index=args.camera)
    pipeline.run()


if __name__ == "__main__":
    main()
