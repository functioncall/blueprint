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
4. **Messages** — for each scenario, the ordered interactions `from → to` (address sub-services
   as `actorId.subId`), what each does, request vs return (`"kind":"ret"`), self-calls, notes.
5. **Phases** — chunk each scenario's messages into named sections with `{"phase":"LABEL"}`
   markers placed between messages (e.g. CAPTURE / SAVE / ENRICH).
6. **Metrics & paths** — which interactions are expensive/load-bearing? Put real numbers on them
   as `"metrics":{"cost":0.011,"latency_ms":900}` (on the call AND its return). Tag messages that
   belong to a traceable flow with `"paths":["enrich"]`. Record `"src":"File → file"` where useful.
7. **Provenance** — record `source_paths` (files/dirs) per scenario so freshness knows what to re-read.

## Hard rules
- **Only real, live behaviour.** Read the code; do NOT invent features, endpoints, or actors.
- **Coarse actors — the #1 readability rule.** Prefer ONE lifeline for your own server; split into
  `sub` modules only if a flow needs it. DO split external vendors into the products a scenario uses.
  Aim for ≤ ~7 lifelines and ≤ ~20 messages per scenario; split if larger.
- **Short labels** (≤ ~6 words per `text`).
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
        {"from": "user", "to": "srv.api", "text": "POST /enrich", "paths": ["enrich"]},
        {"from": "srv.api", "to": "claude", "text": "vision",
         "metrics": {"cost": 0.011, "latency_ms": 900}, "src": "enricher.ts"},
        {"from": "claude", "to": "srv.api", "text": "result", "kind": "ret",
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
  opt|alt|loop|par|break|critical|ref.
- A message is `{from,to,text}` (+`kind:"ret"`, `metrics`, `paths`, `src`), `{self,text}`,
  `{note,text}`, or `{phase:"LABEL"}`. No top-level `actors`, no `system_map`.

## After you output
The skill validates with `validate_master.py`, stamps the git SHA, and renders with
`render_html.py`. Emit only the JSON.
