"""macm-hud CLI — zero tokens, runs direct from terminal"""
import sys
import json
import pathlib
import importlib.util

HOME   = pathlib.Path.home()
CONFIG = HOME / ".claude" / "macm_pulse_config.json"
STATS  = HOME / ".claude" / "macm_pulse_stats.json"
UI     = HOME / ".claude" / "hooks" / "pulse_config_ui.py"


def _cfg():
    return json.loads(CONFIG.read_text()) if CONFIG.exists() else {}

def _save(c):
    CONFIG.write_text(json.dumps(c, indent=2))

def cmd_toggle():
    c = _cfg(); c["enabled"] = not c.get("enabled", True); _save(c)
    print("macm-hud:", "ON" if c["enabled"] else "OFF")

def cmd_on():
    c = _cfg(); c["enabled"] = True; _save(c); print("macm-hud: ON")

def cmd_off():
    c = _cfg(); c["enabled"] = False; _save(c); print("macm-hud: OFF")

def cmd_config():
    spec = importlib.util.spec_from_file_location("ui", UI)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run()

def cmd_stats():
    if not STATS.exists():
        print("No stats yet."); return
    from datetime import date
    s     = json.loads(STATS.read_text())
    today = date.today().isoformat()
    d     = s.get("daily", {}).get(today, {})
    streak = s.get("streak", {}).get("consecutive_days", 0)
    compact = s.get("compact", {}).get("last_time", "never")
    tools   = s.get("session", {}).get("tools", {})
    hourly  = d.get("hourly", {})
    print(f"Today:    {d.get('messages', 0)} messages")
    print(f"Streak:   {streak} consecutive days")
    print(f"Compact:  {compact}")
    if tools:
        top = sorted(tools.items(), key=lambda x: x[1], reverse=True)[:3]
        print("Tools:   ", "  ".join(f"{t}({n})" for t, n in top))
    if hourly:
        top_h = sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:3]
        print("Peak hrs:", "  ".join(f"{h}:00={n}" for h, n in top_h))

def cmd_reset():
    ans = input("Delete all stats? [y/N]: ").strip().lower()
    if ans in ("y", "yes"):
        STATS.unlink(missing_ok=True); print("Stats reset.")

CMDS = {
    "toggle": cmd_toggle, "on": cmd_on, "off": cmd_off,
    "config": cmd_config, "stats": cmd_stats, "reset": cmd_reset,
}

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "toggle"
    fn  = CMDS.get(arg)
    if fn:
        fn()
    else:
        print(f"Usage: hud.py [{'|'.join(CMDS)}]")
