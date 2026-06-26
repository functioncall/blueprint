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
