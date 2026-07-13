# Handpath Lab

A swing-study instrument: interactive visualization of where a golfer's hands
and clubhead travel through the entire swing, in real inches, tracked against
the P-system (P1 Address → P10 Finish), with face-on **and** down-the-line views.

**Live app: <https://dew0001.github.io/Handpath-Project/>** (deploys automatically
from [`index.html`](index.html) via GitHub Actions — see `.github/workflows/pages.yml`).
The app is a single self-contained file with no dependencies; it also runs by just
opening `index.html` in any browser.

## Coordinate system

- `x` — inches from body center (sternum), **+ toward the target** (RH golfer)
- `y` — inches above the ground
- `z` — inches from the body toward the ball line (drives the DTL view)

## Study mode

- Built-in **model swings** (7-iron, driver) with hands + clubhead in pseudo-3D,
  smoothed with Catmull-Rom over ~20 authored anchors
- Face-on, down-the-line, or both stages side by side
- Backswing/downswing split coloring shows the wide-to-narrow loop
  (downswing runs inside the backswing arc)
- Articulated stick golfer driven by hip turn / shoulder turn / tilt / sway /
  head channels; DTL posture figure with shaft-plane reference line
- P1–P10 transport: scrub, play at 0.15×–1× real tempo, click a P to jump
- Live metrics: hands x/y/z, hand speed, clubhead speed; at-impact club path
  (in-to-out/out-to-in), attack angle, clubhead mph (3D data only)
- Velocity coloring (hand-speed gradient along the path)
- Overlay up to 3 swings for comparison; digitized swings persist in
  localStorage with JSON export/import

## Digitize mode (capture real swings)

Load a video (or screenshot sequence), calibrate from the golfer's height in
three clicks, then step frames and click **hands / clubhead / lead hip /
lead shoulder / head** per frame. Tag P positions as you go. Saved captures
appear in Study mode.

## AI pipeline (automated digitizing)

[`pipeline/track_swing.py`](pipeline/README.md) — MediaPipe Pose over every
frame, auto-calibration from golfer height, heuristic P-tagging, exports JSON
the app imports directly. Point it at face-on or DTL footage of any player
(or your own phone video).

## Honesty constraints (load-bearing, keep these)

- Built-in coordinates are **representative models**, authored to match
  published hub-path research (Nesbit & McGinnis: non-circular path, changing
  radius, downswing inside backswing). They are **not measured data** and are
  labeled as models in the UI.
- No public dataset of per-pro raw hand coordinates exists. Pro paths must
  come from digitizing real footage (Digitize mode or the pipeline).
  **Never ship fabricated curves labeled with pro names.**
- Digitized paths are approximate: lens distortion and off-square camera
  angles bend the trace; 2D captures have no depth channel.

## Roadmap

- Clubhead tracking in the pipeline (color/motion tracking; pose models don't see the club)
- Two-angle sync (face-on + DTL of the same swing → true 3D, real club path numbers)
- Velocity/acceleration analysis views; kinematic sequence from hip/shoulder channels
- Per-P-position checkpoints comparison table between two swings
