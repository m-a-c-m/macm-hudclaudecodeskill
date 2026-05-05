---
name: hud
description: Toggle, configure, and inspect macm-hud — the Claude Code real-time status line monitor
version: 1.0.0
author: miguelacm.es
---

# macm-hud skill

This skill controls the macm-hud status line monitor for Claude Code.

## Rules

- Always run commands directly with Bash — never generate code blocks for the user to copy.
- Never modify ~/.claude/settings.json manually; use install.py for that.
- The config UI opens in the browser automatically when `--config` is passed to install.py.
- If macm-hud is not installed, tell the user to run `python install.py` from the repo.

## Commands

When invoked as `/hud` with no arguments: toggle `enabled` on/off in the config file.

When invoked as `/hud on`: set `enabled: true`.

When invoked as `/hud off`: set `enabled: false`.

When invoked as `/hud config`: open the web configuration UI.

When invoked as `/hud stats`: read and display a formatted summary from the stats file.

When invoked as `/hud reset`: confirm with the user, then delete the stats file.

When invoked as `/hud uninstall`: confirm with the user, then run the uninstaller.

## Toggle logic

To toggle hud on/off, run this Python one-liner:

```
python -c "
import json, pathlib
p = pathlib.Path.home() / '.claude' / 'macm_pulse_config.json'
c = json.loads(p.read_text())
c['enabled'] = not c.get('enabled', True)
p.write_text(json.dumps(c, indent=2))
print('macm-hud:', 'ON' if c['enabled'] else 'OFF')
"
```

## Config UI

To open the config UI:

```
python {HOME}/.claude/hooks/pulse_config_ui.py
```

Replace `{HOME}` with the actual home directory path. On Windows use `python`, on macOS/Linux use `python3`.

## Stats summary

To show stats, read `~/.claude/macm_pulse_stats.json` and display:
- Messages today and this week
- Last compaction timestamp and count
- Most used tools
- Active streak in days
- Per-hour message distribution (show the top 3 hours)

## Reset stats

Confirm with the user before deleting. Then:

```
python -c "
import pathlib
p = pathlib.Path.home() / '.claude' / 'macm_pulse_stats.json'
if p.exists():
    p.unlink()
    print('Stats reset.')
else:
    print('No stats file found.')
"
```

## Uninstall

Run: `python {REPO_PATH}/install.py --uninstall`

Ask the user for the repo path if unknown.
