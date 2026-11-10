#!/usr/bin/env python3
"""PreToolUse guard for Bash: the aws CLI may only read.

Allowlist, not denylist: an aws call passes only when its operation is a
read verb (describe/get/list/...) or an explicitly allowed read, and is not
on the deny list (secrets, data downloads, credential minting). Anything the
guard cannot parse is denied (fail closed). Every aws call must also name
--profile explicitly.
"""
import json
import re
import shlex
import sys

READ_VERB = re.compile(r"^(describe|get|list|lookup|filter|search|simulate|head)(-|$)")

ALLOW = {
    ("logs", "start-query"),  # Logs Insights: read-only, billed per GB scanned
    ("logs", "stop-query"),
    ("logs", "tail"),
    ("s3", "ls"),
    ("configure", "list"),
    ("configure", "list-profiles"),
    ("configure", "get"),
}

DENY = {
    # secret values
    ("secretsmanager", "get-secret-value"),
    ("secretsmanager", "batch-get-secret-value"),
    ("ssm", "get-parameter"),
    ("ssm", "get-parameters"),
    ("ssm", "get-parameters-by-path"),
    ("ssm", "get-parameter-history"),
    # env vars and code download links
    ("lambda", "get-function"),
    ("lambda", "get-function-configuration"),
    # credential minting
    ("sts", "get-session-token"),
    ("sts", "get-federation-token"),
    ("ecr", "get-login-password"),
    ("ecr", "get-authorization-token"),
    ("codeartifact", "get-authorization-token"),
    # data-plane reads (customer data)
    ("s3api", "get-object"),
    ("s3api", "get-object-torrent"),
    ("dynamodb", "get-item"),
    ("dynamodb", "batch-get-item"),
    ("kinesis", "get-records"),
    ("kinesis", "get-shard-iterator"),
}

# Global options that consume the next token as their value.
VALUE_OPTS = {
    "--profile", "--region", "--output", "--query", "--endpoint-url",
    "--color", "--ca-bundle", "--cli-read-timeout", "--cli-connect-timeout",
    "--cli-binary-format",
}

SEPARATORS = {"|", "||", "&", "&&", ";", "(", ")", "\n"}
SHELL_WRAPPERS = {"bash", "sh", "zsh", "fish", "eval", "env", "sudo", "xargs", "timeout", "nohup", "command"}


def check_invocation(args):
    """args = tokens after `aws` up to the next separator. Returns a denial reason or None."""
    if "--profile" not in args and not any(a.startswith("--profile=") for a in args):
        return "aws calls must pass --profile explicitly"

    positional = []
    skip = False
    for a in args:
        if skip:
            skip = False
            continue
        if a.startswith("-"):
            if a in VALUE_OPTS:
                skip = True
            continue
        positional.append(a)
        if len(positional) == 2:
            break

    if len(positional) < 2:
        return None if positional in ([], ["help"]) else f"cannot tell the operation of `aws {' '.join(positional)}`"

    service, op = positional
    if op == "help":
        return None
    if (service, op) in DENY:
        return f"`{service} {op}` reads secrets, credentials or customer data"
    if service == "sts" and op != "get-caller-identity":
        return f"`sts {op}` is not allowed; only get-caller-identity"
    if service == "lambda" and op == "list-functions" and "--query" not in args:
        return "`lambda list-functions` returns env vars; pass --query to select fields"
    if service == "apigateway" and any(a.startswith("--include-value") for a in args):
        return "API key values are secrets"
    if (service, op) in ALLOW or READ_VERB.match(op):
        return None
    return f"`{service} {op}` is not a read operation"


def main():
    payload = json.load(sys.stdin)
    cmd = payload.get("tool_input", {}).get("command", "")
    if not re.search(r"\baws\b|boto3|aws-sdk", cmd):
        return

    reason = None
    if re.search(r"boto3|@aws-sdk|aws-sdk", cmd):
        reason = "AWS SDK scripts bypass the CLI guard; use the aws CLI"
    else:
        try:
            # Newlines separate commands; shlex would treat them as plain whitespace.
            lex = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=True)
            lex.whitespace_split = True
            lex.commenters = ""
            tokens = list(lex)
        except ValueError as e:
            tokens = None
            reason = f"could not parse command ({e})"

        if tokens is not None:
            at_cmd = True  # is this token in command position?
            after_wrapper = False
            for i, tok in enumerate(tokens):
                if tok in SEPARATORS:
                    at_cmd, after_wrapper = True, False
                    continue
                name = tok.rsplit("/", 1)[-1]
                if at_cmd and name == "aws" and not re.match(r"^\w+=", tok):
                    end = next((j for j in range(i + 1, len(tokens)) if tokens[j] in SEPARATORS), len(tokens))
                    reason = check_invocation(tokens[i + 1:end])
                    if reason:
                        break
                    at_cmd = False
                elif re.search(r"\baws\b", tok) and i > 0 and (
                    tokens[i - 1] == "-c" or tokens[i - 1].rsplit("/", 1)[-1] in {"eval", "bash", "sh", "zsh", "fish"}
                ):
                    reason = "aws inside a nested shell string can't be checked"
                    break
                elif at_cmd and (name in SHELL_WRAPPERS or re.match(r"^\w+=", tok)):
                    after_wrapper = after_wrapper or name in SHELL_WRAPPERS
                elif at_cmd and after_wrapper and (tok.startswith("-") or tok.isdigit() or tokens[i - 1].startswith("-")):
                    pass  # wrapper options and their values, such as `timeout 30` or `env -u X`
                else:
                    at_cmd = False

    if reason:
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"AWS read-only guard: {reason}",
            }
        }, sys.stdout)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # fail closed
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"AWS read-only guard crashed: {e}",
            }
        }, sys.stdout)
