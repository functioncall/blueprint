# Discovery prompt — LEGACY single-agent fallback

> The default project-mode flow is now a fan-out: `enumerate-prompt.md` lists the flows, the
> user picks, then `draw_workflow.js` spawns one `scenario-prompt.md` agent per flow. Use THIS
> all-in-one prompt only for a tiny repo where one agent can comfortably map every journey at
> once. It is also the shared schema reference the split prompts point back to.

You are mapping a codebase into a **master diagram file** for the sequence-diagram skill.
Explore the repo and answer these questions, then output ONE JSON object (the master file,
the v3 schema below) and nothing else.

## The questions
1. **Scenarios** — the product's top user journeys worth diagramming (capture, ask, checkout,
   login…). One scenario per journey.
2. **Actors per scenario** — who participates: client surfaces, our own services, external
   vendors, datastores, queues. Give each a `zone` ROLE (see below) — this drives both ordering
   and colour, so it must be right. Order doesn't matter; the renderer sorts left→right.
3. **Sub-services per actor** — which sub-components a scenario actually uses. Capture for EVERY
   actor: our server → its modules; a vendor → its products (Firebase → Firestore/Storage/Auth);
   a platform → its services. Each `sub` becomes a full lifeline — **cap at ~3 per actor.**
4. **Messages** — for each scenario, the ordered interactions `from → to` (address sub-services as
   `actorId.subId`). Set `kind` for direction (omit = call · `"ret"` = return · `"async"` = event),
   `via` for category (`"api"` = crosses a process/network boundary · `"io"` = data-store read/write ·
   omit = in-process), and split each label into a short primary `text` + optional soft `caption`.
5. **Phases** — chunk each scenario's messages into named sections with `{"phase":"LABEL"}`
   markers placed between messages (e.g. CAPTURE / SAVE / ENRICH).
6. **Metrics & paths** — which interactions are expensive/load-bearing? Put real numbers on them
   as `"metrics":{"cost":0.011,"latency_ms":900}` (on the call AND its return). Tag messages that
   belong to a traceable flow with `"paths":["enrich"]`. Record `"src":"File → file"` where useful.
   On the load-bearing ones, add `"detail":{why,effects,fails,sends,auth,ordering}` (the click-card
   body — everything the arrow can't show). All keys optional; **omit any you're unsure of**. `why` =
   the PURPOSE in plain words (not the label reworded); `effects` = what changes; `fails` = on-error
   behaviour; `sends`/`auth`/`ordering` = short chips. ≤ ~140 chars each; never restate the label,
   participants, caption, or a chip's fact in prose.
7. **Provenance** — record `source_paths` (files/dirs) per scenario so freshness knows what to re-read.

## Hard rules
- **Only real, live behaviour.** Read the code; do NOT invent features, endpoints, or actors.
- **Coarse actors — the #1 readability rule.** Prefer ONE lifeline for your own server; split into
  `sub` modules only if a flow needs it. DO split external vendors into the products a scenario uses.
  Aim for ≤ ~7 lifelines and ≤ ~20 messages per scenario; split if larger.
- **Short labels** — ONE clause per primary `text` (≤ ~30 chars, no wrap); detail → `caption`. No
  `·`/`—`/math in a primary. Tag `via` (api/io) + `kind` (ret/async) so the type reads at a glance.
- `zone` ROLE values: `user`; `client`/`frontend`/`mobile`/`ui` (our client); `server`/`api`/
  `worker`/`gateway` (our server, or set `kind:"internal"`); anything else = external (vendors,
  datastores). Colour is generated from this — never supply hex.

## Output schema (emit exactly this shape, JSON only — actors are PER SCENARIO)
```json
{
  "project": "<name>",
  "provenance": { "git_sha": "GIT_SHA_AT_BUILD" },
  "scenarios": [
    {
      "id": "capture",
      "title": "...", "subtitle": "...",
      "meta": { "created": "YYYY-MM-DD", "updated": "YYYY-MM-DD" },
      "source_paths": ["src/services/capture.ts"],
      "actors": [
        {"id": "user", "label": "User", "zone": "user", "sub_caption": "person"},
        {"id": "srv",  "label": "Server", "kind": "internal", "zone": "server",
         "sub": [ {"id": "api", "label": "API"} ]},
        {"id": "claude", "label": "Claude", "zone": "llm", "sub_caption": "Haiku"}
      ],
      "messages": [
        {"phase": "ENRICH"},
        {"from": "user", "to": "srv.api", "text": "POST /enrich", "via": "api", "paths": ["enrich"]},
        {"from": "srv.api", "to": "claude", "text": "vision", "caption": "image + prompt", "via": "api",
         "metrics": {"cost": 0.011, "latency_ms": 900}, "src": "enricher.ts",
         "detail": {"why": "Caption the scene for the catalogue card.",
                    "effects": "Writes title + blurb to the item doc.",
                    "fails": "Vision error → item saved untitled, retried by the worker.",
                    "sends": "base64 JPEG + prompt", "ordering": "after upload"}},
        {"from": "claude", "to": "srv.api", "text": "result", "caption": "title, blurb", "kind": "ret",
         "metrics": {"cost": 0.011, "latency_ms": 900}},
        {"self": "srv.api", "text": "persist"},
        {"note": "srv.api", "text": "aside"}
      ],
      "fragments": [ {"kind": "opt", "label": "voice note present", "range": [1, 2]} ]
    }
  ]
}
```
- Leave `git_sha` as `GIT_SHA_AT_BUILD` (the skill stamps it).
- `fragments.range` indexes the **non-phase** message order (a,b inclusive); `kind` ∈
  opt|alt|loop|par|break|critical|ref. **A box must wrap ≥2 messages** — for one message, fold the
  condition into its `caption` (a 1-message `loop` is the only exception).
- A message is `{from,to,text}` (+ optional `kind:"ret"|"async"`, `via:"api"|"io"`, `caption`,
  `metrics`, `paths`, `src`, `detail`), `{self,text}`, `{note,text}`, or `{phase:"LABEL"}`. No
  top-level `actors`, no `system_map`.
- `{note}` = a small icon + SHORT tag (`text`, ≤ ~24 chars), detail in `src` (click). Genuine
  caveats only (scope boundary, a non-obvious constraint) — not a scratchpad for state/impl detail.

## After you output
The skill validates with `validate_master.py`, stamps the git SHA, and renders with
`render_html.py`. Emit only the JSON.
