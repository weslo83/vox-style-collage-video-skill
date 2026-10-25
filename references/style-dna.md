# Style DNA — Vox Paper Collage

The locked visual system. Slots 1–10 never vary within a film; only their
*contents* change shot to shot. Read this fully before writing a prompt — the
specificity is the craft, and a half-specified prompt renders as generic
motion-graphics.

Contents: the ten locked slots · the AI-default betrayal · the infographic-mark
vocabulary · the kinetic-typography rules · hero-frame template · animation
template · reference-sheet formats · style-specific failure rows · the per-shot
checklist.

---

## The ten locked slots

**1. Medium & texture.** **Cut-out photographs**, not drawings or engravings.
Archival photos, editorial/press images, magazine and newsprint scraps, cut with
**visibly torn or rough scissor edges** and layered like a physical photomontage.
Every subject reads as *printed paper that was scanned*: a fine **halftone dot
screen** or newsprint grain, faint paper fibre, a slight photocopy contrast. The
signature imperfection is the **torn edge + registration/offset grain** — its
absence is what makes AI output look like clean flat vector.

**2. Ground / backdrop.** ONE editorial ground for the whole film — **off-white,
newsprint, bone, or pale grey paper** with faint fibre and a subtle paper grain.
No gradient, no vignette, no photographic backdrop. The accent color and
infographic marks live *on* this ground; the ground itself never tints.

**3. Composition & space.** **Flat layers, not depth.** A photomontage: elements
are "layered over," never "in front of." Centered or rule-of-thirds editorial
staging with generous margin for the type. Deliberate **scale juxtaposition** (a
huge cut-out hand over a tiny crowd) is a Vox signature — but it stays flat, no
perspective recession.

**4. Camera.** Mostly **locked-off**, straight-on. The two allowed moves are the
Vox signatures: a **slow editorial push/pull** (a gentle scale on the whole plate)
and a **lateral slide** across a wide collage or map. No orbit, no handheld, no
rack focus, no 3D parallax fly-through.

**5. Lighting.** Flat, even, "scanner" light — the look of art on a copystand. A
**minimal drop shadow** under each cut-out layer, just enough to sell the physical
stack. Never directional, never a real cast shadow (that implies a depth this
world doesn't have).

**6. Color grade — editorial base + ONE accent.** Three tiers, held all film:
1) the off-white/newsprint **ground**; 2) **monochrome or muted photo cut-outs**
(the archival images read desaturated, often near-B&W with a warm or cool wash);
3) **one bold accent color** (Vox's signature warm yellow, or a chosen red /
cobalt / teal) used for redlines, highlights, key type, circles, and fills. Black
is allowed for type and does not count as a hue. A **second** saturated color
breaks the editorial calm — forbid it.

**7. Motion grammar — limited frame rate, cutout-puppet.** The most style-defining
slot. Cadence: **limited / stepped** — motion snaps on a low frame rate
(8–12 fps feel), never buttery. Elements **slide in, snap into place, pop on from
0%, hinge at a paper joint, build up in stacks, get circled or underlined**.
Kinetic type **snaps and slides** in sync with the beat.
- Verbs to use: slides in, snaps in, pops on, cuts to, stacks up, layers over,
  hinges, is circled, is underlined, redline draws across, arrow shoots out,
  builds up, holds.
- Verbs that kill it: morphs, dissolves, fades (except a deliberate accent-wipe),
  eases, tweens, glides smoothly, floats, drifts, rotates smoothly, 3D-spins.
- Repeated action (a crowd moving, a machine working): a **two-frame loop** —
  two poses, hard cut between them, stated explicitly ("two-frame looping cycle").

**8. Audio grammar.** In the *video* prompt: **`No voice.`** — the narration is a
separate track laid on in post, never generated inside the clip (a spoken line
makes the model hunt for a mouth). Under it: crisp **paper foley** (slides, snaps,
the *tok* of a card landing, a page turn) plus at most one material sound tied to a
hero element, and **`No music.`** (the editorial bed is added in the mix). The
finished film's audio stack is: VO on top, music bed ducked under it, paper foley
low.

**9. Text / titles — kinetic typography carries the argument.** Words are a
**first-class element**, not decoration. Heavy **condensed grotesque / bold sans**
(Vox uses a bold neo-grotesque), set in the accent color or black, often on a
solid accent or white block. One card per shot, stating the point — a number, a
name, a short phrase. It **snaps or slides in on the beat** and holds. Optional
faint offset-print misregistration sells the paper. Keep it legible in a quarter
second; the card labels the point, it doesn't paragraph.

**10. Style references.** Primary: **Vox explainer / editorial motion-graphics**
(flat photomontage, kinetic type, infographic journalism). At most one secondary
for texture: mid-century **collage/photomontage** (Hannah Höch, John Heartfield)
or **Terry Gilliam cutout** for the discrete motion. Never lead with a live-action
or 3D reference — it pulls the model toward photoreal depth.

---

## The AI-default betrayal (put the negative in EVERY hero-frame prompt)

The betrayal: the model renders this as **glossy 3D motion-graphics, or as clean
flat-vector motion design with smooth edges and gradients, or as a realistic photo
collage with soft drop shadows and depth** — losing the torn paper and the print
grain.

The negative that beats it, in every hero-frame prompt:

> *Flat scanned-paper photomontage — real cut-out photographs with visibly torn/
> rough edges and a printed halftone/newsprint grain, physically layered on paper.
> No gloss, no 3D bevel or extrusion, no smooth vector shapes, no gradients, no
> soft realistic drop shadows beyond a thin paper offset, no depth-of-field.*

If a shot still drifts glossy, add "photocopied, slightly high-contrast, visible
paper fibre and dot screen."

---

## Infographic-mark vocabulary (the journalism layer)

These marks, in the accent color, are what make it read *Vox* rather than a craft
collage. Draw them as if inked/taped onto the plate:

- **Redline / route** — a bold accent line drawn across a torn map (a border, a
  migration, a supply chain). Animates by *drawing on*.
- **Circle / ring** — a hand-drawn accent ring around a face, a building, a word
  ("this one"). Animates by *snapping on*.
- **Arrow** — a cut-paper or drawn arrow shooting from A to B; scale/flow.
- **Underline / highlight** — an accent bar swiping under key type.
- **Pin / X / dot** — a location marker dropped on a map.
- **Bar / pie / line chart** — cut-paper data that **builds up** bar by bar, one
  tier the accent color; a number card lands the figure.
- **Timeline / ruler** — a horizontal band of years a marker slides along.
- **Magnifier** — a cut-out lens over a clipping for a "look closer" beat.

One or two marks per shot, max. They label; they don't clutter.

---

## Hero-frame prompt template (Unsora `create_image`, `nano-banana-pro`)

```
[If a sheet is bound: Match the design of @Image1 exactly; pose ONE instance of
[element] as described — the sheet is the design source, not the composition.]

[Primary cut-out-photograph subject with specific traits], [secondary cut-out
elements and how they layer over it]. [The single frozen action / arrangement the
shot shows]. [Infographic mark(s) in the accent color: e.g. a hand-drawn ACCENT
circle around X / an ACCENT redline drawn across the map]. Real cut-out
photographs with visibly torn, rough edges and a printed halftone / newsprint
grain, physically layered like a paper photomontage; thin paper drop shadow only.

Set on a flat [off-white / newsprint / pale-grey] paper ground with faint fibre,
no gradient and no texture beyond the paper. Flat editorial photomontage staging,
centered [or rule-of-thirds] with margin for the type; deliberate flat scale
juxtaposition allowed, no perspective. Even flat copystand light.

Palette: off-white ground, monochrome / muted near-B&W photo cut-outs, and ONE
accent color [ACCENT] for marks, fills, and key type — no second saturated color.

Render the card "[CARD TEXT]" in a heavy condensed bold grotesque, [placement],
in [ACCENT / black] [on a solid ACCENT or white block], faint offset-print
misregistration.

Flat scanned-paper photomontage — no gloss, no 3D bevel or extrusion, no smooth
vector shapes, no gradients, no soft realistic drop shadows, no depth-of-field.
Aspect ratio [16:9 / 9:16 / 1:1]. No watermark.
```

## Animation prompt template (Unsora `create_video`, `seedance-2.0`)

```
[16:9 / 9:16 / 1:1]. [N] seconds. Single shot. Limited-frame-rate paper-collage
motion — cut-out photo elements and type snap and slide on a low frame rate
(~8–12 fps feel), hard steps between poses, no smooth interpolation, no morphing,
no tweening. In the grammar of a Vox editorial explainer / photomontage cutout.

The supplied starting plate is the actual first frame. [Describe motion that can begin from this plate. If using an approved partial plate plus a supported end-frame constraint, describe the assembly into that final composition.] Do not re-light or redesign the supplied elements. A finished starting image cannot be made empty by calling it an end state.

[Bind each design sheet to its actual reference slot. In the example call with image occupying @Image1, the first additional reference is @Image2. Verify this against the live tool schema.]

Rundown: [element A] slides in from [edge] → [element B] pops on over it →
[the accent mark: e.g. the ACCENT redline draws across / the ACCENT circle snaps
around X] → the card "[CARD TEXT]" snaps in [and holds]. [Two-frame looping cycle
for any repeated motion.] Assembly completes by [0:0X]; hold on the finished
composition for the rest.

Camera: locked-off [or one slow editorial push / one lateral slide across the
plate]. No orbit, no handheld, no 3D parallax, no rack focus. Lighting: flat
copystand, thin paper drop shadow, static.

Audio: No voice. Crisp paper foley — slides, snaps, the tok of the card landing
[+ one material sound]. No music.
```

**Never** put the VO line inside the animation prompt. `No voice.` is load-bearing.

---

## Reference-sheet formats (Unsora `create_image`, always 16:9)

Generate a sheet once for any element flagged by the tally, **before** any shot,
and pass its URL into every shot that uses it. Sheets are always `16:9` regardless
of the film's ratio.

**Recurring person (as a cut-out):**

```
Character reference sheet, 16:9, on a plain off-white paper ground. The SAME
person as a torn-edged cut-out photograph, shown three ways left to right:
full-body front, full-body 3/4, and a head-and-shoulders close-up. [Age, build,
hair, clothing, era, defining features]. Monochrome / muted near-B&W press-photo
look, visible halftone grain and torn edges. Flat scanned-paper photomontage — no
gloss, no 3D, no smooth vector. Neutral pose, no background scene, no text.
```

**Recurring place / set:**

```
Location reference sheet, 16:9, on a plain off-white paper ground. [The place] as
a torn-paper photomontage master plate — [key layered elements and their
arrangement]. Monochrome / muted cut-out photographs, halftone grain, torn edges,
thin paper offset shadows; the ONE accent color [ACCENT] only where noted. Flat,
no perspective, no text. This is the design source for the place across shots.
```

Show each finished sheet to the user before proceeding — a flawed sheet
propagates into every shot that references it, so this is the cheapest moment to
re-roll.

**Binding a sheet in a shot:** pass the sheet URL in `referenceImages` of BOTH the
`create_image` and `create_video` calls (slot order: in the video call `image` =
@Image1, so the first `referenceImages` entry = @Image2), and in the prompt write
"Match the design of @ImageN; pose ONE instance as described." Pass only the sheets
a shot actually uses — a dangling reference invites drift.

---

## Style-specific failure rows (in addition to SKILL.md's table)

| Symptom | Cause | Fix |
|---|---|---|
| Cut-outs look like clean flat vectors | Torn-paper medium ignored | Add "real cut-out photographs, visibly torn rough edges, printed halftone/newsprint grain, photocopied" |
| Subjects render in full color | Monochrome tier dropped | Force "muted near-B&W press-photo cut-outs; color lives only in the ACCENT" |
| Type is dull / static / tiny | Kinetic-type rule ignored | Make it a heavy condensed grotesque card in the accent, snapping in on the beat, big enough to read in a quarter second |
| A second bold color appears | Accent not held | Restate "editorial base + ONE accent only; no second saturated color" |
| Elements recede into 3D perspective | Flat-layer constraint ignored | Add "flat photomontage, layered over not in front of, no perspective, every instance same size" |
| Motion is buttery/cinematic | Limited-frame cadence dropped | State "limited frame rate ~8–12fps, snaps between poses, no smooth interpolation" |
| Infographic mark looks CGI | Mark rendered as 3D | "drawn/taped-on flat accent mark, hand-inked look, no bevel" |

## Per-shot checklist — before generating

- The shot delivers one nameable point; the kinetic-type card carries it and the
  VO complements (doesn't echo) it.
- Cut-outs are torn-edged photographs with halftone/newsprint grain; the medium
  sentence AND the AI-default negative are both in the hero-frame prompt.
- Ground is the locked editorial base; palette is base + monochrome cut-outs +
  the ONE locked accent; no second saturated color.
- At most one or two infographic marks, in the accent, and they animate by
  drawing/snapping on.
- Hero-frame prompt ordered Subject → Action → Setting → Style → Camera →
  Lighting → Text → Constraints.
- If the shot uses a sheet: the sheet URL is in `referenceImages` of BOTH calls,
  bound by slot in both prompts, and the prompt describes only pose/arrangement.
- Animation prompt names @Image1 / the start frame by role, redescribes nothing,
  distinguishes the actual starting frame from the final arrangement, uses only limited-frame verbs, states the cadence.
- Camera is locked-off or exactly one slow push / lateral slide.
- Audio line is `No voice.` + paper foley + one material sound + `No music.`
- `aspectRatio` identical in both prompts and both tool calls; duration identical
  in the generation plan, animation prompt and requested `duration` parameter.
  Keep the final edit window separate; it must fit measured narration plus lead and tail.
