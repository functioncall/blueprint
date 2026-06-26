---
name: sequence-diagram
description: Render an interactive, self-contained HTML sequence-diagram app from a JSON spec, using a frozen renderer (tokens + layout + emitter) so the drafting-paper look, generated OKLCH palette, swimlane headers, phase sections, combined fragments, and switchable colour lenses are byte-identical every run on any project. You only ever author JSON. For a whole project it discovers scenarios once into a cached master file and re-renders only what git says changed. Use when the user wants a sequence diagram, a rendered/"proper" diagram (not ASCII), to visualise a request flow, API/service interaction, who-calls-whom over time, or to diagram a scenario as an interactive artifact (PNG export is built into the HTML).
---

# Sequence diagram

Render real sequence diagrams as **one self-contained interactive `index.html`**.
**Never hand-draw ASCII sequence diagrams** — they collide once labels have real text.
The renderer is frozen: `scripts/tokens.py` (the single source of truth for every
colour/size — never hardcode style elsewhere) → `scripts/layout.py` (pure geometry) →
`scripts/render_html.py` (SVG/HTML emitter) + `scripts/assets/` (app.css/app.js/page.html).
**You only ever write JSON data, so the look is identical every run, on every project.**
Design legend: `STYLE.md`. PNG is the in-browser ⤓ export (no separate PNG renderer).

The output is a small app: a clean header bar with a **scenario dropdown** (when there
are 2+), the active diagram full-bleed (sticky swimlane header, the body scrolls), and a
bottom toolbar of **colour lenses** + a PNG export. Click any message for its detail.

## Two modes

**A. Ad-hoc — one diagram, right now.** Write a spec (schema below) and render:
```bash
python3 ~/.claude/skills/sequence-diagram/scripts/render_html.py spec.json index.html
```
A spec is either a single scenario `{title,actors,messages,…}` or a master
`{project,scenarios:[…]}`. Copy `examples/web-request.json` (single) or
`examples/master-backdrop.json` (master). Open the HTML to view; deliver the file.

**B. Project mode — the SET, cached + self-freshening.** One **master file** holds every
scenario and renders to one `index.html` (a card per scenario, switchable via the dropdown).
Discovery is a **dynamic fan-out**: list the flows once, let the user pick, then spawn ONE
agent per chosen flow (count scales to the list). A git check means you research once, not
every time, and adding scenarios later never touches the ones already drawn.

### Project-mode runtime flow (discover → choose → fan out → merge)
1. **Locate** the master (convention: `agent_docs/diagrams/architecture.json`, else
   `docs/diagrams/`).
2. **Build the candidate flow list:**
   - **No master (first build):** spawn ONE agent with `enumerate-prompt.md` at the repo
     (pass the existing ids = none) → a JSON list of every flow.
   - **Master exists:** run the git freshness check AND spawn ONE `enumerate-prompt.md` agent
     to spot brand-new flows (pass it the existing scenario ids so it returns only what's
     missing). Candidates = changed-known + new.
     ```bash
     python3 scripts/freshness.py master.json [repo]   # fresh | stale+list | no_provenance
     ```
     If freshness is `fresh` AND enumerate finds no new flows → skip to step 6 (render only).
3. **Choose — the gate (default ON):** show the candidates as an **AskUserQuestion
   multi-select** with a **"draw all"** option; draw only the ticked ones. **Override:** if the
   user's request already said "one shot" / "draw all" / "everything", skip the picker and take
   the whole list.
4. **Fan out — the dynamic workflow:** use `scripts/draw_workflow.js` as the template and
   launch it via the **Workflow tool**, **embedding the chosen flows (+ `repo`/`masterPath`/
   `skillDir`) as literals in the inline `script`**. It spawns ONE agent per flow (each reads
   only that flow's `source_paths` + reuses the master's actor vocabulary) and returns
   `{scenarios:[…]}` — one v3 scenario object each.
   ⚠️ Pass the flows **inline**, NOT via the Workflow `args` field with `scriptPath` — observed:
   `args` does not reach the script that way (it ran with 0 flows). Inline `script` is reliable.
   (Tiny repo / no workflow wanted? `discovery-prompt.md` still does list+draw in one agent.)
5. **Merge:** add/replace those scenarios in the master **by `id`**; leave every other scenario
   byte-for-byte. (Workflow scripts have no filesystem — the main loop writes the file.)
6. **Validate → stamp → render:**
   ```bash
   python3 scripts/validate_master.py master.json   # must pass
   python3 scripts/stamp_provenance.py master.json [repo]
   python3 scripts/render_html.py master.json agent_docs/diagrams/index.html
   ```
7. **Open the HTML** (or screenshot it headless) before sending; commit the JSON + HTML.

## Spec schema (v3 — actors are PER SCENARIO)

```json
{ "project": "Acme",
  "provenance": { "git_sha": "GIT_SHA_AT_BUILD" },
  "scenarios": [
    { "id": "capture", "title": "…", "subtitle": "…",
      "meta": { "created": "2026-06-26", "updated": "2026-06-26" },
      "actors": [
        { "id": "user", "label": "User", "zone": "user", "sub_caption": "person" },
        { "id": "phone", "label": "Phone", "kind": "internal", "zone": "client",
          "sub": [ {"id":"ui","label":"Camera UI"}, {"id":"up","label":"Upload"} ] },
        { "id": "srv", "label": "Server", "zone": "server", "sub_caption": "/enrich" },
        { "id": "claude", "label": "Claude", "zone": "llm", "sub_caption": "Haiku" }
      ],
      "messages": [
        { "phase": "CAPTURE" },
        { "from": "user", "to": "phone.ui", "text": "press & hold", "paths": ["capture"] },
        { "self": "phone.ui", "text": "freeze still" },
        { "phase": "ENRICH" },
        { "from": "phone.up", "to": "srv", "text": "POST /enrich", "paths": ["enrich"],
          "src": "EnrichClient.swift → routes.ts" },
        { "from": "srv", "to": "claude", "text": "vision", "paths": ["enrich"],
          "metrics": { "cost": 0.011, "latency_ms": 900 } },
        { "from": "claude", "to": "srv", "text": "title · blurb", "kind": "ret",
          "metrics": { "cost": 0.011, "latency_ms": 900 } },
        { "note": "srv", "text": "enqueue wiki compile" }
      ],
      "fragments": [ { "kind": "opt", "label": "voice note present", "range": [1, 2] } ]
    }
  ] }
```

- **actors** (per scenario): `{id,label,zone}` (+ optional `kind`, `sub_caption`, `sub:[{id,label}]`).
  **Left→right order is computed automatically** from `zone` role (user → our client → our
  server → external third-party, busiest-first) — author them in any order. `sub` = sub-services,
  each a lifeline under the parent band (cap ~3). `sub_caption` is a one-line caption under a
  no-sub actor.
- **`zone`** = ROLE, drives ordering + the generated colour: `user`; client/`frontend`/`mobile`/
  `ui`; `server`/`api`/`worker`/`gateway`; everything else (vendors, datastores) = external.
  `kind:"internal"` also sits in the server tier. Colour is positional OKLCH — no per-zone hex.
- **messages** (ordered):
  - `{phase:"LABEL"}` — a section divider (vertical label in the left rail). No text/refs.
  - `{from,to,text}` — solid request; add `"kind":"ret"` for a dashed return. Address a
    sub-service as `actorId.subId` (e.g. `phone.ui`).
  - `{self,text}` — self-loop. `{note,text}` — folded-corner aside.
  - `"metrics":{"cost":0.011,"latency_ms":900}` — enables the `$ cost` / `⏱ latency` lenses
    (a perceptual graphite ramp; absent data → that lens isn't offered).
  - `"paths":["enrich"]` — tags the message to a named flow → a `↪ enrich` highlight lens.
  - `"src":"File.swift → route.ts"` — shown in the click-a-message detail popover.
- **`fragments`** (per scenario): `[{kind,label,range:[a,b],segments?:[{guard}]}]`. `kind` ∈
  opt|alt|loop|par|break|critical|ref. **`range` indexes the NON-phase message order** (a,b
  inclusive). `segments` adds divider guards (for alt/par).
- **`meta`** (per scenario, optional): `{created,updated,status}` — informational.

## Conventions
- Short labels (≤ ~6 words) — the renderer wraps to ≤2 lines.
- Pair every request that returns with a `kind:"ret"`. Put `metrics` on the paid/heavy call
  (and its return) so a lens can rank them — never invent a "cost" boolean; it's the metric.
- Use `phase` markers to chunk a long flow into sections; use `paths` for flows worth tracing.
- Aim for ≤ ~7 lifelines and ≤ ~20 messages per scenario; split if larger.
- Only diagram **real** behaviour — read the code, don't invent.

## Extending (keep the style frozen)
Every visual feature is a JSON field consumed by `render_html.py`, never caller-side drawing
code. New token/colour → `tokens.py` (then `STYLE.md`). New behaviour → `layout.py` geometry +
`render_html.py` emit. The author side never changes how things look.
