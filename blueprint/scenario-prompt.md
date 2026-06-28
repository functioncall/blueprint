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
- **`messages`** (ordered): `{phase:"LABEL"}` divider · `{from,to,text}` request · `{self,text}` ·
  `{note,text}`. Address a sub-service as `actorId.subId`.
  - **Direction** via `kind`: omit = sync call · `"ret"` = return · `"async"` = fire-and-forget/event.
  - **Category** via `via`: `"api"` = crosses a process/network/trust boundary (HTTP/RPC/IPC/3rd-party
    SDK) · `"io"` = a data-store read/write (DB/cache/file/blob). Omit for a plain in-process call.
  - **Label = a short primary `text` + optional soft `caption`.** Keep `text` to ONE clause
    (≤ ~30 chars, renders as one line); move params / state / model names / thresholds to `caption`.
    NEVER put `·` / `—` / math in `text` (the validator rejects it). Phrase by category: call →
    `name()` or `verb noun` · api → `VERB target` (`POST /enrich`) · io → `read/write/query X` ·
    async → `emit/on/enqueue X` · return → a noun (`JPEG bytes`, `200 OK`) · self → an imperative
    phrase (`build quadtree`).
  - **`{note}`** renders as a small icon + a SHORT tag (`text`, ≤ ~24 chars); put the long
    explanation / file refs in `src` (revealed on click). Use ONLY for a genuine caveat the arrows
    can't show (a scope boundary, "CPU-only path") — sparingly, never as a scratchpad for state/impl detail.
- Pair every return with `kind:"ret"`. Put real `"metrics":{"cost":..,"latency_ms":..}` on the
  paid/heavy call AND its return. Tag traceable flows with `"paths":[...]`. Record
  `"src":"File → file"` where useful.
- **`detail`** — the click-card body. On **load-bearing** messages only (api/io/metric'd/path-tagged
  or otherwise non-obvious), add `"detail":{why,effects,fails,sends,auth,ordering}` — all keys
  optional, **omit any you're unsure of** (blank > guess). `why` is the headline (the PURPOSE, not a
  paraphrase of the label); `effects` = what it changes; `fails` = behaviour on error; `sends`/`auth`/
  `ordering` are short chips (payload token / credential / sequence constraint like `runs LAST`).
  ≤ ~140 chars each. The card already shows route, `step N/M`, phase, and fragment guard — so detail
  must NOT restate the label, participants, or caption, and a chip's fact isn't repeated in prose.
- **`fragments`**: `[{kind,label,range:[a,b]}]` — `range` indexes the **NON-phase** messages
  (0-based, inclusive); `kind` ∈ opt|alt|loop|par|break|critical|ref. **A box must wrap ≥2 messages**;
  for a single message, fold the condition into that message's `caption` (a 1-message `loop` is the
  only exception). Don't box one connection — it's noise.
- Include `source_paths` (the files you read) and `meta:{created,updated}`.
- **Only real behaviour.**

## Output
Return **only the one scenario object** — no `project` key, no `scenarios` wrapper, no prose.
