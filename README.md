<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/logo-dark.png">
  <img src="docs/img/logo-light.png" width="540" alt="Sequence Diagrams">
</picture>

*Interactive sequence diagrams, drawn from your code.*

![license](https://img.shields.io/badge/license-MIT-555?style=flat-square)
![agent skill](https://img.shields.io/badge/agent_skill-SKILL.md-555?style=flat-square)
![python](https://img.shields.io/badge/python_3-zero_deps-555?style=flat-square)
![output](https://img.shields.io/badge/output-self--contained_HTML-555?style=flat-square)

<img src="docs/img/hero.png" width="820" alt="A sign-in flow with the Google path lit up">

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
git clone https://github.com/functioncall/sequence-diagram-skill.git
cp -r sequence-diagram-skill/sequence-diagram ~/.claude/skills/
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

Prefer to write the spec yourself? The format is in [`SKILL.md`](sequence-diagram/SKILL.md) and [`USAGE.md`](sequence-diagram/USAGE.md).

## What you get

**One file, every flow.** A whole product in one place. Switch scenarios from a dropdown — same lanes and colours every time.

<img src="docs/img/feat-scenarios.png" width="440" alt="A dropdown listing every flow in one file">

**Colour lenses.** Light up one path from start to finish, or shade the arrows by cost or latency against your real numbers.

<img src="docs/img/feat-lens.png" width="800" alt="The cost lens shading arrows, with a scaled legend">

**Click any row for the detail.** Why the call happens, what it changes, what breaks, and the files behind it — filled in by your agent as it reads the code.

<img src="docs/img/feat-detail.png" width="600" alt="A click-a-row detail card with why, what changes, on-fail, and source files">

**Export to PNG.** One click saves the whole diagram, swimlane header and all, as a crisp image for a doc or a PR.

Plus UML arrows, markers for network calls and data stores, phase bands, `opt` / `alt` / `loop` boxes, and a sticky header.

## License

MIT. [LICENSE](LICENSE)
