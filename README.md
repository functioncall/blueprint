<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/img/logo-dark.png">
  <img src="docs/img/logo-light.png" width="540" alt="Sequence Diagrams">
</picture>

*See the conversations hidden in your code.*

![license](https://img.shields.io/badge/license-MIT-555?style=flat-square)
![agent skill](https://img.shields.io/badge/agent_skill-SKILL.md-555?style=flat-square)
![python](https://img.shields.io/badge/python_3-zero_deps-555?style=flat-square)
![output](https://img.shields.io/badge/output-self--contained_HTML-555?style=flat-square)

<img src="docs/img/hero.png" width="820" alt="A sign-in flow with the Google path lit up">

<em>Click any row, switch scenarios, export a PNG — all from one HTML file.</em>

</div>

It takes a flow you describe and draws it as a real, clickable sequence diagram — one HTML file you can open in any browser, click around, and save as an image. Write a little JSON, or just ask your agent. The look is fixed, so you never pick colours or wrestle with layout. You say what happens; it draws it the same way every time.

It's an [Agent Skill](https://code.claude.com/docs/en/skills): just a folder with a `SKILL.md` and a small Python script. No Node, no build step, nothing to install. It works in Claude Code, Codex, Cursor, Gemini, or anything else that reads skills.

## Install

The easy way is to let your agent do it:

1. Give your agent the link to this repo.
2. Say: *"Install this skill from its SKILL.md."*

It drops the folder into your skills directory and you're done. No dependencies, no build, nothing to set up.

<details>
<summary>Rather do it by hand?</summary>

```bash
git clone https://github.com/functioncall/sequence-diagram-skill.git
cp -r sequence-diagram-skill/sequence-diagram ~/.claude/skills/
```

Python 3, standard library only. Nothing to install.
</details>

## Use it

Most of the time you just ask. The skill loads itself and writes the JSON for you:

> *"Diagram our checkout flow: web app, API, Stripe, Postgres, with the webhook path."*
>
> *"Make a sequence diagram of our login — iOS app, Firebase, Apple and Google."*
>
> *"Map every flow in this repo into one file I can switch between."*

It reads the code, draws the diagram, and hands you the HTML. You only describe the flow. Point it at a whole repo and it maps everything, sends one agent per flow, then only redraws the flows that actually changed.

Want to write specs by hand or see every field? It's all in [`SKILL.md`](sequence-diagram/SKILL.md) and [`USAGE.md`](sequence-diagram/USAGE.md).

## What you get

**One file, every flow.** A whole product in one place. Switch scenarios from a dropdown — same lanes, same colours, every time.

<img src="docs/img/feat-scenarios.png" width="440" alt="A dropdown listing every flow in one file">

**Colour lenses.** Light up one path from start to finish, or shade the arrows by cost or latency. The scale matches your real numbers.

<img src="docs/img/feat-lens.png" width="800" alt="The cost lens shading arrows, with a scaled legend">

**Click any row for the story.** Why the call happens, what it changes, what breaks, and the files behind it. Your agent fills this in as it reads the code.

<img src="docs/img/feat-detail.png" width="600" alt="A click-a-row detail card with why, what changes, on-fail, and source files">

**Export to PNG.** One click saves the whole diagram — swimlane header and all — as a crisp image you can drop in a doc or a PR.

You also get proper UML arrows, markers for network calls and data stores, phase bands, `opt` / `alt` / `loop` boxes, and a sticky header.

## License

MIT — do what you like with it. [LICENSE](LICENSE)
