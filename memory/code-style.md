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
- **No ticket references in code** (`ENG-XXXX`, `JIRA-123`) — not in comments, error messages, or logs. They rot fast. Ticket IDs belong in commits and PRs.

## Fixing bugs

- **Fix at the root, not with shims** — even when a shim is smaller/safer. Prefer explicit structural separation (fork/quarantine the legacy path under clear names, make the correct system canonical) over runtime-conditional indirection. Present the root fix first; offer stopgaps only when explicitly labeled as such.
