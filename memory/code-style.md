---
name: code-style
description: Code style — React/TSX idioms, CSS units, comments, and fixing at the root
metadata:
  type: feedback
---

# Code style

## React / TSX

- **Arrow-function consts, not `function` declarations** — for components and module-level helpers, including the default export: `const Foo = (props) => { ... }` with `export default Foo;` at the bottom.
- **Fragment shorthand `<>...</>`**, not an imported `Fragment`. When a `.map()` needs a `key`, extract a small component that returns `<>...</>` and put the key on the instance.

## CSS / SCSS

- **Use `rem` for spacing**, not `px` (÷16: 4px→0.25rem, 8px→0.5rem). Idiomatic exceptions are fine: `1px` hairline borders, `1000px` pill radii.
- **Exception — `apps/pdf-report`:** use `px`. It renders fixed-size paged documents and is slated to migrate to `pt`, so absolute units are preferred there.

## Comments & references

- **No code comments** unless explicitly asked. No block comments, rationale paragraphs, or JSDoc explaining behavior. Prefer renaming/restructuring to make code self-explanatory. (Test descriptions and prompt-string literals aren't code comments — those are fine.)
- **"Constraint" comments don't get a pass either.** A cross-file constraint (e.g. why a z-index value must exceed other components' values) still isn't worth a comment — Chris had it removed on ENG-4854 (2026-07-31, "Do not over-explain things"). Put that context in the PR body if it matters. Repeated 2026-08-03 (ENG-4856): a why-imperative-navigation rationale comment in apps/mobile App.tsx drew "let's not over-comment please" — removed entirely, not just trimmed. Existing comment density in apps/mobile does NOT license new comments.
- **This applies to CI/pipeline files too** (workflows, scripts, actions) — even though the repo's existing workflows are heavily commented, don't match that. Chris (2026-07-24, ENG-4827): "let's avoid over-commenting and over-explaining all the pipeline." At most a one-line note for a genuinely non-obvious constraint. Rationale for tool/approach choices is NOT that — it belongs in the PR body (Chris removed a "why expo-doctor was swapped" comment, 2026-07-24). Repeated 2026-07-28 ("avoid over-explaining and over-commenting") after Claude wrote multi-line rationale comments in config.ts / deploy.yml — the rule covers chat verbosity too, keep explanations tight.
- **No ticket references in code** (`ENG-XXXX`, `JIRA-123`) — not in comments, error messages, or logs. They rot fast. Ticket IDs belong in commits and PRs.
- **Migrations get the template JSDoc and nothing else.** No rationale for index naming, column ordering, or why an old index is dropped. On ENG-4870 (2026-08-11) Chris removed three separate comments in two migration files — "Do not add that temp index probe. Just the migration", then "No comments. Just the migration." Reviewer-facing rationale is NOT an exception to the no-comments rule, and neither is a marker for deliberately temporary code; both belong in the PR body or the Slack thread.

## Fixing bugs

- **Fix at the root, not with shims** — even when a shim is smaller/safer. Prefer explicit structural separation (fork/quarantine the legacy path under clear names, make the correct system canonical) over runtime-conditional indirection. Present the root fix first; offer stopgaps only when explicitly labeled as such.
