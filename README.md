# Fingertip Tracker Framework

Detects fingertip positions from a laptop webcam using MediaPipe Hands,
built so new applications can be added without touching the core
detection/tracking code.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Requires Python 3.9–3.11 (MediaPipe wheels lag behind the newest Python
releases — if `pip install mediapipe` fails, this is almost always why).

## Controls

- Number keys `1`, `2`, `3`... — switch between registered apps live
- `q` — quit
- App-specific keys are shown on screen (e.g. `c` cycles draw color)

## Architecture

```
camera.py         -> grabs frames from the webcam
hand_tracker.py    -> MediaPipe Hands wrapper; only file that imports mediapipe
fingertip.py       -> turns raw landmarks into smoothed tip positions +
                      finger-extended states + pinch distance (reusable
                      across every app)
apps/base.py       -> BaseApp interface every use-case implements
apps/*.py          -> individual applications (drawing, mouse control, ...)
pipeline.py        -> the shared loop: camera -> tracker -> fingertip ->
                      active app -> display
main.py            -> registers apps and starts the pipeline
```

### Adding a new use-case

1. Copy `apps/pinch_gesture.py` as a template.
2. Subclass `BaseApp`, implement `on_frame(self, frame_bgr, hands)`.
   `hands` is a list of `HandState` objects, each giving you:
   - `hand.tip("index")` -> smoothed (x, y) pixel position
   - `hand.is_extended("thumb")` -> bool
   - `hand.extended_fingers()` -> list of extended finger names
   - `hand.pinch_distance("thumb", "index")` -> pixel distance
3. Register it in `main.py`'s `APPS` dict.

Ideas to build next: volume/brightness control via pinch distance,
slide-deck navigation via swipe gestures, a sign-language letter
classifier (feed the 21 landmarks into a small trained classifier
instead of hand-written rules), a game controller (e.g. fingertip as
a paddle), or multi-hand gestures (two-hand zoom/rotate for a simple
AR-style viewer).

## Notes on accuracy / performance

- Works best with good, even lighting and the hand roughly 30cm–1m
  from the camera.
- `HandTracker(max_hands=2)` in `pipeline.py` controls how many hands
  are tracked at once — 1 hand is noticeably faster if you don't need both.
- `FingertipDetector(smoothing_alpha=...)` in `pipeline.py` controls
  jitter vs. responsiveness — lower alpha = smoother but more laggy.
- The "finger extended" rule (`fingertip.py`) is a simple
  geometric heuristic (tip-to-wrist vs pip-to-wrist distance), not a
  trained classifier. It's reliable for the common cases here but if
  you build something gesture-heavy (e.g. sign language), consider
  training a small classifier on the 21 landmarks instead.
