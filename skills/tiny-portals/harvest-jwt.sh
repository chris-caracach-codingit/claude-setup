#!/usr/bin/env bash
# Harvest a Results JWT straight from the sandbox auth API and write it into
# PDF_ADMIN_JWT in credentials.env — no browser required.
#
# Usage:  ./harvest-jwt.sh [ACCOUNT]
#   ACCOUNT is the credentials.env suffix, e.g. NEWBORN or BIO. When omitted it
#   defaults to PDF_DEFAULT from credentials.env (falling back to NEWBORN).
#   Reads RESULTS_EMAIL_<ACCOUNT> / RESULTS_PASS_<ACCOUNT>.
#
# Sandbox only. Never prints the token; confirms with a 6-char mask + expiry.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV="$DIR/credentials.env"
API="${SANDBOX_API_URL:-https://sandbox-api.tinyhealth.com}"

set -a; source "$ENV"; set +a

ACCOUNT="${1:-${PDF_DEFAULT:-NEWBORN}}"

EMAIL_VAR="RESULTS_EMAIL_${ACCOUNT}"
PASS_VAR="RESULTS_PASS_${ACCOUNT}"
EMAIL="${!EMAIL_VAR:-}"
PASS="${!PASS_VAR:-}"

if [[ -z "$EMAIL" || -z "$PASS" ]]; then
  echo "ERROR: $EMAIL_VAR / $PASS_VAR are blank in credentials.env" >&2
  exit 1
fi

RESP="$(curl -fsS -X POST "$API/auth/login" \
  -H 'Content-Type: application/json' \
  -d "$(E="$EMAIL" P="$PASS" python3 -c 'import json,os;print(json.dumps({"email":os.environ["E"],"password":os.environ["P"]}))')")"

TOKEN="$(printf '%s' "$RESP" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("token",""))')"
if [[ -z "$TOKEN" ]]; then
  echo "ERROR: no token in response" >&2
  exit 1
fi

# Splice into PDF_ADMIN_JWT (replace existing line or append)
python3 - "$ENV" "$TOKEN" <<'PY'
import sys, re
path, tok = sys.argv[1], sys.argv[2]
lines = open(path).read().splitlines()
out, done = [], False
for ln in lines:
    if re.match(r'\s*PDF_ADMIN_JWT\s*=', ln):
        out.append(f"PDF_ADMIN_JWT={tok}"); done = True
    else:
        out.append(ln)
if not done: out.append(f"PDF_ADMIN_JWT={tok}")
open(path, 'w').write("\n".join(out) + "\n")
PY

EXP="$(printf '%s' "$TOKEN" | python3 -c 'import json,sys,base64,datetime
p=sys.stdin.read().split(".")[1]; p+="="*(-len(p)%4)
exp=json.loads(base64.urlsafe_b64decode(p)).get("exp")
print(datetime.datetime.fromtimestamp(exp, datetime.timezone.utc).isoformat() if exp else "n/a")')"

echo "PDF_ADMIN_JWT updated for account '$ACCOUNT' ($EMAIL)"
echo "  token: set, ${#TOKEN} chars, …${TOKEN: -6}"
echo "  expires: $EXP"
