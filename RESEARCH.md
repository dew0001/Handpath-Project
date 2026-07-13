# Tour-Pro Swing Data — Research Findings

*Compiled for Handpath Lab from a multi-source deep-research pass (peer-reviewed
biomechanics, TrackMan/GEARS/TPI publications, coaching media). Every number
below is tagged with its source and a confidence level. Where a value is coaching
consensus rather than a measurement, it says so. **No numbers were invented** — the
gaps are left as gaps, which is the whole point.*

## TL;DR for the app

1. **There is no public per-pro hand-path coordinate dataset.** The academic
   hub-path work that everyone cites (Nesbit & McGinnis) measured **4 amateurs**,
   not tour pros. So the built-in hand paths must stay labeled as *models* — the
   research validates their *shape*, not any pro's exact curve.
2. **Only 2 of the 30 named players have real published quantitative swing data:**
   - **Rory McIlroy** — GEARS 3D body angles (hip/shoulder turn at P4 and P7,
     pelvis velocity, clubhead speed). *Reported via coaching media, GEARS-derived.*
   - **Jon Rahm** — TrackMan impact numbers (driver attack angle, club path
     tendency). *TrackMan's own blog.*
   - The other 28 (Scheffler, Schauffele, Åberg, Morikawa, Hovland, Cantlay,
     Thomas, Spieth, Homa, Fleetwood, Matsuyama, Zalatoris, Finau, Koepka,
     DeChambeau, Niemann, Clark, Burns, Im, Henley, Bradley, Fitzpatrick,
     Conners, Theegala, Pendrith, Day, Woods, Els) have **no published
     position-by-position data**. They can be shown against tour-average models
     only — or digitized from video with the pipeline.
3. **Per-player clubhead speed IS available for all 30** from PGA Tour ShotLink
   radar (public stat pages) — a real, citable per-player number even when body
   positions aren't.
4. **The strong, encodable layer is tour-average bands** (below): X-Factor at the
   top, hips open at impact, tempo ratio, TrackMan impact conditions. These are
   well-sourced and safe to encode as a *tour-average reference*, drawn as a band,
   not a line.

---

## 1. Hand / hub path geometry — CONFIRMED (adversarially verified 3–0)

Source: **Nesbit & McGinnis, "Kinematic Analyses of the Golf Swing Hub Path,"
*J. Sports Sci. Med.* 2009; 8(2):235–246** (PMID 24149532 / PMC3761476). Primary,
peer-reviewed. **Caveat: n = 4 amateurs** (scratch, 5, 13, 18 handicap) — archetypal,
not tour data.

| Finding | Value | Use in app |
|---|---|---|
| Hub path is **not** a constant-radius arc | radius changes continuously; center-of-curvature moves throughout downswing | ✅ already modeled (Catmull-Rom, non-circular) — now citable |
| Three-phase radius pattern | local **max near top**, local **min at downswing midpoint**, local **max near impact** | ✅ validates the wide→narrow→wide loop |
| Measured radii (scratch / 5H / 13H / 18H) | top: 0.665 / 0.649 / 0.842 / 0.629 m · mid-downswing min: 0.535 / 0.408 / 0.397 / 0.460 m · near impact: 0.793 / 0.581 / 0.979 / 0.874 m | reference scale (~21–26 in radius for a scratch swing) |
| Sharp radius reduction just before impact | present in all subjects; linked to skill (Miura 2001) | ✅ the "narrowing into impact" the model shows |

**Bottom line:** the app's core design decision — a non-circular hand path that
narrows in transition and re-widens toward impact — is exactly what the peer-reviewed
data shows. This is the most solid result in the whole search.

---

## 2. Tour-average body positions (P-system) — encodable as BANDS

These are the reference bands safe to encode as a tour-average model. Sources mixed
(peer-reviewed + TPI + GEARS documentation); confidence noted per row.

| Position | Metric | Tour-average / band | Source | Confidence |
|---|---|---|---|---|
| **P4** (top) | Pelvis (hip) turn | ~45° (male & female tour avg) | TPI, *X-Factor* | Medium (coaching org) |
| **P4** | Thorax (shoulder) turn | ~90° | TPI | Medium |
| **P4** | **X-Factor** (separation) | ~45° | TPI | Medium |
| **P4→P5** | X-Factor "stretch" | +~5° (→ ~50°) in transition | TPI | Medium |
| **P7** (impact) | Pelvis open to target | **20–45°** (folklore "45" is high end) | Golf Insider 3D summary | Medium |
| **P7** | Thorax at impact | roughly square, ~50–90° range across players | Golf Insider / GolfWRX 3D | Medium |
| whole swing | Elite pelvis–thorax **separation** | **70 ± 20°** | 3D research summary | Medium |
| whole swing | Peak X-Factor ↔ clubhead speed | r = **0.863 ± 0.134** (very strong) | Meister et al. 2011 (PMID 21844613) | High (peer-reviewed) |
| whole swing | Pro rotational consistency | X-Factor CoV **7.4%**, S-factor **8.4%** across pros | Meister et al. 2011 | High |
| downswing | **Kinematic sequence** | pelvis → thorax → arm → club (proximal-to-distal) | Meister et al. 2011 | High |

> **Measurement-convention warning (important for honesty):** reported "shoulder
> turn" varies by whether the system tracks the acromia (shoulder points) or the
> ribcage — this alone shifts numbers 10–20°. GEARS' own position is that there are
> **no single ideal numbers, only "windows"** players fit into. Encode ranges, not
> lines. (GEARS Golf Body Metrics; GolfWRX body-rotation article.)

---

## 3. Per-player data — the honest inventory

### Players WITH published quantitative data (2 of 30)

**Rory McIlroy** — GEARS 3D capture (via Golf.com/TaylorMade, 2019). *Secondary
reporting of GEARS-derived numbers; treat as approximate.*

| Metric | Value |
|---|---|
| Hip turn at top (P4) | ~42° |
| Shoulder turn at top (P4) | ~116° |
| X-Factor at top | ~75° (well above the ~45° tour avg — an outlier) |
| Shoulders P4→P7 | 114° closed → 35° open |
| Hips unwind top→impact | >100° |
| Peak pelvis rotational velocity | ~720°/s (tour avg ~500°/s; amateurs ~300°/s) |
| Driver clubhead speed | up to ~122 mph |

**Jon Rahm** — TrackMan (TrackMan Golf blog). *Primary launch-monitor source.*

| Metric | Value |
|---|---|
| Driver attack angle | **+5.2°** (steep up — notably positive) |
| Club path (6-iron) | slightly left |

### Players with per-player SPEED only (all 30)

PGA Tour ShotLink radar publishes measured **clubhead speed** per player per season
(pgatour.com stats). This is real and citable — usable as a per-player scalar even
when body positions aren't available. *Not fetched per-player in this pass; pull
live when building profiles.*

### Players with NO published position data (28 of 30)

Scheffler, Schauffele, Åberg, Morikawa, Hovland, Cantlay, Thomas, Spieth, Homa,
Fleetwood, Matsuyama, Zalatoris, Finau, Koepka, DeChambeau, Niemann, Clark, Burns,
Im, Henley, Bradley, Fitzpatrick, Conners, Theegala, Pendrith, Day, Woods, Els.

→ These get the **tour-average model** in the app until their footage is digitized
(Digitize mode or the pipeline). Do **not** fabricate per-position numbers for them.

---

## 4. Tempo — tour-average, encodable

Source: **Tour Tempo (Novosel)**, frame-count method. Secondary but the standard reference.

| Metric | Value |
|---|---|
| Backswing : downswing ratio | **~3 : 1** (27:9 frames typical; Nick Price 24:8) |
| PGA Tour backswing time | ~0.8 s |
| PGA Tour downswing time | ~0.25 s |
| Individual variation | McIlroy quicker transition (~2.2:1 reported) |

---

## 5. TrackMan tour-average impact conditions — encodable

Source: **TrackMan PGA Tour Averages** (trackman.com, 2024 refresh + classic table).

| Club | Clubhead speed | Attack angle | Ball speed | Carry |
|---|---|---|---|---|
| Driver | ~113–115 mph | **−1.3° to −0.9°** (band — varies by source year) | ~167 mph | ~275 yd |
| 7-iron | ~90–92 mph | ~−4° (down) | ~120 mph | ~172–176 yd |

> **Data-quality flag:** TrackMan blends competition + range shots and quietly
> revises these year to year (driver AoA quoted as −1.3° in 2019, −0.9° later). The
> app already shows model 7-iron ≈ −4° AoA / +3.5° path and driver ≈ +1° AoA, which
> sit correctly relative to these bands. Encode a **band with a source-year**, not a
> fixed number.

---

## 6. What this means for the build

| Layer | Data quality | Action |
|---|---|---|
| Hand-path shape (non-circular, 3-phase) | ✅ Peer-reviewed | Keep models; cite Nesbit & McGinnis in-app |
| Tour-average P4 / P7 body bands | 🟡 Coaching-org + 3D summaries | Add a **"tour-average band"** reference overlay |
| Tempo 3:1 | 🟡 Standard reference | Already implicit in playback; can label |
| TrackMan impact bands | ✅ Primary (with year caveat) | Show model impact numbers against the band |
| Rory McIlroy profile | 🟡 GEARS via media | Can add as a **single real per-player profile**, labeled "GEARS, approx." |
| Jon Rahm impact | ✅ TrackMan primary | Can add attack-angle note |
| Other 28 players | ❌ None | Tour-average model only; digitize to get real data |

### Recommended next feature
A **"tour-average reference"** toggle: shade the P4 hip-turn band (40–50°), the P7
hips-open band (20–45°), and the impact-condition bands behind the model swing, with
a citation footnote. This turns the honesty constraint into a feature — the user sees
exactly where measured tour ranges sit versus the model, and which pros have real
data behind them.

---

## Sources

- Nesbit & McGinnis 2009, *J. Sports Sci. Med.* 8(2):235–246 — hub-path geometry (PMID 24149532 / PMC3761476) — **primary, verified**
- Nesbit 2005, *J. Sports Sci. Med.* — 3D kinematic/kinetic study, 84 amateurs (PMC3899667) — primary
- Meister et al. 2011, *J. Applied Biomechanics* 27(3) — elite rotational benchmarks, X-Factor↔speed (PMID 21844613) — primary
- Swing Performance Index 2022, *Frontiers in Sports & Active Living* (PMC9816382) — pro rotational-velocity consistency — primary
- IMU validation 2023, *Sensors* 23(20):8433 — measurement-system agreement (±0.6–1.7°) — primary
- TPI, *X-Factor: Why More Isn't Always Better* (mytpi.com) — tour-avg separation ~45° — coaching org
- GEARS Golf, *Body Metrics* (gearssports.com) — "windows not numbers" — vendor documentation
- TrackMan PGA/LPGA Tour Averages 2024 (trackman.com) — impact bands — primary
- Golf.com / TaylorMade GEARS, *Secrets to Rory McIlroy's Swing* (2019) — Rory 3D numbers — secondary
- TrackMan Golf blog, *Jon Rahm TrackMan Numbers* — Rahm impact — primary
- Tour Tempo (tourtempo.com) — 3:1 tempo — secondary/standard
- PGA Tour ShotLink stats (pgatour.com) — per-player clubhead speed — primary
- GolfWRX *Body Rotation* + Golf Insider 3D summary — tour bands, measurement caveats — coaching media

*Provenance note: the research run's automated verification pass was interrupted by
a usage limit, so most claims here carry "extracted with verbatim source quote" rather
than a full 3-vote confirmation. The hand-path geometry claims (§1) completed
verification 3–0. All quotes were captured verbatim from the cited sources; treat
coaching-media rows as medium-confidence pending a re-verification pass.*
