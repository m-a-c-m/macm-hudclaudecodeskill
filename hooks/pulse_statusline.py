"""
macm-pulse · pulse_statusline.py  v1.0.0
──────────────────────────────────────────────────────────────────────
PURPOSE:    Render Claude Code status line. READ-ONLY operation.
READS:      stdin (JSON from Claude Code session data)
            ~/.claude/macm_pulse_config.json
            ~/.claude/macm_pulse_stats.json
WRITES:     nothing
NETWORK:    none  |  SUBPROCESS: none  |  eval/exec: none
Audit in ~2 min. See docs/SECURITY.md for full access list.
──────────────────────────────────────────────────────────────────────
"""
import sys
import io
import json
import copy
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 output on Windows (handles Unicode box chars and ANSI)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HOME        = Path.home()
CONFIG_PATH = HOME / ".claude" / "macm_pulse_config.json"
STATS_PATH  = HOME / ".claude" / "macm_pulse_stats.json"

# ANSI 256-color themes: (bright, dim, reset)
THEMES = {
    "cyan":   ("\033[38;5;51m",  "\033[38;5;38m",  "\033[0m"),
    "green":  ("\033[38;5;46m",  "\033[38;5;28m",  "\033[0m"),
    "purple": ("\033[38;5;141m", "\033[38;5;91m",  "\033[0m"),
    "orange": ("\033[38;5;208m", "\033[38;5;130m", "\033[0m"),
    "mono":   ("\033[38;5;255m", "\033[38;5;245m", "\033[0m"),
}

YELLOW = "\033[38;5;220m"
RED    = "\033[38;5;196m"
RESET  = "\033[0m"

DEFAULT_CONFIG = {
    "enabled": True,
    "theme": "cyan",
    "language": "en",
    "density": "compact",
    "currency": "USD",
    "notify_at_pct": 85,
    "show": {
        "model":          True,
        "context_bar":    True,
        "context_tokens": True,
        "cache":          True,
        "cost_session":   True,
        "cost_today":     False,
        "session_time":   True,
        "lines_changed":  False,
        "rate_limit_5h":  True,
        "rate_limit_7d":  True,
        "messages_today": True,
        "messages_week":  False,
        "last_compact":   True,
        "peak_hour":      False,
        "top_tool":       False,
        "streak":         False,
    },
}


def _load(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return copy.deepcopy(default)


def _bar(pct, width=14):
    filled = max(0, min(width, int(width * pct / 100)))
    return "█" * filled + "░" * (width - filled)


def _bar_color(pct, bright):
    if pct >= 90:
        return RED
    if pct >= 70:
        return YELLOW
    return bright


def _fmt_duration(ms):
    secs = int(ms / 1000)
    if secs < 60:
        return f"{secs}s"
    mins = secs // 60
    if mins < 60:
        return f"{mins}m"
    return f"{mins // 60}h {mins % 60}m"


def _fmt_reset(epoch):
    try:
        now    = datetime.now(timezone.utc)
        target = datetime.fromtimestamp(float(epoch), tz=timezone.utc)
        secs   = int((target - now).total_seconds())
        if secs <= 0:
            return None
        mins = secs // 60
        return f"{mins // 60}h {mins % 60}m" if mins >= 60 else f"{mins}m"
    except Exception:
        return None


def _compact_ago(ts):
    if not ts:
        return None
    try:
        t = datetime.fromisoformat(ts)
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        mins = int((datetime.now(timezone.utc) - t).total_seconds() / 60)
        if mins < 1:
            return "just now"
        return f"{mins}m ago" if mins < 60 else f"{mins // 60}h ago"
    except Exception:
        return None


def _fmt_tokens(n):
    return f"{n // 1000}k" if n >= 1000 else str(n)


def _today_key():
    return datetime.now().date().isoformat()


def _week_key():
    y, w, _ = datetime.now().date().isocalendar()
    return f"{y}-W{w:02d}"


def render(data, config, stats):
    show    = config.get("show", DEFAULT_CONFIG["show"])
    theme   = config.get("theme", "cyan")
    density = config.get("density", "compact")
    lang    = config.get("language", "en")
    cur_sym = "€" if config.get("currency") == "EUR" else "$"
    cur_mul = 0.92     if config.get("currency") == "EUR" else 1.0

    bright, dim, reset = THEMES.get(theme, THEMES["cyan"])
    sep = f"{dim} │ {reset}"

    # ── Data from Claude Code stdin (exact, no estimation) ──────────
    model_obj  = data.get("model") or {}
    model_name = model_obj.get("display_name") or model_obj.get("id") or "unknown"

    ctx        = data.get("context_window") or {}
    pct        = int(ctx.get("used_percentage") or 0)
    ctx_size   = int(ctx.get("context_window_size") or 200000)
    cur_usage  = ctx.get("current_usage") or {}
    inp_tok    = int(cur_usage.get("input_tokens") or 0)
    cache_r    = int(cur_usage.get("cache_read_input_tokens") or 0)
    cache_w    = int(cur_usage.get("cache_creation_input_tokens") or 0)

    cost_obj   = data.get("cost") or {}
    cost_sess  = float(cost_obj.get("total_cost_usd") or 0)
    dur_ms     = int(cost_obj.get("total_duration_ms") or 0)
    lines_add  = int(cost_obj.get("total_lines_added") or 0)
    lines_rem  = int(cost_obj.get("total_lines_removed") or 0)

    rl       = data.get("rate_limits") or {}
    rl_5h    = rl.get("five_hour") or {}
    rl_7d    = rl.get("seven_day") or {}
    pct_5h   = rl_5h.get("used_percentage")
    pct_7d   = rl_7d.get("used_percentage")
    rst_5h   = _fmt_reset(rl_5h.get("resets_at"))

    # ── Data from persistent stats (cross-session history) ──────────
    today_data   = (stats.get("daily")   or {}).get(_today_key()) or {}
    week_data    = (stats.get("weekly")  or {}).get(_week_key())  or {}
    compact_data = stats.get("compact")  or {}

    msgs_today   = today_data.get("messages", 0)
    msgs_week    = week_data.get("messages", 0)
    last_compact = _compact_ago(compact_data.get("last_time"))
    hourly       = today_data.get("hourly") or {}
    peak_hour    = (max(hourly, key=lambda h: hourly[h]) + ":00") if hourly else None
    tools_dict   = (stats.get("session") or {}).get("tools") or {}
    top_tool     = max(tools_dict, key=lambda t: tools_dict[t]) if tools_dict else None
    streak       = (stats.get("streak") or {}).get("consecutive_days", 0)

    # ── Labels (en/es) ──────────────────────────────────────────────
    lbl_today = "HOY"    if lang == "es" else "TODAY"
    lbl_week  = "SEMANA" if lang == "es" else "WEEK"
    lbl_sess  = "SESION" if lang == "es" else "SESSION"

    # ── Assemble parts ──────────────────────────────────────────────
    parts = []

    if show.get("model", True):
        parts.append(f"{bright}◈ {model_name}{reset}")

    if show.get("context_bar", True):
        bc  = _bar_color(pct, bright)
        bar = _bar(pct)
        tok = ""
        if show.get("context_tokens", True) and inp_tok > 0:
            tok = f"  {dim}{_fmt_tokens(inp_tok)}/{_fmt_tokens(ctx_size)}{reset}"
        parts.append(f"{bc}{bar}{reset} {bc}{pct}%{reset}{tok}")

    if show.get("cache", True):
        total_cache = cache_r + cache_w
        if total_cache > 0:
            parts.append(f"{dim}CACHE {_fmt_tokens(total_cache)}{reset}")

    if show.get("last_compact", True) and last_compact:
        parts.append(f"{dim}COMPACT {last_compact}{reset}")

    if show.get("rate_limit_5h", True) and pct_5h is not None:
        bc  = _bar_color(int(pct_5h), bright)
        rst = f" ({rst_5h})" if rst_5h else ""
        parts.append(f"{bc}5H {int(pct_5h)}%{reset}{dim}{rst}{reset}")

    if show.get("rate_limit_7d", True) and pct_7d is not None:
        bc = _bar_color(int(pct_7d), bright)
        parts.append(f"{bc}7D {int(pct_7d)}%{reset}")

    if show.get("messages_today", True):
        parts.append(f"{bright}{lbl_today} {msgs_today}{reset}")

    if show.get("messages_week", False):
        parts.append(f"{dim}{lbl_week} {msgs_week}{reset}")

    if show.get("session_time", True) and dur_ms > 0:
        parts.append(f"{dim}{lbl_sess} {_fmt_duration(dur_ms)}{reset}")

    if show.get("lines_changed", False) and (lines_add or lines_rem):
        parts.append(f"{dim}+{lines_add} -{lines_rem}{reset}")

    if show.get("cost_session", True) and cost_sess > 0:
        amt = cost_sess * cur_mul
        parts.append(f"{dim}~{cur_sym}{amt:.2f}{reset}")

    if show.get("peak_hour", False) and peak_hour:
        parts.append(f"{dim}PEAK {peak_hour}{reset}")

    if show.get("top_tool", False) and top_tool:
        parts.append(f"{dim}TOP {top_tool}{reset}")

    if show.get("streak", False) and streak > 1:
        parts.append(f"{dim}STREAK {streak}d{reset}")

    if not parts:
        return ""

    if density == "full" and len(parts) > 6:
        mid   = len(parts) // 2
        line1 = sep.join(parts[:mid])
        line2 = sep.join(parts[mid:])
        return f" {line1} \n {line2} "

    return " " + sep.join(parts) + " "


def main():
    try:
        raw  = sys.stdin.buffer.read()
        data = json.loads(raw.decode("utf-8-sig"))
    except Exception:
        data = {}

    config = _load(CONFIG_PATH, DEFAULT_CONFIG)

    if not config.get("enabled", True):
        print("", end="")
        return

    stats  = _load(STATS_PATH, {})
    output = render(data, config, stats)
    print(output, end="")


if __name__ == "__main__":
    main()
