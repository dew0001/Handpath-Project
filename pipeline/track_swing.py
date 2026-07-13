#!/usr/bin/env python3
"""
track_swing.py — AI swing digitizer for Handpath Lab.

Takes a golf-swing video (face-on or down-the-line), runs MediaPipe Pose on
every frame, calibrates pixels -> inches from the golfer's height, estimates
P-system positions from the hand trajectory, and writes a JSON file that
imports directly into swing-lab.html (Study mode -> Import JSON).

Usage:
    python track_swing.py rory_driver_faceon.mp4 --height 70 --name "Rory McIlroy" \
        --club Driver --view face --target right

    python track_swing.py scheffler_7i_dtl.mov --height 75 --name "Scottie Scheffler" \
        --club 7-iron --view dtl

Requires: pip install -r requirements.txt   (mediapipe, opencv-python, numpy)

Notes on accuracy (keep expectations honest):
  * Output is an approximation. Lens distortion, camera tilt, and off-square
    framing bend the trace. Use footage where the camera is square to the
    golfer (face-on: chest-on at hand height; DTL: down the target line).
  * Slow-motion footage (120/240 fps) gives dramatically better impact-zone
    sampling than 30 fps.
  * MediaPipe tracks the BODY, not the club. Hands = wrist midpoint. The
    clubhead channel is left null; digitize it manually in the app if needed.
  * P positions are heuristic estimates from the hand path (height crossings
    relative to the golfer's own hip/shoulder landmarks). Spot-check them in
    the app and re-tag any that look off.
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

try:
    import mediapipe as mp
except ImportError:
    sys.exit("mediapipe not installed - run: pip install -r requirements.txt")

# MediaPipe Pose landmark indices
NOSE = 0
L_SHOULDER, R_SHOULDER = 11, 12
L_WRIST, R_WRIST = 15, 16
L_HIP, R_HIP = 23, 24
L_ANKLE, R_ANKLE = 27, 28
L_HEEL, R_HEEL = 29, 30

# nose sits at ~93% of standing height, ankle joint at ~4%
NOSE_TO_ANKLE_FRACTION = 0.89


def landmarks_px(results, w, h):
    """Return dict of landmark -> (x_px, y_px, visibility) or None."""
    if not results.pose_landmarks:
        return None
    out = {}
    for i, lm in enumerate(results.pose_landmarks.landmark):
        out[i] = (lm.x * w, lm.y * h, lm.visibility)
    return out


def mid(pts, a, b):
    return ((pts[a][0] + pts[b][0]) / 2.0, (pts[a][1] + pts[b][1]) / 2.0)


def track_video(path, model_complexity=1):
    """Run pose estimation over every frame. Returns (fps, w, h, frames)
    where frames is a list of (t_seconds, landmark_dict|None)."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        sys.exit(f"cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames = []
    pose = mp.solutions.pose.Pose(
        static_image_mode=False,
        model_complexity=model_complexity,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)
        frames.append((i / fps, landmarks_px(res, w, h)))
        i += 1
        if i % 60 == 0:
            print(f"  {i} frames...", file=sys.stderr)
    pose.close()
    cap.release()
    return fps, w, h, frames


def smooth(series, k=5):
    """Simple moving average, NaN-tolerant."""
    arr = np.asarray(series, dtype=float)
    out = np.copy(arr)
    half = k // 2
    for i in range(len(arr)):
        seg = arr[max(0, i - half): i + half + 1]
        seg = seg[~np.isnan(seg)]
        out[i] = seg.mean() if len(seg) else np.nan
    return out


def detect_p_positions(t, hx, hy, hip_y, sh_y):
    """Heuristic P1-P10 estimation from the hands trace (world inches).
    Returns dict frame_index -> phase int."""
    n = len(t)
    speed = np.full(n, np.nan)
    for i in range(1, n - 1):
        dt = t[i + 1] - t[i - 1]
        if dt > 0:
            speed[i] = np.hypot(hx[i + 1] - hx[i - 1], hy[i + 1] - hy[i - 1]) / dt

    # top of backswing: global max hand height in the first 75% of the clip
    lim = max(3, int(n * 0.75))
    p4 = int(np.nanargmax(hy[:lim]))

    # impact: lowest hands within 0.6 s after the top
    after = min(n - 1, p4 + max(3, int(0.6 * (n / (t[-1] - t[0] + 1e-9)))))
    if after <= p4 + 1:
        after = min(n - 1, p4 + 2)
    p7 = p4 + 1 + int(np.nanargmin(hy[p4 + 1: after + 1]))

    # takeaway start: walk back from top to last near-still frame
    p1 = 0
    thresh = np.nanpercentile(speed[:p4 + 1], 25) if p4 > 4 else np.nan
    if not np.isnan(thresh):
        for i in range(p4, 0, -1):
            if not np.isnan(speed[i]) and speed[i] <= max(thresh, 8.0):
                p1 = i
                break

    hipY = np.nanmedian(hip_y) if hip_y is not None else np.nanmin(hy) + 6
    shY = np.nanmedian(sh_y) if sh_y is not None else np.nanmax(hy) - 10

    def first_crossing(i0, i1, level, rising):
        step = 1 if i1 >= i0 else -1
        for i in range(i0, i1, step):
            if np.isnan(hy[i]):
                continue
            if rising and hy[i] >= level:
                return i
            if not rising and hy[i] <= level:
                return i
        return None

    tags = {p1: 1, p4: 4, p7: 7}
    p2 = first_crossing(p1, p4, hipY + 2, rising=True)       # hands pass hip height going back
    p3 = first_crossing(p1, p4, shY - 4, rising=True)        # hands near shoulder height going back
    p5 = first_crossing(p4, p7, shY - 4, rising=False)       # back down through shoulder height
    p6 = first_crossing(p4, p7, hipY + 2, rising=False)      # down through hip height
    p8 = first_crossing(p7, n - 1, hipY + 2, rising=True)    # up through hip height post-impact
    p9 = first_crossing(p7, n - 1, shY - 4, rising=True)     # up through shoulder height post-impact
    p10 = n - 1
    for idx, p in [(p2, 2), (p3, 3), (p5, 5), (p6, 6), (p8, 8), (p9, 9), (p10, 10)]:
        if idx is not None and idx not in tags:
            tags[idx] = p
    return tags, p1, p10


def main():
    ap = argparse.ArgumentParser(description="Pose-track a golf swing video into Handpath Lab JSON.")
    ap.add_argument("video", type=Path)
    ap.add_argument("--height", type=float, required=True, help="golfer height in inches (e.g. 70)")
    ap.add_argument("--name", default=None, help='player name, e.g. "Rory McIlroy"')
    ap.add_argument("--club", default="Other", help="Driver, 7-iron, ...")
    ap.add_argument("--view", choices=["face", "dtl"], default="face")
    ap.add_argument("--target", choices=["right", "left"], default="right",
                    help="which side of the FRAME the target is on (face-on only)")
    ap.add_argument("--out", type=Path, default=None, help="output JSON path")
    ap.add_argument("--max-anchors", type=int, default=48,
                    help="downsample the swing to at most this many anchor frames")
    ap.add_argument("--model-complexity", type=int, choices=[0, 1, 2], default=1,
                    help="MediaPipe pose model complexity (2 = most accurate, slowest)")
    args = ap.parse_args()

    print(f"tracking {args.video} ...", file=sys.stderr)
    fps, w, h, frames = track_video(args.video, args.model_complexity)
    detected = [f for f in frames if f[1] is not None]
    print(f"  {len(frames)} frames, pose detected on {len(detected)}", file=sys.stderr)
    if len(detected) < 10:
        sys.exit("pose detected on fewer than 10 frames - check framing/lighting")

    # ---- calibration from the first solidly-detected frame (address) ----
    cal = None
    for _, pts in frames:
        if pts is None:
            continue
        need = [NOSE, L_ANKLE, R_ANKLE, L_HIP, R_HIP, L_WRIST, R_WRIST]
        if all(pts[i][2] > 0.5 for i in need):
            ankle_y = (pts[L_ANKLE][1] + pts[R_ANKLE][1]) / 2
            nose_y = pts[NOSE][1]
            px_per_in = (ankle_y - nose_y) / (NOSE_TO_ANKLE_FRACTION * args.height)
            ground_y = ankle_y + 0.039 * args.height * px_per_in   # ankle joint sits above the sole
            center_x = (pts[L_HIP][0] + pts[R_HIP][0]) / 2
            cal = (px_per_in, ground_y, center_x)
            break
    if cal is None:
        sys.exit("could not find a frame with full-body visibility for calibration")
    px_per_in, ground_y, center_x = cal
    direction = 1 if args.target == "right" else -1
    if args.view == "dtl":
        direction = 1  # dtl horizontal axis: toward the ball line
    print(f"  calibrated: {px_per_in:.2f} px/in", file=sys.stderr)

    def to_world(p):
        return (round(direction * (p[0] - center_x) / px_per_in, 2),
                round((ground_y - p[1]) / px_per_in, 2))

    # ---- per-frame world channels ----
    T, HX, HY, HIP, SH, HEAD = [], [], [], [], [], []
    for t, pts in frames:
        if pts is None or pts[L_WRIST][2] < 0.4 or pts[R_WRIST][2] < 0.4:
            continue
        hands = to_world(mid(pts, L_WRIST, R_WRIST))
        T.append(t)
        HX.append(hands[0])
        HY.append(hands[1])
        HIP.append(to_world(pts[L_HIP][:2]))       # lead hip for RH golfer face-on
        SH.append(to_world(pts[L_SHOULDER][:2]))
        HEAD.append(to_world(pts[NOSE][:2]))

    T = np.asarray(T)
    HXs = smooth(HX, 5)
    HYs = smooth(HY, 5)

    tags, i_start, i_end = detect_p_positions(
        T, HXs, HYs,
        np.asarray([p[1] for p in HIP], dtype=float),
        np.asarray([p[1] for p in SH], dtype=float),
    )
    print(f"  P tags at frames: { {f'P{v}': k for k, v in sorted(tags.items())} }", file=sys.stderr)

    # ---- clip to the swing, downsample to anchors (denser near impact) ----
    idxs = list(range(i_start, i_end + 1))
    if len(idxs) > args.max_anchors:
        keep = set(np.linspace(i_start, i_end, args.max_anchors).astype(int).tolist())
        keep.update(tags.keys())                       # never drop a tagged frame
        p7s = [k for k, v in tags.items() if v == 7]
        if p7s:                                        # extra density around impact
            keep.update(i for i in range(p7s[0] - 4, p7s[0] + 5) if i_start <= i <= i_end)
        idxs = sorted(keep)

    t0 = T[i_start]
    anchors = []
    for i in idxs:
        a = {
            "t": round(float(T[i] - t0), 4),
            "p": tags.get(i, 0),
            "h": [round(float(HXs[i]), 2), round(float(HYs[i]), 2)],
            "c": None,
            "hip": list(HIP[i]),
            "sh": list(SH[i]),
            "head": list(HEAD[i]),
        }
        anchors.append(a)

    payload = {
        "source": "track_swing",
        "video": args.video.name,
        "name": (args.name or args.video.stem) + f" · {args.club} · {args.view}",
        "club": args.club,
        "view": args.view,
        "heightIn": args.height,
        "fps": fps,
        "note": "MediaPipe pose estimate - approximate; P tags are heuristic, verify in the app",
        "anchors": anchors,
    }
    out = args.out or args.video.with_suffix(".swing.json")
    out.write_text(json.dumps(payload, indent=1))
    print(f"wrote {out}  ({len(anchors)} anchors) - import it in swing-lab.html Study mode")


if __name__ == "__main__":
    main()
