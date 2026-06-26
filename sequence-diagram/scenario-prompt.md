# Scenario prompt — "draw ONE flow" (handed to each fan-out agent)

You draw **exactly one** scenario as a v3 JSON object. You'll be given the flow's `id`,
`title`, and `source_paths`, the repo path, and the path to the existing master file.

## Steps
1. **Read the existing master file.** Note the actor `id`s and `zone`s already in use, and
   **reuse them** wherever the same real component appears (same `id`, same `zone`). This keeps
   colours and lane order consistent across the whole set.
2. **Read the `source_paths`** (and what they reference) and trace the real interactions for
   THIS flow only.
3. **Emit one scenario object.**

## The shape
The full schema + every field's meaning is the **"Spec schema (v3)"** section of `SKILL.md` —
read it. The hard rules in brief:

- **`actors`** — each `{id,label,zone}` (+ optional `kind`, `sub_caption`, `sub:[{id,label}]`).
  `zone` is the ROLE (`user` · client/`frontend`/`mobile` · `server`/`api`/`worker` · anything
  else = external vendor/datastore) and drives both order and colour. **Never supply hex.**
- **Coarse actors** — ONE lifeline for our own server unless the flow truly needs sub-modules;
  DO split a vendor into the products this flow touches. Aim ≤ ~7 lifelines, ≤ ~20 messages.
- **`messages`** (ordered): `{phase:"LABEL"}` divider · `{from,to,text}` request (+`"kind":"ret"`
  for a dashed return) · `{self,text}` · `{note,text}`. Address a sub-service as `actorId.subId`.
- Pair every return with `kind:"ret"`. Put real `"metrics":{"cost":..,"latency_ms":..}` on the
  paid/heavy call AND its return. Tag traceable flows with `"paths":[...]`. Record
  `"src":"File → file"` where useful.
- **`fragments`**: `[{kind,label,range:[a,b]}]` — `range` indexes the **NON-phase** messages
  (0-based, inclusive); `kind` ∈ opt|alt|loop|par|break|critical|ref.
- Include `source_paths` (the files you read) and `meta:{created,updated}`.
- **Only real behaviour.** Short labels (≤ ~6 words).

## Output
Return **only the one scenario object** — no `project` key, no `scenarios` wrapper, no prose.
