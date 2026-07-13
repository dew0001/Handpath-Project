# Swing tracking pipeline

Turns a golf-swing video into Handpath Lab JSON: MediaPipe Pose on every frame,
pixel→inch calibration from the golfer's height, heuristic P1–P10 tagging from
the hand trajectory.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python track_swing.py rory_driver_faceon.mp4 --height 70 \
    --name "Rory McIlroy" --club Driver --view face --target right
```

- `--height` — golfer's height in inches (Rory 70, Scheffler 75, Åberg 75,
  Homa 70, Fleetwood 73, Tiger 73). This is the calibration scale; get it right.
- `--view face|dtl` — camera angle of the footage.
- `--target right|left` — which side of the *frame* the target is on (face-on).
- `--model-complexity 2` — slower, more accurate pose model.
- Output: `<video>.swing.json` → import in `swing-lab.html` → Study → Import JSON.

## Getting good captures

- Camera square to the golfer: face-on at hand height aimed at the sternum;
  DTL directly down the target line. Off-square angles bend the trace.
- Slow motion (120/240 fps) massively improves impact-zone sampling.
- Clip the video roughly to one swing (a few seconds of address is fine —
  the tracker finds the takeaway).
- Full body in frame the entire swing, decent light, minimal camera movement.

## Honest limitations

- **Pose ≠ club.** MediaPipe tracks the body; hands are the wrist midpoint.
  The clubhead channel is exported as `null` — add clubhead points manually in
  the app's Digitize mode if you need the club trace.
- **P tags are estimates** from height crossings and speed extrema. Verify
  against the video and re-tag in the app where needed.
- **2D only.** A face-on capture has no depth; impact metrics that need z
  (club path, attack angle) stay model-only until a second synced angle exists.
- Digitized paths are approximate — treat them as study aids, not measurements.
