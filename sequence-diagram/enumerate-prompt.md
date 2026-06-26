# Enumerate prompt — "list the flows" (handed to ONE agent)

Your job is to produce the **menu** of user journeys worth diagramming. You do **not** draw
anything — you return a JSON list the skill shows the user to pick from.

Read the app's surface: the entry point / root view / router, the screens, the
tab/stack/navigation definitions, the buttons and the actions they fire, the API route
files, and the auth / purchase / account entry points. Cover the whole product.

## Output — ONLY a JSON array, one item per journey
```json
[
  { "id": "ask", "title": "Ask a question about the scene",
    "subtitle": "one line: what the user does → what happens",
    "source_paths": ["Packages/.../Ask", "server/src/ask"],
    "size": "M",          // S ≤6 steps · M ~7–14 · L 15+ (rough)
    "network": true }     // true = hits server/vendor · false = pure client navigation
]
```

## Rules
- **EXCLUDE anything already drawn.** You will be given the list of existing scenario ids —
  do not return those. Only return what's **missing or new**.
- **One journey per real user goal** (capture, ask, buy premium, restore purchases, sign in,
  sign out, delete account, onboarding / permission grant, browse…). Don't split one goal
  into several entries, and don't merge two goals into one.
- **`source_paths` must be specific** — the files/dirs that actually implement the journey, so
  the skill can re-check freshness later from git.
- **Only REAL journeys** — read the code; never invent a flow, screen, or endpoint.
- Output the JSON array and **nothing else** (no prose, no fences if avoidable).
