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

Shows **only swings you have digitized** — there are no built-in models or
pro reference data. Capture a swing in Digitize mode and it appears here.

- Face-on, down-the-line, or both stages side by side; `x = 0` marks body center
- Backswing/downswing split coloring shows the wide-to-narrow loop
  (downswing runs inside the backswing arc)
- Traced hand path, clubhead path, and hip/shoulder/head point traces
- P1–P10 transport: scrub, play at 0.15×–1× real tempo, click a P to jump
- Live metrics: hands x/y/z, hand speed, clubhead speed
- Velocity coloring (hand-speed gradient along the path)
- Overlay up to 3 of your swings for comparison; the source video overlays
  behind the path when present. All swings persist in localStorage with
  JSON export/import

## Digitize mode (capture real swings)

Load a face-on or down-the-line video, then hit **✨ Auto-track (AI)**: MediaPipe
Pose runs *in your browser*, auto-calibrates from the golfer's height, tracks
hands / lead hip / lead shoulder / head across the swing, and heuristically tags
**P1–P10**. (No install — the model streams from a CDN on first use; needs an
internet connection. Offline or batch work → use the Python pipeline below.)

Then **correct what the AI got wrong**. The whole digitizer fits on one screen —
no scrolling — with the point picker, **P1–P10 jump bar**, frame stepper, and
zoom controls always in view. **Zoom** (scroll wheel or +/−) right into the
footage to place dots precisely; a dot stays locked to the exact pixel you put it
on when you zoom back out. **Pan** with the ✋ button or by holding space.
**Drag any dot to fix it** — AI-placed points show a dashed ring until you touch
them, so you see machine-guess vs. hand-corrected at a glance. Delete a point by
clicking it then pressing Delete (or Alt-/double-click); delete whole frames from
the list. Add the clubhead manually (pose models don't see the club) and re-tag P
positions. Full manual tracking (3-click calibrate + click each point) is always
available too.

**The video is stored with the swing** (IndexedDB), so Study mode overlays your
traced path directly on the footage, scrubber-synced — toggle "Video overlay" in
the Display panel.

**Export project** bundles the video + all tracked points + calibration into one
`.handpath.json` file. **Import project** re-opens it later (or on another
machine) to keep editing — nothing is lost. Saved library swings can also be
exported this way via the ⤓ button.

## AI pipeline (automated digitizing)

[`pipeline/track_swing.py`](pipeline/README.md) — MediaPipe Pose over every
frame, auto-calibration from golfer height, heuristic P-tagging, exports JSON
the app imports directly. Point it at face-on or DTL footage of any player
(or your own phone video).

## Honesty constraints (load-bearing, keep these)

- The app ships with **no built-in swings and no pro/tour reference data** —
  Study shows only paths the user digitized themselves.
- No public dataset of per-pro raw hand coordinates exists. Any pro path must
  come from digitizing real footage (Digitize mode or the pipeline).
  **Never ship fabricated curves labeled with pro names.**
- Digitized paths are approximate: lens distortion and off-square camera
  angles bend the trace; 2D captures have no depth channel.
- `RESEARCH.md` retains the cited tour-average findings for reference, but that
  data is intentionally **not** surfaced in the app UI.

## Roadmap

- Clubhead tracking in the pipeline (color/motion tracking; pose models don't see the club)
- Two-angle sync (face-on + DTL of the same swing → true 3D, real club path numbers)
- Velocity/acceleration analysis views; kinematic sequence from hip/shoulder channels
- Per-P-position checkpoints comparison table between two swings
