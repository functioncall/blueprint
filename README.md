<div align="center">

<img src="docs/img/logo.png" width="540" alt="Blueprint">

*Interactive sequence diagrams, drawn from your code.*

![license](https://img.shields.io/badge/license-MIT-555?style=flat-square)
![agent skill](https://img.shields.io/badge/agent_skill-SKILL.md-555?style=flat-square)
![python](https://img.shields.io/badge/python_3-zero_deps-555?style=flat-square)
![output](https://img.shields.io/badge/output-self--contained_HTML-555?style=flat-square)

<img src="docs/video/blueprint-web.webp" width="100%" alt="Switching scenarios and lighting up a path in a rendered blueprint">

</div>

Describe a flow to your coding agent. It reads your code and renders an interactive sequence diagram. The layout and colours are fixed, so every diagram comes out consistent and you never touch styling.

It's an [Agent Skill](https://code.claude.com/docs/en/skills): a `SKILL.md` and a Python script, zero dependencies. It runs in Claude Code, Codex, Cursor, Gemini, or any tool that reads skills.

## Install

Let your agent install it:

1. Give it the link to this repo.
2. Say: *"Install this skill from its SKILL.md."*

It copies the folder into your skills directory. Nothing to configure.

<details>
<summary>Prefer to do it by hand?</summary>

```bash
git clone https://github.com/functioncall/blueprint.git
cp -r blueprint/blueprint ~/.claude/skills/
```

Python 3, standard library only.
</details>

## Use it

Just ask:

> *"Diagram our checkout flow: web app, API, Stripe, Postgres, with the webhook path."*
>
> *"Make a sequence diagram of our login — iOS app, Firebase, Apple and Google."*
>
> *"Map every flow in this repo into one file I can switch between."*

Your agent reads the code, writes the spec, and renders the diagram. Point it at a whole repo and it maps every flow into one file, then only redraws the ones that change.

Prefer to write the spec yourself? The format is in [`SKILL.md`](blueprint/SKILL.md) and [`USAGE.md`](blueprint/USAGE.md).

## What you get

- **One file, every flow.** A whole product in one place. Switch scenarios from a dropdown — same lanes and colours every time.
- **Colour lenses.** Light up one path from start to finish, or shade the arrows by cost or latency against your real numbers.
- **Click any row for the detail.** Why the call happens, what it changes, what breaks, and the files behind it — filled in by your agent as it reads the code.
- **Run it again and it only redraws what changed.** The file remembers the git SHA it was built from. The next run diffs that against `HEAD` and re-reads only the flows whose files actually moved. The rest are left byte for byte. Twelve flows, one changed route, one flow redrawn.
- **Export to PNG.** One click saves the whole diagram, swimlane header and all, as a crisp image for a doc or a PR.

Plus UML arrows, markers for network calls and data stores, phase bands, `opt` / `alt` / `loop` boxes, and a sticky header.

## Under the hood

Two ways in: hand-author one flow, or point it at a repo and let it map the lot.

```
blueprint
│
├─ ONE FLOW ─ you author it
│    └─ copy an example ──► edit JSON ──► render ──► index.html
│
└─ WHOLE REPO ─ project mode, cached and self-freshening
     │
     ├─ LOCATE
     │    └─ agent_docs/diagrams/architecture.json        (else docs/diagrams/)
     │
     ├─ SCOUT ─ what actually needs drawing?
     │    ├─ no master ────► enumerate every flow         (first build)
     │    │
     │    ├─ master ──┬──► freshness ──► git_sha vs HEAD
     │    │           │       └─ moved ──► stale flows    (source_paths touched)
     │    │           └──► enumerate ───► new flows
     │    │                     │
     │    │                     ▼
     │    │                candidates
     │    │
     │    └─ fresh, nothing new? ──────► skip to SEAL     (re-render only)
     │
     ├─ GATE ──► YOU tick the flows                       (or "draw all")
     │
     ├─ DRAW ─ one agent per flow
     │    ├─ flow A ─┐
     │    ├─ flow B ─┤   each reads only its source_paths
     │    └─ flow C ─┘   each reuses the master's actors
     │         │
     │         ▼
     │    scenarios[]
     │
     ├─ MERGE ──► add / replace by id                     (rest byte-for-byte)
     │
     ├─ SEAL
     │    ├─ validate ──────► must pass
     │    ├─ stamp ─────────► git_sha = HEAD              (baseline for next run)
     │    └─ render ────────► index.html
     │
     └─ SHIP ──► open / screenshot ──► commit JSON + HTML
          │
          └┄┄ next run ┄┄► SCOUT                          (redraw only what moved)
```

The gate is the only place you have to show up. The dashed line at the bottom is what makes the second run cheap.

## The JSON is half the value

You asked for a diagram. You also get the file it renders from, `agent_docs/diagrams/architecture.json`.

Every flow in it names the paths it lives in and the file behind each call. So the file doubles as a map of your codebase, written by an agent that had just read it properly.

Hand it to the next agent before it starts a task. It skips the scouting, opens the right files first time, and gets on with the work. Same for a new hire, or for you after six months away.

## License

MIT. [LICENSE](LICENSE)
