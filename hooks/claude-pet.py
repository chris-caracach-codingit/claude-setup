#!/usr/bin/env python3
"""Claude Code pet: a tiny bottom-right popup that appears when Claude runs
commands worth knowing about (git push, Slack sends, docker/db, vercel).

Hook mode (default): reads the PreToolUse JSON on stdin, decides whether it
matches a watched pattern, and if so spawns a detached popup. Never blocks
and never exits non-zero, so it can only alert, not stop Claude.

Popup mode (--show CATEGORY BODY): renders the pet with GTK3. Internal.
"""

import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

RUNTIME_DIR = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
REG_DIR = RUNTIME_DIR / "claude-pet"  # one file per live popup: "<ts>-<pid>" -> height
THEME_DUNST = Path("~/.config/themes/current/dunst.conf").expanduser()

FONT = "Hack Nerd Font Mono 10"
TIMEOUT_MS = 10000
MARGIN = 16
GAP = 8
MAX_STACK = 6

# --------------------------------------------------------------------------
# What to watch. Bash commands are matched against the whole command string;
# MCP tools are matched by tool name.
# --------------------------------------------------------------------------

BASH_WATCH = [
    ("git push", r"\bgit\s+push\b"),
    ("git commit", r"\bgit\s+commit\b"),
    ("database", r"\b(bun\s+(run\s+)?db:|knex\b|mysql(dump)?\b|psql\b|drizzle-kit\b)"),
    ("docker", r"^docker(-compose)?\b"),
    # only the CLI itself (vercel / vc), directly or via a package runner;
    # `cat vercel.json` or a commit message mentioning vercel must not fire
    ("vercel", r"^(?:(?:npx|bunx|yarn|yarn\s+dlx|pnpm\s+(?:dlx|exec)|npm\s+exec|bun\s+x)\s+(?:-\S+\s+)*)?(?:vercel|vc)(?:@\S+)?(?:\s|$)"),
    ("rm", r"^rm(dir)?\s"),
]

TOOL_WATCH = [
    ("slack", r"^mcp__.*slack.*(send|schedule)_message$"),
]

# --------------------------------------------------------------------------
# The pet: a 12x16 pixel-art robot, drawn at PIXEL px per cell.
#   .  transparent     D  outline (dark)     B  body
#   E  eyes            M  mouth              A  accent (antenna tip, chest light)
# --------------------------------------------------------------------------

ROBOT = """
.....AA.....
.....DD.....
..DDDDDDDD..
.DBBBBBBBBD.
.DBEEBBEEBD.
.DBEEBBEEBD.
.DBBBBBBBBD.
.DBDMMMMDBD.
.DBBBBBBBBD.
..DDDDDDDD..
....DDDD....
.DDDBBBBDDD.
DBDBBAABBDBD
DBDBBBBBBDBD
.D.DDDDDD.D.
...DD..DD...
""".strip("\n").splitlines()
PIXEL = 4
BLINK_EVERY_MS = 2800
BLINK_MS = 130

SAYINGS = {
    "git push": "pushing to the remote!",
    "git commit": "making a commit!",
    "docker": "poking docker!",
    "database": "touching a database!",
    "vercel": "running the vercel CLI!",
    "slack": "sending a slack message!",
    "rm": "removing something!",
}


SPLIT = re.compile(r"\s*(?:&&|\|\||;|\||\n)\s*")
HEREDOC = re.compile(r"(<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n).*?^\2\s*$", re.S | re.M)
CWD_SENSITIVE = {"docker", "database", "vercel"}


def resolve(path, cwd):
    path = os.path.expandvars(os.path.expanduser(path))
    return os.path.normpath(path if os.path.isabs(path) else os.path.join(cwd, path))


def segments(cmd, cwd):
    """Yield (segment, words, cwd) for each simple command, tracking `cd`.
    Heredoc bodies and comments are ignored so file contents can't trigger."""
    import shlex
    cmd = HEREDOC.sub(r"\1", cmd)
    for seg in SPLIT.split(cmd):
        seg = seg.strip().lstrip("({ ").rstrip(")} ")
        if not seg or seg.startswith("#"):
            continue
        try:
            words = shlex.split(seg, comments=True)
        except ValueError:
            words = seg.split()
        while words and words[0] in ("sudo", "env", "nohup", "time"):
            words = words[1:]
        if words and words[0] in ("cd", "pushd"):
            cwd = resolve(words[1] if len(words) > 1 else "~", cwd)
            continue
        if words:
            yield seg, words, cwd


def rm_targets(words):
    return [w for w in words[1:] if not w.startswith("-")]


def match(payload):
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    for category, pattern in TOOL_WATCH:
        if re.search(pattern, tool):
            body = tool_input.get("channel_id") or tool_input.get("channel") or ""
            text = tool_input.get("text") or tool_input.get("message") or ""
            return category, " ".join(x for x in (body, text) if x)
    if tool != "Bash":
        return None
    cmd = tool_input.get("command") or ""
    start_cwd = payload.get("cwd") or os.getcwd()
    for seg, words, cwd in segments(cmd, start_cwd):
        probe = " ".join(words)
        for category, pattern in BASH_WATCH:
            if not re.search(pattern, probe):
                continue
            if category == "rm":
                targets = rm_targets(words) or [seg]
                return category, "\n".join(resolve(t, cwd) for t in targets)
            if category in CWD_SENSITIVE:
                return category, f"{seg}\nin {cwd}"
            return category, seg
    return None


def live_entries():
    """Popups currently on screen, oldest first: (ts, pid, height, path)."""
    REG_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for f in REG_DIR.iterdir():
        try:
            ts, pid = f.name.split("-")
            pid = int(pid)
            os.kill(pid, 0)  # raises if that popup is gone
            entries.append((float(ts), pid, int(f.read_text() or 0), f))
        except (ValueError, OSError):
            f.unlink(missing_ok=True)
    return sorted(entries)


def spawn_popup(category, body):
    entries = live_entries()
    while len(entries) >= MAX_STACK:  # drop the oldest to make room
        _, pid, _, f = entries.pop(0)
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
        f.unlink(missing_ok=True)
    subprocess.Popen(
        [sys.executable, __file__, "--show", category, body],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def theme_colors():
    colors = {"background": "#0f111a", "foreground": "#a6accd", "frame_color": "#82aaff"}
    try:
        text = THEME_DUNST.read_text()
        block = text.split("[urgency_normal]", 1)[1].split("[", 1)[0]
        for key in colors:
            m = re.search(rf'{key}\s*=\s*"?(#[0-9a-fA-F]{{6}})', block)
            if m:
                colors[key] = m.group(1)
    except (OSError, IndexError):
        pass
    return colors


def shorten(text, width=72, lines=4):
    out = []
    for raw in text.splitlines():
        raw = raw.rstrip()
        while raw and len(out) < lines:
            out.append(raw[:width])
            raw = raw[width:]
        if len(out) >= lines:
            break
    if len(out) == lines and (len(text.splitlines()) > lines or any(len(l) > width for l in text.splitlines())):
        out[-1] = out[-1][: width - 1] + "…"
    return "\n".join(out) or "(no details)"


def show(category, body):
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, GLib, Gtk, Pango

    colors = theme_colors()
    css = Gtk.CssProvider()
    css.load_from_data(f"""
        .pet-box {{ background-color: {colors['background']}; border: 2px solid {colors['frame_color']}; padding: 10px; }}
        .pet-art {{ color: {colors['frame_color']}; }}
        .pet-say {{ color: {colors['foreground']}; }}
        .pet-body {{ color: {colors['foreground']}; opacity: 0.8; }}
    """.encode())
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    win = Gtk.Window(type=Gtk.WindowType.POPUP)  # override-redirect: WM leaves it alone
    win.set_keep_above(True)
    win.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)

    font = Pango.FontDescription(FONT)

    def label(text, cls):
        l = Gtk.Label(label=text)
        l.set_xalign(0)
        l.set_valign(Gtk.Align.CENTER)
        l.override_font(font)
        l.get_style_context().add_class(cls)
        return l

    def hex_rgb(h):
        return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))

    def mix(c, toward, amount):
        return tuple(a + (b - a) * amount for a, b in zip(c, toward))

    base = hex_rgb(colors["frame_color"])
    palette = {
        "B": base,
        "D": mix(base, (0, 0, 0), 0.55),
        "E": mix(hex_rgb(colors["foreground"]), (1, 1, 1), 0.6),
        "M": mix(base, (0, 0, 0), 0.75),
        "A": (1.0, 0.80, 0.42),
    }
    state = {"blink": False}

    def draw(widget, cr):
        for y, row in enumerate(ROBOT):
            for x, ch in enumerate(row):
                if ch == ".":
                    continue
                if ch == "E" and state["blink"]:
                    ch = "B"
                cr.set_source_rgb(*palette[ch])
                cr.rectangle(x * PIXEL, y * PIXEL, PIXEL, PIXEL)
                cr.fill()

    art = Gtk.DrawingArea()
    art.set_size_request(len(ROBOT[0]) * PIXEL, len(ROBOT) * PIXEL)
    art.set_valign(Gtk.Align.CENTER)
    art.connect("draw", draw)

    def blink():
        state["blink"] = True
        art.queue_draw()
        GLib.timeout_add(BLINK_MS, unblink)
        return True

    def unblink():
        state["blink"] = False
        art.queue_draw()
        return False

    GLib.timeout_add(BLINK_EVERY_MS, blink)
    say = label(f"< Claude is {SAYINGS.get(category, category)}", "pet-say")
    detail = label(shorten(body), "pet-body")

    right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    right.pack_start(say, False, False, 0)
    right.pack_start(detail, False, False, 0)

    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    box.get_style_context().add_class("pet-box")
    box.pack_start(art, False, False, 0)
    box.pack_start(right, False, False, 0)

    win.add(box)
    win.connect("button-press-event", lambda *_: Gtk.main_quit())
    win.show_all()

    # Bottom-right of the primary monitor's work area, stacked above any
    # pets already on screen. Each popup re-reads the registry a few times a
    # second so the stack collapses when an older one closes.
    display = Gdk.Display.get_default()
    monitor = display.get_primary_monitor() or display.get_monitor(0)
    wa = monitor.get_workarea()
    _, nat = win.get_preferred_size()
    x = wa.x + wa.width - nat.width - MARGIN
    base_y = wa.y + wa.height - nat.height - MARGIN

    my_ts = time.time()
    me = REG_DIR / f"{my_ts:.6f}-{os.getpid()}"
    REG_DIR.mkdir(parents=True, exist_ok=True)
    me.write_text(str(nat.height))

    def place():
        below = sum(h + GAP for ts, pid, h, _ in live_entries()
                    if pid != os.getpid() and ts > my_ts)
        win.move(x, base_y - below)
        return True

    place()
    GLib.timeout_add(250, place)
    GLib.timeout_add(TIMEOUT_MS, Gtk.main_quit)
    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    try:
        Gtk.main()
    finally:
        me.unlink(missing_ok=True)


def fallback_notify(category, body):
    subprocess.Popen(
        ["dunstify", "-a", "claude-pet", "-r", "9001", f"[o_o] Claude is {SAYINGS.get(category, category)}", body[:200]],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "--show":
        show(sys.argv[2], sys.argv[3])
        return
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return
    hit = match(payload)
    if not hit:
        return
    category, body = hit
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        try:
            spawn_popup(category, body)
            return
        except OSError:
            pass
    fallback_notify(category, body)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # alert-only: never let the pet break a tool call
        pass
    sys.exit(0)
