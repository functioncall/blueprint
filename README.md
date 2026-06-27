<div align="center">

<img src="docs/img/logo.png" width="620" alt="Sequence Diagrams">

![license](https://img.shields.io/badge/license-MIT-555?style=flat-square)
![agent skill](https://img.shields.io/badge/agent_skill-SKILL.md-555?style=flat-square)
![python](https://img.shields.io/badge/python_3-zero_deps-555?style=flat-square)
![output](https://img.shields.io/badge/output-self--contained_HTML-555?style=flat-square)

<br>

<img src="docs/img/hero.png" width="860" alt="Interactive sequence diagram — Backdrop sign-in flow with the Google path lit">

*Describe a flow in JSON. Get a self-contained, interactive sequence diagram — byte-identical every run, on any project.*

</div>

---

## What it is

An **[Agent Skill](https://code.claude.com/docs/en/skills)** (`SKILL.md` + a folder) that renders real, **interactive** sequence diagrams to a single self-contained `index.html` — drafting-paper look, auto-generated OKLCH palette, swimlane headers, phase bands, combined fragments, switchable colour lenses, click-for-detail, and in-browser PNG export.

You only ever **author JSON**. A frozen renderer (`tokens.py` → `layout.py` → `render_html.py`) turns it into the same diagram every time, so you never fight layout or pick colours. Because it's just a skill folder + a Python script, it works with **any agent that reads skills** — Claude Code, Codex, Cursor, Gemini CLI — and anything else can call the renderer directly.

> No Mermaid wrestling, no hand-placed boxes, no ASCII that collapses the moment labels get real. Say the flow; get the diagram.

## What it does

**One master file, every flow.** A whole product's journeys live in one file and render to a scenario dropdown — switch between them with consistent lanes and colours.

<img src="docs/img/feat-scenarios.png" width="820" alt="Scenario dropdown listing 13 flows in one file">

**Switchable colour lenses.** Trace a named path end-to-end, or ramp the arrows by **$ cost** or **latency** — the legend scales to your real numbers.

<img src="docs/img/feat-lens.png" width="820" alt="Cost lens — arrows ramped by dollar cost with a scaled legend">

**Click any message for the full story.** A tiered detail card: *why* the call happens, what it changes, what fails, the credential that crosses, and the source files — captured by the agent while it reads your code.

<img src="docs/img/feat-detail.png" width="820" alt="Click-a-message detail card with why, changes, on-fail, chips and source">

Plus: **UML arrowheads** (call / return / async), **api / data-store markers**, **phase bands**, **opt / alt / loop fragments**, **sticky swimlane header**, and **⤓ PNG export** straight from the browser.

## Quickstart

```bash
git clone https://github.com/functioncall/sequence-diagram-skill.git

# Claude Code (user scope — available everywhere):
cp -r sequence-diagram-skill/sequence-diagram ~/.claude/skills/

# render the smallest example to see it live:
python3 sequence-diagram-skill/sequence-diagram/scripts/render_html.py \
        sequence-diagram-skill/sequence-diagram/examples/web-request.json index.html
open index.html      # interactive: click a row, toggle a lens, ⤓ export PNG
```

**Python 3 standard library only — nothing to `pip install`, no Node, no build step.** (PNG export runs in the browser.) Other harnesses: drop the `sequence-diagram/` folder into that harness's skills dir, or just point the model at `sequence-diagram/SKILL.md`.

## Using it

**With an agent** (the normal way) — just ask; the skill auto-loads from its description:

> "Diagram the checkout flow: web app → API → Stripe → Postgres, with the webhook path."
>
> "Make a sequence diagram of our login: iOS app, Firebase, Apple & Google providers."
>
> "Map every flow in this repo into one diagram file I can switch between."

The agent reads the code, authors the JSON, and runs the renderer. You only describe the flow.

**By hand** — write a spec and render it:

```bash
python3 sequence-diagram/scripts/render_html.py myflow.json index.html
```

### Spec schema in 30 seconds

A spec is one JSON object. Render any `examples/*.json` to see it live; here's the shape:

```jsonc
{
  "title": "Web request — cached read",
  "subtitle": "browser → API → cache, falling back to the DB",
  "actors": [                                   // the columns, left → right (order auto-sorted by zone)
    { "id": "user", "label": "User", "zone": "user",   "sub_caption": "browser" },
    { "id": "api",  "label": "API",  "zone": "server", "sub_caption": "/v1" },
    { "id": "db",   "label": "Postgres", "zone": "database" }
  ],
  "messages": [                                 // arrows, top → bottom, in order
    { "phase": "REQUEST" },                     // a labelled section band
    { "from": "user", "to": "api", "text": "GET /order/42", "paths": ["read"] },
    { "from": "api",  "to": "db",  "text": "SELECT order 42", "via": "io",
      "metrics": { "latency_ms": 35 } },
    { "from": "db",   "to": "api", "text": "row", "kind": "ret" }   // "ret" = dashed return
  ],
  "fragments": [                                // optional grouping boxes
    { "kind": "opt", "label": "cache miss", "range": [2, 3] }   // [firstMsg, lastMsg] index
  ]
}
```

| Field | Meaning |
|-------|---------|
| `actors[].zone` | swimlane role → colour (`user` / `client` / `server` / `cache` / `database` / vendor…). **Never set colours by hand** — zones drive the generated palette + the left→right order. |
| `messages[].kind` | `ret` = dashed return · `async` = open-tip event · omit = solid call. |
| `messages[].via` | `api` = crosses a network/trust boundary · `io` = a data-store read/write (each draws a small marker). |
| `messages[].paths` | tags a message to a **colour lens** (bottom toolbar toggles them). |
| `messages[].metrics` | `{ cost, latency_ms }` → enables the **$ cost / ⏱ latency** lenses. |
| `messages[].detail` | optional `{ why, sends, effects, fails, ordering, auth }` → the click-a-row detail card. |
| `{ "phase": "NAME" }` | a labelled section band across the diagram. |
| `fragments[]` | `opt` / `alt` / `loop` boxes spanning a `[start, end]` message range. |

Full field reference: [`sequence-diagram/USAGE.md`](sequence-diagram/USAGE.md) · design legend: [`sequence-diagram/STYLE.md`](sequence-diagram/STYLE.md).

## Examples

Render any of these immediately (`python3 sequence-diagram/scripts/render_html.py <file> index.html`):

| File | Shows |
|------|-------|
| [`examples/web-request.json`](sequence-diagram/examples/web-request.json) | smallest spec — phases, a return, one `opt` fragment, a colour lens. **Start here.** |
| [`examples/capture.json`](sequence-diagram/examples/capture.json) | a real, dense flow with metrics and multiple lenses. |
| [`examples/master-backdrop.json`](sequence-diagram/examples/master-backdrop.json) | a **master** — many scenarios in one, rendered to the scenario dropdown above. |

## What's inside

| Path | Purpose |
|------|---------|
| `SKILL.md` | The skill: when to use it + how to author specs. **Read this first.** |
| `USAGE.md` · `STYLE.md` | Full command reference · the visual design legend. |
| `scripts/render_html.py` | Renderer entrypoint: `render_html.py <spec\|master>.json [out.html]`. |
| `scripts/tokens.py` · `layout.py` | Single source of truth for colour/size · pure geometry (spec → primitives). |
| `scripts/assets/` | `page.html` / `app.css` / `app.js` inlined into the output. |
| `examples/` | Sample specs you can render immediately. |

The renderer is **frozen** — you write JSON data only, so the look is byte-identical every run. Never hardcode style outside `tokens.py`.

## License

[MIT](LICENSE) — do almost anything (use, copy, modify, sell, embed in closed-source software) **as long as you keep the copyright + license notice.** In return it:

- **shields the author** — an explicit *no warranty / no liability* clause: if it breaks your build, that's on you, not the author.
- **guarantees credit** — the author's name rides along in every copy.

MIT doesn't *stop* anyone copying the code — that's the point of open source; it just requires attribution and removes the author's liability. (Shipping with **no** license would mean the opposite: default copyright applies, so legally nobody may use or copy it at all — worse for something meant to be shared, and with no liability shield.)
