export const meta = {
  name: 'blueprint-draw',
  description: 'Draw one blueprint scenario per chosen flow, in parallel',
  phases: [{ title: 'Draw' }],
}

// TEMPLATE — replace the four `repo`/`masterPath`/`skillDir`/`flows` consts below with literals
// for the run, WRITE the filled-in script to a file, and launch it with `Workflow({scriptPath})`.
//   flows: [{id, title, subtitle, source_paths}, ...]
// Returns { scenarios: [<v3 scenario object>, ...] } — the main loop merges + renders.
// (Workflow scripts have no filesystem access, so merge/validate/render happen in the main loop.)
// ⚠️ Bake the values into the consts below — do NOT pass them via the Workflow `args` field
//    (observed: args does not reach the script, so it runs with 0 flows).
// ⚠️ Prefer `scriptPath` (a file) over passing the whole script inline: inline embedding can
//    mangle the prompt strings. This template therefore uses plain string concatenation (no
//    `${…}` template literals) so it parses cleanly either way — keep it that way.

// >>> the main loop replaces these four literals for each run:
const repo = '/ABS/PATH/TO/REPO'
const masterPath = repo + '/agent_docs/diagrams/architecture.json'
const skillDir = '/ABS/PATH/TO/.claude/skills/blueprint'
const flows = [ /* {id, title, subtitle, source_paths:[...]}, ... */ ]

const SCENARIO_SCHEMA = {
  type: 'object',
  additionalProperties: true,
  required: ['id', 'title', 'actors', 'messages'],
  properties: {
    id: { type: 'string' },
    title: { type: 'string' },
    subtitle: { type: 'string' },
    source_paths: { type: 'array', items: { type: 'string' } },
    meta: { type: 'object', additionalProperties: true },
    actors: {
      type: 'array',
      minItems: 1,
      items: {
        type: 'object',
        additionalProperties: true,
        required: ['id', 'label', 'zone'],
        properties: {
          id: { type: 'string' },
          label: { type: 'string' },
          zone: { type: 'string' },
          kind: { type: 'string' },
          sub_caption: { type: 'string' },
          sub: { type: 'array', items: { type: 'object', additionalProperties: true } },
        },
      },
    },
    messages: { type: 'array', minItems: 1, items: { type: 'object', additionalProperties: true } },
    fragments: { type: 'array', items: { type: 'object', additionalProperties: true } },
  },
}

if (!flows.length) {
  log('no flows passed — nothing to draw')
  return { scenarios: [] }
}

log('drawing ' + flows.length + ' scenario(s), one agent each')

// NOTE: plain string concatenation only (no `${…}` template literals) so this parses cleanly
// whether run from a file or embedded inline.
const drawn = await parallel(
  flows.map((f) => () => {
    const paths = (f.source_paths || []).join(', ') || '(locate from the repo)'
    const masterStep = masterPath
      ? '2. Read the existing master at ' + masterPath + ' and REUSE its actor ids + zones wherever the same real component appears, so the set stays visually consistent.'
      : '2. (No existing master — choose clear actor ids/zones.)'
    const prompt = [
      'Draw EXACTLY ONE blueprint scenario as a v3 JSON object.',
      '',
      'Flow id: ' + f.id,
      'Title: ' + f.title,
      f.subtitle ? 'What it is: ' + f.subtitle : '',
      'Repo: ' + repo,
      'Trace it by reading ONLY these paths (plus what they reference): ' + paths,
      '',
      '1. Read the rules + schema in ' + skillDir + '/scenario-prompt.md and the "Spec schema (v3)" section of ' + skillDir + '/SKILL.md.',
      masterStep,
      '3. Read the real code for this flow — never invent behaviour.',
      '',
      'Return ONE scenario object (id, title, subtitle, meta, source_paths, actors, messages, fragments). Output only the object.',
    ].filter(Boolean).join('\n')
    return agent(prompt, { label: 'draw:' + f.id, phase: 'Draw', schema: SCENARIO_SCHEMA })
  }),
)

const scenarios = drawn.filter(Boolean)
log('drew ' + scenarios.length + '/' + flows.length)
return { scenarios }
