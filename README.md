# sequence-diagram (Agent Skill)

Render real, **interactive sequence diagrams** as a single self-contained `index.html` —
drafting-paper look, generated OKLCH palette, swimlane headers, phase sections, combined
fragments, switchable colour lenses, and in-browser PNG export. You only ever author JSON;
a frozen renderer turns it into the same diagram every run, on any project.

It's an [Agent Skill](https://code.claude.com/docs/en/skills) (`SKILL.md` + a folder). The
`SKILL.md` folder layout is a cross-harness convention, so this works with any agent that
reads skills — **Claude Code, Codex, Gemini CLI, Cursor**, etc. — and the renderer itself is
just a Python script, so even a harness with no skill support can call it directly.

## Requirements

- **Python 3** — standard library only. **Nothing to `pip install`.**
- That's it. No Node, no build step. (PNG export happens in the browser.)

## Install

Drop the `sequence-diagram/` folder into your agent's skills directory.

```bash
git clone https://github.com/<you>/sequence-diagram-skill.git

# Claude Code (user scope, available everywhere):
cp -r sequence-diagram-skill/sequence-diagram ~/.claude/skills/

# or project scope:
cp -r sequence-diagram-skill/sequence-diagram <your-repo>/.claude/skills/
```

Start a new session — the skill auto-loads from its `description` when you ask for a sequence
diagram. (Other harnesses: copy the folder into that harness's skills dir, or just point the
model at `sequence-diagram/SKILL.md`.)

If you use the [`gh-skill`](https://cli.github.com/manual/gh_skill_install) extension:

```bash
gh skill install <you>/sequence-diagram-skill
```

## Smoke test (proves it works without an agent)

```bash
cd sequence-diagram
python3 scripts/render_html.py examples/web-request.json index.html
open index.html      # interactive diagram, click any message, ⤓ exports PNG
```

## Using it

**With an agent** (the normal way) — just ask, and the skill auto-loads from its description:

> "Make a sequence diagram of the login flow: browser → API → Redis → Postgres."

The agent authors the JSON and runs the renderer for you. You only ever describe the flow.

**By hand** — write a spec and render it:

```bash
python3 sequence-diagram/scripts/render_html.py myflow.json index.html
```

### Spec schema in 30 seconds

A spec is one JSON object. Render any of `examples/*.json` to see it live; here's the shape:

```jsonc
{
  "title": "Web request — cached read",
  "subtitle": "browser → API → cache, falling back to the DB",
  "actors": [                                   // the columns, left → right
    { "id": "user", "label": "User", "zone": "user",   "sub_caption": "browser" },
    { "id": "api",  "label": "API",  "zone": "server", "sub_caption": "/v1" },
    { "id": "db",   "label": "Postgres", "zone": "database" }
  ],
  "messages": [                                 // arrows, top → bottom, in order
    { "phase": "REQUEST" },                     // a labelled section divider
    { "from": "user", "to": "api", "text": "GET /order/42", "paths": ["read"] },
    { "from": "api",  "to": "db",  "text": "SELECT order 42", "metrics": { "latency_ms": 35 } },
    { "from": "db",   "to": "api", "text": "row", "kind": "ret" }   // "ret" = dashed return
  ],
  "fragments": [                                // optional grouping boxes
    { "kind": "opt", "label": "cache miss", "range": [2, 3] }   // [firstMsg, lastMsg] index
  ]
}
```

| Field | Meaning |
|-------|---------|
| `actors[].zone` | swimlane group → colour (`user` / `client` / `server` / `cache` / `database` …). Never set colours by hand — zones drive the palette. |
| `messages[].kind` | `ret` = dashed return arrow; omit for a solid call. |
| `messages[].paths` | tags a message to a **colour lens** (the bottom toolbar toggles them). |
| `{ "phase": "NAME" }` | a labelled section band across the diagram. |
| `fragments[]` | `opt` / `loop` / `alt` boxes spanning a `[start, end]` message range. |

Full field reference: [`sequence-diagram/USAGE.md`](sequence-diagram/USAGE.md) · design legend: [`sequence-diagram/STYLE.md`](sequence-diagram/STYLE.md).

## Examples

Render any of these immediately (`python3 sequence-diagram/scripts/render_html.py <file> index.html`):

| File | Shows |
|------|-------|
| [`examples/web-request.json`](sequence-diagram/examples/web-request.json) | smallest spec — phases, a return, one `opt` fragment, colour lens. Start here. |
| [`examples/capture.json`](sequence-diagram/examples/capture.json) | a real, dense flow with metrics and multiple lenses. |
| [`examples/master-backdrop.json`](sequence-diagram/examples/master-backdrop.json) | a **master** file — many scenarios in one, rendered to a scenario dropdown. |

## What's inside

| Path | Purpose |
|------|---------|
| `SKILL.md` | The skill: when to use it + how to author specs. Read this first. |
| `USAGE.md` | Command reference (render, freshness, validate, provenance). |
| `STYLE.md` | The visual design legend. |
| `scripts/render_html.py` | Renderer entrypoint: `render_html.py <spec\|master>.json [out.html]`. |
| `scripts/tokens.py` | Single source of truth for every colour/size. |
| `scripts/layout.py` | Pure geometry (spec → positioned primitives). |
| `scripts/assets/` | `page.html` / `app.css` / `app.js` inlined into the output. |
| `examples/` | Sample specs you can render immediately. |

The renderer is **frozen** (`tokens.py` → `layout.py` → `render_html.py` + `assets/`): you
write JSON data only, so the look is byte-identical every run. Never hardcode style outside
`tokens.py`.

## License

MIT — see [LICENSE](LICENSE).
