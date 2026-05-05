# macm-hud

**Real-time status line for Claude Code.**  
Context %, rate limits, cost, compaction — exact data from the Claude Code API, displayed in the bar below your input.

```
 ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ COMPACT 23m ago │ 5H 28% (2h 14m) │ 7D 41% │ TODAY 14 │ SESSION 47m │ ~$0.18
```

> No estimations. No network calls. No tokens consumed. 100% local.

---

## Why

Claude Code no longer shows a visual context indicator. Without it you lose track of:

- How close you are to the next auto-compact
- Whether you are approaching your 5-hour rate limit
- What the session has cost so far
- Which model is actually active

macm-hud adds a persistent status bar below your input — updated after every response, sourced directly from the Claude Code API.

---

## What it shows

| Metric | Source | Exact? |
|---|---|---|
| Model name | Claude Code API | Yes |
| Context bar + % | Claude Code API (`used_percentage`) | Yes |
| Token count (`146k/200k`) | Claude Code API | Yes |
| Cache tokens | Claude Code API | Yes |
| 5-hour rate limit % + time to reset | Claude Code API | Yes |
| 7-day rate limit % | Claude Code API | Yes |
| Session cost | Claude Code API | Yes |
| Session duration | Claude Code API | Yes |
| Last compaction + time elapsed | Local hook (`PostCompact`) | Yes |
| Messages today / this week | Local hook (`UserPromptSubmit`) | Yes |
| Lines of code changed | Claude Code API | Yes |
| Peak usage hour | Local hook (hourly histogram) | Yes |
| Most used tool | Local hook (`PreToolUse`) | Yes |
| Active day streak | Local hook (daily tracking) | Yes |

Every metric is individually toggleable — show only what you care about.

---

## Requirements

- Claude Code CLI
- Python 3.8+
- Windows 10+, macOS 12+, or Linux

---

## Install

```bash
git clone https://github.com/m-a-c-m/macm-hudclaudecodeskill
cd macm-hudclaudecodeskill
python install.py
```

The installer:
1. Copies the hook scripts to `~/.claude/hooks/`
2. Patches `~/.claude/settings.json` — creates a timestamped backup first
3. Opens the **configuration UI** in your browser

The status line activates after your next Claude Code message.

---

## Themes

Five ANSI 256-color themes. The context bar changes color automatically by fill level:

| Level | Color |
|---|---|
| Below 70% | Theme color |
| 70 – 89% | Yellow |
| 90%+ | Red |

```
cyan    ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
green   ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
purple  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
orange  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
mono    ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
```

---

## Language

**English (default):**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT 23m ago │ 5H 28% │ TODAY 14 │ SESSION 47m │ ~$0.18
```

**Spanish (`language: "es"`):**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT hace 23m │ 5H 28% │ HOY 14 │ SESION 47m │ ~€0.16
```

---

## Configuration UI

Runs as a local server on `127.0.0.1` — no data leaves your machine.

**Open at any time:**

```bash
python ~/.claude/hooks/pulse_config_ui.py
```

**Or via the skill:**

```
/hud config
```

### What you can configure

| Setting | Options |
|---|---|
| Theme | Cyan · Green · Purple · Orange · Mono |
| Layout | Compact (1 line) · Full (2 lines) |
| Language | English · Spanish |
| Currency | USD · EUR |
| Alert threshold | Context % that triggers red bar (default: 85%) |
| Metrics | Toggle each one individually with live preview |

---

## Skill commands

Copy `SKILL.md` to `~/.claude/skills/macm-hud/SKILL.md` and restart Claude Code to enable skill commands.

| Command | Action |
|---|---|
| `/hud` | Toggle status line on/off |
| `/hud on` | Force enable |
| `/hud off` | Force disable (hooks keep collecting data) |
| `/hud config` | Open configuration UI in browser |
| `/hud stats` | Print usage summary to chat |
| `/hud reset` | Clear stats (with confirmation) |
| `/hud uninstall` | Remove macm-hud (with confirmation) |

---

## How it integrates with Claude Code

macm-hud uses two native Claude Code extension points: `statusLine` and `hooks`.

After install, your `~/.claude/settings.json` gains these entries:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python ~/.claude/hooks/pulse_statusline.py",
    "padding": 1
  },
  "hooks": {
    "UserPromptSubmit": [{ "matcher": "", "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pulse_collector.py" }] }],
    "PostCompact":      [{ "matcher": "", "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pulse_collector.py" }] }],
    "PreCompact":       [{ "matcher": "", "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pulse_collector.py" }] }],
    "SessionStart":     [{ "matcher": "", "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pulse_collector.py" }] }],
    "PreToolUse":       [{ "matcher": "", "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pulse_collector.py" }] }],
    "Stop":             [{ "matcher": "", "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pulse_collector.py" }] }]
  }
}
```

**Files created in `~/.claude/`:**

```
~/.claude/
├── hooks/
│   ├── pulse_collector.py      hook event processor  — writes cross-session stats
│   ├── pulse_statusline.py     status line renderer  — reads Claude Code stdin
│   └── pulse_config_ui.py      web configuration UI  — local only, 127.0.0.1
├── macm_pulse_config.json      your preferences
└── macm_pulse_stats.json       usage counters (auto-created on first run)
```

`settings.json` is backed up with a timestamp before any change. A clean uninstall removes every entry macm-hud added.

---

## How it works

```
Claude Code
   │
   ├── statusLine  →  pulse_statusline.py
   │     reads:   stdin  (live session JSON from Claude Code)
   │              macm_pulse_config.json
   │              macm_pulse_stats.json
   │     writes:  nothing
   │     prints:  one ANSI-colored line
   │
   └── hooks  →  pulse_collector.py
         reads:   stdin  (hook event JSON)
         writes:  macm_pulse_stats.json
         prints:  {"continue": true}
```

The status line script runs after each Claude response and does not consume API tokens — this is documented in the Claude Code official docs.

---

## Security

- Zero network requests of any kind
- Zero telemetry or analytics
- Reads only its own config/stats files and Claude Code's stdin
- Writes only `~/.claude/macm_pulse_stats.json`
- No `subprocess`, no `eval`, no `exec`

Full audit guide: [docs/SECURITY.md](docs/SECURITY.md)

Quick audit — these should return no output:

```bash
grep -E "urllib|requests|socket|http\." ~/.claude/hooks/pulse_*.py
grep -E "subprocess|os\.system|os\.popen" ~/.claude/hooks/pulse_*.py
grep -E "\beval\b|\bexec\b|__import__" ~/.claude/hooks/pulse_*.py
```

---

## Uninstall

```bash
python install.py --uninstall
```

Removes hook scripts and cleans `settings.json`. Config and stats at `~/.claude/` are preserved — delete manually if needed:

```bash
rm ~/.claude/macm_pulse_config.json
rm ~/.claude/macm_pulse_stats.json
```

---

## Troubleshooting

**Status line not appearing**
- Send one message in Claude Code — it activates after the first response.
- Smoke test: `echo '{}' | python ~/.claude/hooks/pulse_statusline.py`
- Check that `disableAllHooks` is not `true` in your Claude Code settings.

**All values show 0 or blank**
- Fields from Claude Code are `null` before the first API call. Send one message.

**Config UI does not open**
- Run manually: `python ~/.claude/hooks/pulse_config_ui.py`
- Check Python is in PATH: `python --version`

**Reinstall after pulling an update**

```bash
cd macm-hudclaudecodeskill && git pull
python install.py  # choose Reinstall
```

---

## Documentation

- English: this file
- Español: [README.es.md](README.es.md)
- Configuration reference: [docs/CONFIG.md](docs/CONFIG.md)
- Security audit guide: [docs/SECURITY.md](docs/SECURITY.md)

---

## License

MIT — [Miguel Angel Colorado Marin](https://miguelacm.es)
