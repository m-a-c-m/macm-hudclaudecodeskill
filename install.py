"""
macm-pulse · install.py  v1.0.0
──────────────────────────────────────────────────────────────────────
PURPOSE:    One-time installer. Copies hooks, patches settings.json,
            opens the web config UI.
READS:      ~/.claude/settings.json
WRITES:     ~/.claude/hooks/pulse_collector.py
            ~/.claude/hooks/pulse_statusline.py
            ~/.claude/hooks/pulse_config_ui.py
            ~/.claude/settings.json  (after timestamped backup)
            ~/.claude/settings.json.bak.<timestamp>
NETWORK:    localhost only (config UI on 127.0.0.1)
SUBPROCESS: none  |  eval/exec: none
──────────────────────────────────────────────────────────────────────
"""
import sys
import json
import shutil
import platform
from pathlib import Path
from datetime import datetime

HOME         = Path.home()
CLAUDE_DIR   = HOME / ".claude"
HOOKS_DIR    = CLAUDE_DIR / "hooks"
COMMANDS_DIR = CLAUDE_DIR / "commands"
SETTINGS     = CLAUDE_DIR / "settings.json"
CONFIG_DST   = CLAUDE_DIR / "macm_pulse_config.json"

REPO       = Path(__file__).parent
SRC_FILES  = {
    "pulse_collector.py":  REPO / "hooks" / "pulse_collector.py",
    "pulse_statusline.py": REPO / "hooks" / "pulse_statusline.py",
    "pulse_config_ui.py":  REPO / "pulse_config_ui.py",
}

HOOK_EVENTS = [
    "SessionStart", "UserPromptSubmit",
    "PreCompact", "PostCompact",
    "PreToolUse", "Stop",
]

C  = "\033[38;5;51m"   # cyan bright
D  = "\033[38;5;38m"   # cyan dim
Y  = "\033[38;5;220m"  # yellow
G  = "\033[38;5;46m"   # green
R  = "\033[38;5;196m"  # red
RS = "\033[0m"


def pr(msg=""):
    print(msg)

def ok(msg):
    print(f"  {G}✓{RS}  {msg}")

def info(msg):
    print(f"  {D}·{RS}  {msg}")

def warn(msg):
    print(f"  {Y}!{RS}  {msg}")

def err(msg):
    print(f"  {R}✗{RS}  {msg}")

def header():
    pr(f"\n{C}{'─'*54}{RS}")
    pr(f"{C}  ◈  macm-pulse  ·  Claude Code Status Line{RS}")
    pr(f"{C}{'─'*54}{RS}\n")

def _py():
    return "python" if platform.system() == "Windows" else "python3"

def _norm(path):
    return str(path).replace("\\", "/")

def _hook_cmd():
    return f"{_py()} {_norm(HOOKS_DIR / 'pulse_collector.py')}"

def _statusline_cmd():
    return f"{_py()} {_norm(HOOKS_DIR / 'pulse_statusline.py')}"

def _load_settings():
    try:
        if SETTINGS.exists():
            return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _save_settings(data):
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _backup():
    if SETTINGS.exists():
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = CLAUDE_DIR / f"settings.json.bak.{ts}"
        shutil.copy2(SETTINGS, bak)
        info(f"Backup → {bak.name}")

def _patch_settings():
    s = _load_settings()

    s["statusLine"] = {
        "type":    "command",
        "command": _statusline_cmd(),
        "padding": 1,
    }

    if "hooks" not in s:
        s["hooks"] = {}

    hook_entry = {"type": "command", "command": _hook_cmd(), "timeout": 10}
    matcher_entry = {"matcher": "", "hooks": [hook_entry]}

    for event in HOOK_EVENTS:
        if event not in s["hooks"]:
            s["hooks"][event] = []
        s["hooks"][event] = [
            h for h in s["hooks"][event]
            if "pulse_collector" not in str(h.get("command", ""))
            and "pulse_collector" not in str(h.get("hooks", ""))
        ]
        s["hooks"][event].append(matcher_entry)

    _save_settings(s)

def _copy_files():
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    for name, src in SRC_FILES.items():
        if not src.exists():
            err(f"Source not found: {src}")
            sys.exit(1)
        dst = HOOKS_DIR / name
        shutil.copy2(src, dst)
        ok(f"Copied  {name}")

    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    cmd_src = REPO / "hud.md"
    if cmd_src.exists():
        shutil.copy2(cmd_src, COMMANDS_DIR / "hud.md")
        ok(f"Copied  hud.md  → ~/.claude/commands/hud.md")

def _is_installed():
    return (HOOKS_DIR / "pulse_collector.py").exists() and \
           (HOOKS_DIR / "pulse_statusline.py").exists()

def _open_config_ui():
    pr()
    pr(f"{C}  Opening configuration UI in your browser...{RS}")
    try:
        ui_path = HOOKS_DIR / "pulse_config_ui.py"
        # Import and run directly (no subprocess)
        import importlib.util
        spec = importlib.util.spec_from_file_location("pulse_config_ui", ui_path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.run(open_browser=True)
    except KeyboardInterrupt:
        pr(f"\n  {Y}Config skipped. Run  python install.py --config  to configure later.{RS}")
    except Exception as e:
        warn(f"Could not open UI: {e}")
        warn(f"Configure manually: edit  {CONFIG_DST}")

def _uninstall():
    pr(f"\n{Y}Uninstalling macm-hud...{RS}")
    removed = 0
    for name in SRC_FILES:
        f = HOOKS_DIR / name
        if f.exists():
            f.unlink()
            ok(f"Removed {name}")
            removed += 1

    cmd_file = COMMANDS_DIR / "hud.md"
    if cmd_file.exists():
        cmd_file.unlink()
        ok("Removed hud.md from ~/.claude/commands/")
        removed += 1

    s = _load_settings()
    changed = False

    if "statusLine" in s and "pulse_statusline" in str(s["statusLine"].get("command", "")):
        del s["statusLine"]
        changed = True

    if "hooks" in s:
        for event in HOOK_EVENTS:
            if event in s["hooks"]:
                before = len(s["hooks"][event])
                s["hooks"][event] = [
                    h for h in s["hooks"][event]
                    if "pulse_collector" not in str(h.get("command", ""))
                    and "pulse_collector" not in str(h.get("hooks", ""))
                ]
                if len(s["hooks"][event]) < before:
                    changed = True
                if not s["hooks"][event]:
                    del s["hooks"][event]

    if changed:
        _backup()
        _save_settings(s)
        ok("settings.json cleaned")

    if removed == 0 and not changed:
        info("Nothing to remove — macm-pulse was not installed")
    else:
        pr(f"\n{C}  macm-pulse removed.{RS}")
        pr(f"  {D}Config and stats preserved:{RS}")
        pr(f"  {D}{CONFIG_DST}{RS}")
        pr(f"  {D}{CLAUDE_DIR / 'macm_pulse_stats.json'}{RS}")
        pr(f"  {D}Delete them manually if no longer needed.{RS}\n")

def _install():
    pr(f"{C}  Installing...{RS}\n")

    _copy_files()
    pr()

    pr(f"{C}  Patching settings.json...{RS}")
    _backup()
    _patch_settings()
    ok("statusLine configured")
    ok("Hooks registered (6 events)")

    pr()
    _open_config_ui()

    pr(f"""
{C}{'─'*54}{RS}
{C}  Done.{RS}

  The status line activates after your next message
  in Claude Code.

  Commands (via skill):
    {D}/hud{RS}            — toggle on / off
    {D}/hud config{RS}     — open config UI
    {D}/hud stats{RS}      — show usage summary

  Quick smoke test:
    {D}{_py()} {_norm(HOOKS_DIR/'pulse_statusline.py')} <<< '{{}}'
{C}{'─'*54}{RS}
""")

def main():
    header()

    if "--uninstall" in sys.argv:
        ans = input(f"  {Y}Remove macm-pulse?{RS} [y/N]: ").strip().lower()
        if ans in ("y", "yes"):
            _uninstall()
        return

    if "--config" in sys.argv:
        _open_config_ui()
        return

    if _is_installed():
        pr(f"{Y}  macm-pulse is already installed.{RS}\n")
        pr(f"  [1]  Reinstall / update hooks")
        pr(f"  [2]  Open config UI")
        pr(f"  [3]  Uninstall")
        pr(f"  [4]  Exit\n")
        choice = input(f"  Choice [4]: ").strip()
        if choice == "1":
            _install()
        elif choice == "2":
            _open_config_ui()
        elif choice == "3":
            ans = input(f"  {Y}Remove macm-pulse?{RS} [y/N]: ").strip().lower()
            if ans in ("y", "yes"):
                _uninstall()
        return

    ans = input(f"  Install macm-pulse? [Y/n]: ").strip().lower()
    if ans in ("", "y", "yes"):
        _install()

if __name__ == "__main__":
    main()
