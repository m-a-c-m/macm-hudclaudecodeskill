"""
macm-pulse · pulse_collector.py  v1.0.0
──────────────────────────────────────────────────────────────────────
PURPOSE:    Process Claude Code hook events, persist stats locally.
READS:      stdin (hook JSON from Claude Code)
            ~/.claude/macm_pulse_stats.json
WRITES:     ~/.claude/macm_pulse_stats.json  (only this file)
NETWORK:    none  |  SUBPROCESS: none  |  eval/exec: none
Audit in ~2 min. See docs/SECURITY.md.
──────────────────────────────────────────────────────────────────────
"""
import sys
import json
import copy
from datetime import datetime, date
from pathlib import Path

HOME       = Path.home()
STATS_PATH = HOME / ".claude" / "macm_pulse_stats.json"

DEFAULT_STATS = {
    "session": {"id": None, "start": None, "model": None, "tools": {}},
    "compact": {"last_time": None, "tokens_at_compact": 0, "count_today": 0},
    "daily":   {},
    "weekly":  {},
    "streak":  {"last_active_date": None, "consecutive_days": 0},
}


def _load(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return copy.deepcopy(default)


def _save(path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass


def _today():
    return date.today().isoformat()


def _week():
    y, w, _ = date.today().isocalendar()
    return f"{y}-W{w:02d}"


def _ensure_day(stats, key):
    if key not in stats["daily"]:
        stats["daily"][key] = {"messages": 0, "compacts": 0, "hourly": {}}


def _ensure_week(stats, key):
    if key not in stats["weekly"]:
        stats["weekly"][key] = {"messages": 0}


def _update_streak(stats):
    today = _today()
    streak = stats.get("streak") or {}
    last   = streak.get("last_active_date")
    days   = streak.get("consecutive_days", 0)
    if last == today:
        return
    if last:
        try:
            delta = (date.today() - date.fromisoformat(last)).days
            days  = days + 1 if delta == 1 else 1
        except Exception:
            days = 1
    else:
        days = 1
    stats["streak"] = {"last_active_date": today, "consecutive_days": days}


def on_session_start(p, stats):
    sid = p.get("session_id")
    stats["session"].update({
        "id":    sid,
        "start": datetime.now().isoformat(),
        "model": p.get("model") or stats["session"].get("model"),
        "tools": {},
    })
    if p.get("source") == "compact" and not stats["compact"].get("last_time"):
        stats["compact"]["last_time"] = datetime.now().isoformat()


def on_prompt(p, stats):
    sid              = p.get("session_id")
    today, week, hr  = _today(), _week(), str(datetime.now().hour)

    if stats["session"].get("id") != sid:
        stats["session"].update({"id": sid, "start": datetime.now().isoformat(), "tools": {}})

    _ensure_day(stats, today)
    _ensure_week(stats, week)
    stats["daily"][today]["messages"] += 1
    stats["weekly"][week]["messages"]  += 1
    h = stats["daily"][today]["hourly"]
    h[hr] = h.get(hr, 0) + 1
    _update_streak(stats)


def on_pre_compact(p, stats):
    stats["compact"]["tokens_at_compact"] = (stats.get("session") or {}).get("input_tokens", 0)


def on_post_compact(p, stats):
    today = _today()
    stats["compact"]["last_time"] = datetime.now().isoformat()
    _ensure_day(stats, today)
    stats["daily"][today]["compacts"] += 1


def on_tool(p, stats):
    name  = p.get("tool_name", "unknown")
    tools = stats["session"].get("tools") or {}
    tools[name] = tools.get(name, 0) + 1
    stats["session"]["tools"] = tools


def on_stop(p, stats):
    model = p.get("model") or stats["session"].get("model")
    if model:
        stats["session"]["model"] = model


HANDLERS = {
    "SessionStart":     on_session_start,
    "UserPromptSubmit": on_prompt,
    "PreCompact":       on_pre_compact,
    "PostCompact":      on_post_compact,
    "PreToolUse":       on_tool,
    "Stop":             on_stop,
    "StopFailure":      on_stop,
}


def main():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
        p   = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.stdout.write('{"continue":true}\n')
        return

    event   = p.get("hook_event_name", "")
    handler = HANDLERS.get(event)

    if handler:
        stats = _load(STATS_PATH, DEFAULT_STATS)
        handler(p, stats)
        _save(STATS_PATH, stats)

    sys.stdout.write('{"continue":true}\n')


if __name__ == "__main__":
    main()
