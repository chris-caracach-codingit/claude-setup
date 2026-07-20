# Tiny Health portal access rules (for Claude Code + Chrome DevTools MCP)

Copy this skeleton to `~/prog/tiny-portals/ACCESS_RULES.md` and fill in your
verified ports, backends, and account layout. That real file stays untracked.
The `tiny-portals` skill reads it at runtime.

## Hard rules

- Sandbox/test accounts only. Never production, never real-user data.
- Never echo a secret value into chat, a commit, a log, or a screenshot.
- Never start/stop/restart servers — the user runs those.
- Browser is read-only except the sanctioned login flow and the PDF JWT cookie.

## App registry (verified <date>)

| Portal | URL | Start command | Backend |
|---|---|---|---|
| Results | http://localhost:PORT | `…` | … |
| Practitioner | … | … | … |
| Partner | … | … | … |
| Ops | … | … | … |
| PDF report | … | … | … |

## Standard procedure (Practitioner, Partner, Ops)

<how to log in>

## Results Portal (multiple accounts)

<account switching notes>

## PDF Report (JWT harvested from Results)

### Refresh / populate the PDF JWT (on demand)

<steps; see harvest-jwt.sh>

### View a report

<steps>

## Notes

<anything else>
