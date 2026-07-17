# Beat mapping — segmentation, asset tally, VO-first timing

How a script becomes an approved shot list. Vox style is narration-driven, so the
**VO is the spine**: segment by idea, write the line, then let the line's spoken
length set the shot's duration.

---

## 1. One shot = one point (segmentation)

Split the script into beats where **each beat carries exactly one point** — a
claim, a number, a contrast, a location, or one turn in the story. Not one
sentence: a sentence with two points splits; three sentences circling one point
merge; connective tissue folds into a neighbour.

- **Split** when a sentence contains two facts ("It cost $2B *and* took ten years"
  → two shots, `$2B` then `10 YEARS`).
- **Merge** when several clauses build one idea ("It started small, then grew, then
  took over" → one build-up shot, a bar stacking).
- **Fold** pure transitions ("But here's the thing…") into the next beat's VO; they
  don't earn their own shot.

Every beat gets a **kinetic-type card** (the point, stated) and a **VO line** (the
why / the turn). If a beat has no card-worthy point, it's filler — cut it or give
it information.

---

## 2. Asset tally (what earns a reference sheet)

Scan all beats and count each recurring **character, place, and significant
object** against the shots it appears in:

- Appears in **3+ shots** → reference sheet.
- The **film's hero subject** (the person/place the story is about) → sheet even at
  2 shots.
- A **recurring place** the viewer must recognize → sheet.
- Everything else (one-off props, background crowds, single-use cut-outs) →
  per-shot, no sheet.

No speculative sheets — a sheet is a generation and is approved at the gate. List
each earned sheet in the shot list's asset plan: name, kind, the shots it's used
in, and one sentence of its locked design.

---

## 3. Narrative arc (Vox pacing)

A Vox explainer has a shape; hold it so the film isn't a flat list of facts:

1. **Hook** (1–2 shots) — the surprising claim or question, big type, no setup.
2. **Context** (2–4 shots) — the map, the timeline, the who/where; sheets first
   appear here.
3. **Build** (the middle run) — the fact beats, one point each, accent marks doing
   the work; this is the bulk.
4. **Turn** (1–2 shots) — the twist, the "but," the reveal; often the film's one
   full-accent-flood shot or its biggest scale-juxtaposition frame.
5. **Landing** (1 shot) — the takeaway card, held, VO closes.

Vary the card treatment shot to shot (number vs phrase; accent block vs type on
ground) so the cards don't feel like one template.

---

## 4. VO-first timing (the spine)

Because the style is narrated, size shots to their lines, not the reverse.

1. Write every VO line (Phase 3). Pace for the ear: short clauses, one idea per
   breath, strong verbs; **complement** the card, never read it aloud.
2. Voice each line on the chosen provider (Phase 4), then `ffprobe` its real
   duration.
3. Set each shot's `duration` from that: **word budget ≈ 2.4 words/sec**, and the
   shot runs the line's length **+ ~0.3s of air at each end**, rounded to a whole
   second (Seedance takes integer seconds, floor 4).

| VO line | ~words | Spoken | Shot `duration` |
|---|---|---|---|
| "Overnight, the border jumped west." | 6 | ~2.5s | 4s (floor) |
| "Three firms quietly took ninety percent of the market." | 9 | ~3.8s | 4s |
| "For a decade, nobody in the capital noticed what was happening." | 11 | ~4.6s | 5s |
| A two-clause build with a beat of silence | ~16 | ~6.5s | 7s |

Keep one VO segment per shot — that makes the mix offsets trivial (each shot's
cumulative start). If a line truly needs longer than ~8s, split the beat into two
shots rather than letting one clip run dead.

---

## 5. Worked example (narration → shot map)

Script excerpt:
> "In 1971, one decision unpinned the dollar from gold. Overnight, money became an
> idea backed by nothing but trust. Within a decade, inflation had doubled."

Beat map (16:9, accent = Vox yellow):

| # | Point | Card | Assets | VO line | Sec |
|---|---|---|---|---|---|
| 1 | The dollar was cut from gold | **1971** | — | "In nineteen seventy-one, one decision unpinned the dollar from gold." | 5 |
| 2 | Money became pure trust | **BACKED BY TRUST** | — | "Overnight, money became an idea — backed by nothing but trust." | 5 |
| 3 | Inflation doubled in ten years | **×2 IN 10 YRS** | — | "Within a decade, inflation had doubled." | 4 |

- Shot 1: a torn dollar bill cut-out and a gold-bar cut-out, a yellow scissors-cut
  line snapping between them, **1971** card snaps in. Redline draws the cut.
- Shot 2: the dollar cut-out floating over an off-white void, a yellow ring
  snapping around the word **TRUST** on a torn card.
- Shot 3: a yellow bar chart building up two bars, the second doubled, **×2 IN 10
  YRS** card lands as the second bar snaps to full height.

No sheets earned (no recurring person/place across the excerpt). Total 14s; VO
voiced first, each shot sized to its line, then generated on Unsora.
