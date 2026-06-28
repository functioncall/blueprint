# blueprint — usage cheatsheet

`SK=~/.claude/skills/blueprint`  ·  full docs: `SKILL.md` · design legend: `STYLE.md`

## Just ask (skill auto-triggers, any project)
```
"blueprint of the checkout flow"
"diagram the login request"
"/blueprint the webhook flow"
```
It writes the JSON, renders the interactive `index.html`, and sends it. You don't touch scripts.

## Ad-hoc — one diagram from a spec
```bash
python3 $SK/scripts/render_html.py myflow.json index.html      # single scenario or a master
```
Copy a starter: `$SK/examples/web-request.json` (single) · `$SK/examples/master-backdrop.json` (master).
PNG? Open the HTML and hit the **⤓ PNG** button in the toolbar — no separate PNG renderer.

## Project mode — cached SET (discover → choose → fan out → merge)
```bash
REPO=.
python3 $SK/scripts/freshness.py        architecture.json $REPO   # fresh | stale+list | no_provenance
# (+ one enumerate-prompt.md agent to spot NEW flows not yet in the file)
# → show the candidates as a multi-select (default) → user picks (or "draw all")
# → Workflow $SK/scripts/draw_workflow.js  args={repo,masterPath,skillDir,flows}  (1 agent / flow)
# → merge the returned scenarios into the master by id (leave the rest untouched)
python3 $SK/scripts/validate_master.py  architecture.json         # guardrail (must pass)
python3 $SK/scripts/stamp_provenance.py architecture.json $REPO   # baseline the git SHA
python3 $SK/scripts/render_html.py      architecture.json agent_docs/diagrams/index.html
```
Discovery fans out: `enumerate-prompt.md` lists the flows once, the user picks, then
`draw_workflow.js` spawns ONE agent per chosen flow (count scales to the list). Adding flows
later reuses the file and never redraws the existing ones. (Legacy: `discovery-prompt.md` does
list+draw in a single agent — fine for tiny repos.)

```
ad-hoc:   spec.json ─▶ render_html.py ─▶ index.html
project:  enumerate ─▶ [pick / "draw all"] ─▶ draw_workflow.js (N agents) ─▶ merge ─▶ master.json
          (once)         ▲                                                              │
          freshness.py ──┘  reuse unchanged; only new/changed flows go to the fan-out   ▼
                                                              render_html.py ─▶ index.html (card per scenario)
```

## Spec quick-reference (v3 — actors are PER SCENARIO; order is automatic)
```json
{ "project":"Acme",
  "scenarios":[
    { "id":"capture", "title":"…", "subtitle":"…",
      "meta":{"created":"2026-06-26","updated":"2026-06-26"},
      "actors":[
        {"id":"user","label":"User","zone":"user","sub_caption":"person"},
        {"id":"srv","label":"Server","zone":"server","sub_caption":"/enrich"},
        {"id":"claude","label":"Claude","zone":"llm","sub_caption":"Haiku"} ],
      "messages":[
        {"phase":"ENRICH"},                                                 // section divider
        {"from":"user","to":"srv","text":"POST /enrich","paths":["enrich"]},// solid request
        {"from":"srv","to":"claude","text":"vision",
         "metrics":{"cost":0.011,"latency_ms":900}},                        // enables $/⏱ lens
        {"from":"claude","to":"srv","text":"result","kind":"ret"},          // dashed return
        {"self":"srv","text":"persist"},                                    // self-loop
        {"note":"srv","text":"aside"} ],                                    // folded-corner note
      "fragments":[{"kind":"opt","label":"voice note","range":[1,2]}] }     // range = non-phase idx
  ] }
```
- **zone** (role → ordering + generated OKLCH colour): `user · client/frontend/mobile · server/api/worker · <external: vendors, datastores>`. `kind:"internal"` → server tier. No per-zone hex; colour is positional.
- **sub** = sub-services → lifelines under a parent band (cap ~3). **Author order is ignored** — left→right is computed (user → client → server → external, busiest-first).
- **metrics** `{cost,latency_ms}` feed the **cost/latency lenses** (a green→amber→red heatmap with thicker lit arrows); **paths** feed flow-highlight lenses; **fragments.range** indexes the NON-phase messages.
- **detail** `{why,sends,effects,fails,ordering,auth}` (all keys optional) fills the **click-a-row detail card** — `why` is the headline, `effects`/`fails` are short prose, `sends`/`auth`/`ordering` render as chips; **src** (`File.swift → route.ts`) shows in that card's footer. Add it only for load-bearing messages.

## Scripts
| Script | Does |
|---|---|
| `render_html.py <spec\|master> <out.html>` | render a single spec or a whole master → one interactive HTML |
| `freshness.py <master> [repo]` | git-only staleness check (no agents) |
| `validate_master.py <spec\|master>` | verify v3 schema + actor refs + fragment ranges (exit 1 on error) |
| `stamp_provenance.py <master> [repo]` | write current HEAD into provenance |
