# Security — macm-pulse

## What macm-pulse reads

| File | Who reads it | Why |
|---|---|---|
| Claude Code hook stdin | `pulse_collector.py` | Hook event data (session ID, model, usage) |
| Claude Code status line stdin | `pulse_statusline.py` | Live session data (context %, cost, rate limits) |
| `~/.claude/macm_pulse_config.json` | both scripts | User preferences (theme, enabled, show flags) |
| `~/.claude/macm_pulse_stats.json` | both scripts | Persistent counters (messages, compactions) |
| `~/.claude/settings.json` | `install.py` only | To add statusLine and hooks entries |

## What macm-pulse writes

| File | Who writes it | Why |
|---|---|---|
| `~/.claude/macm_pulse_stats.json` | `pulse_collector.py` | Persist per-day/week counters |
| `~/.claude/macm_pulse_config.json` | `install.py`, config UI | Save user preferences |
| `~/.claude/settings.json` | `install.py` only | Register statusLine and hooks |
| `~/.claude/settings.json.bak.<ts>` | `install.py` only | Backup before any edit |
| `~/.claude/hooks/pulse_*.py` | `install.py` only | Copy runtime scripts |

## What macm-pulse never does

- Makes network requests of any kind
- Sends telemetry or analytics
- Reads files outside `~/.claude/` (except its own source files during install)
- Writes files outside `~/.claude/`
- Spawns subprocesses
- Uses `eval`, `exec`, or `__import__` tricks
- Reads environment variables (other than what Python sets automatically)
- Accesses your code, git history, or project files

## Audit instructions

All runtime code lives in two files under `~/.claude/hooks/`:

```
pulse_collector.py   ~150 lines   — hook event processor
pulse_statusline.py  ~200 lines   — status line renderer
```

Verify no network calls:
```
grep -E "urllib|requests|socket|http|ftp|smtp" ~/.claude/hooks/pulse_*.py
```
Expected: no output.

Verify no subprocess:
```
grep -E "subprocess|os\.system|os\.popen|Popen" ~/.claude/hooks/pulse_*.py
```
Expected: no output.

Verify no eval/exec:
```
grep -E "\beval\b|\bexec\b|__import__" ~/.claude/hooks/pulse_*.py
```
Expected: no output.

## Uninstall completely

```
python /path/to/macm-pulse/install.py --uninstall
```

Then optionally:
```
rm ~/.claude/macm_pulse_config.json
rm ~/.claude/macm_pulse_stats.json
```
