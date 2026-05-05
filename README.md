<div align="center">

# macm-hud

### Real-time status line for Claude Code

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-6366f1?style=for-the-badge)](README.md)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-f97316?style=for-the-badge)](https://claude.ai/code)

<br>

```
 ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ COMPACT 23m ago │ 5H 28% (2h 14m) │ 7D 41% │ TODAY 14 │ SESSION 47m │ ~$0.18
```

**No estimations &nbsp;·&nbsp; No network calls &nbsp;·&nbsp; No tokens consumed &nbsp;·&nbsp; 100% local**

<br>

[Install](#install) &nbsp;·&nbsp; [Control](#controlling-macm-hud) &nbsp;·&nbsp; [Configure](#configuration-ui) &nbsp;·&nbsp; [Themes](#themes) &nbsp;·&nbsp; [Security](#security) &nbsp;·&nbsp; [Español](README.es.md)

</div>

---

## Why

Claude Code removed the visual context indicator. Without it you lose track of:

- How close you are to the next auto-compact
- Whether you are approaching your 5-hour rate limit
- What the session has cost so far
- Which model is actually active

macm-hud puts all of that in the bar below your input — updated after every response, sourced directly from the Claude Code API.

---

## What it shows

| Metric | Source | Exact? |
|---|---|:---:|
| Model name | Claude Code API | ✅ |
| Context bar + % | Claude Code API (`used_percentage`) | ✅ |
| Token count (`146k/200k`) | Claude Code API | ✅ |
| Cache tokens | Claude Code API | ✅ |
| 5-hour rate limit % + time to reset | Claude Code API | ✅ |
| 7-day rate limit % | Claude Code API | ✅ |
| Session cost | Claude Code API | ✅ |
| Session duration | Claude Code API | ✅ |
| Last compaction + time elapsed | Local hook (`PostCompact`) | ✅ |
| Messages today / this week | Local hook (`UserPromptSubmit`) | ✅ |
| Lines of code changed | Claude Code API | ✅ |
| Peak usage hour | Local hook (hourly histogram) | ✅ |
| Most used tool | Local hook (`PreToolUse`) | ✅ |
| Active day streak | Local hook (daily tracking) | ✅ |

Every metric is individually toggleable — show only what you care about.

---

## Install

```bash
git clone https://github.com/m-a-c-m/macm-hudclaudecodeskill
cd macm-hudclaudecodeskill
python install.py
```

The installer copies the hooks to `~/.claude/hooks/`, patches `~/.claude/settings.json` (with a timestamped backup), and opens the configuration UI in your browser. The status line is active after your next Claude Code message.

> **Windows:** run `python install.py` from a terminal window, not through Claude Code tools.

---

## Controlling macm-hud

There are three ways to control macm-hud. Choose whichever fits your workflow.

---

### Option 1 — Terminal (zero tokens, fastest)

Run `hud.py` directly from any terminal. No Claude involved, no tokens consumed.

**Windows — PowerShell:**
```powershell
python $env:USERPROFILE\.claude\hooks\hud.py
python $env:USERPROFILE\.claude\hooks\hud.py on
python $env:USERPROFILE\.claude\hooks\hud.py off
python $env:USERPROFILE\.claude\hooks\hud.py config
python $env:USERPROFILE\.claude\hooks\hud.py stats
python $env:USERPROFILE\.claude\hooks\hud.py reset
```

**Windows — CMD:**
```
python %USERPROFILE%\.claude\hooks\hud.py config
python %USERPROFILE%\.claude\hooks\hud.py stats
```

**macOS / Linux:**
```bash
python3 ~/.claude/hooks/hud.py
python3 ~/.claude/hooks/hud.py on
python3 ~/.claude/hooks/hud.py off
python3 ~/.claude/hooks/hud.py config
python3 ~/.claude/hooks/hud.py stats
python3 ~/.claude/hooks/hud.py reset
```

---

### Option 2 — `/hud` slash commands (uses tokens)

The `/hud` command is available inside Claude Code once the installer copies `hud.md` to `~/.claude/commands/`. Claude reads the file and executes the action — convenient but it uses a small amount of context.

| Command | Action |
|---|---|
| `/hud` | Toggle status line on / off |
| `/hud on` | Force enable |
| `/hud off` | Force disable |
| `/hud config` | Open configuration UI in browser |
| `/hud stats` | Print usage summary to chat |
| `/hud reset` | Clear stats (with confirmation) |

> Tip: for frequent toggles, prefer Option 1 or 2 to keep your context clean.

---

## Configuration UI

A local web interface on `127.0.0.1` — no data ever leaves your machine.

**Open it:**

```powershell
# Windows (PowerShell)
python $env:USERPROFILE\.claude\hooks\hud.py config
```
```bash
# macOS / Linux
python3 ~/.claude/hooks/hud.py config
```

| Setting | Options |
|---|---|
| **Theme** | Cyan · Green · Purple · Orange · Mono |
| **Layout** | Compact (1 line) · Full (2 lines) |
| **Language** | English · Spanish |
| **Currency** | USD · EUR |
| **Alert threshold** | Context % that turns the bar red (default: 85%) |
| **Metrics** | Toggle each one with live preview |

Save in the browser and the server closes automatically.

---

## Themes

Five ANSI 256-color themes. The context bar changes color automatically:

| Fill | Color |
|---|---|
| `< 70%` | Theme color |
| `70 – 89%` | Yellow |
| `≥ 90%` | Red |

```
  cyan  │  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
 green  │  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
purple  │  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
orange  │  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
  mono  │  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ TODAY 14 │ ~$0.18
```

---

## Language

**English (default)**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT 23m ago │ 5H 28% │ TODAY 14 │ SESSION 47m │ ~$0.18
```

**Spanish (`"language": "es"`)**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT hace 23m │ 5H 28% │ HOY 14 │ SESION 47m │ ~€0.16
```

---

## How it integrates with Claude Code

macm-hud uses two native Claude Code extension points: `statusLine` and `hooks`.

After install, `~/.claude/settings.json` gains these entries:

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
│   ├── pulse_collector.py      hook processor   — writes cross-session stats
│   ├── pulse_statusline.py     status renderer  — reads Claude Code stdin
│   ├── pulse_config_ui.py      config web UI    — local only, 127.0.0.1
│   └── hud.py                  CLI controller   — toggle/config/stats from terminal
├── commands/
│   └── hud.md                  /hud slash command definition
├── macm_pulse_config.json      your preferences
└── macm_pulse_stats.json       usage counters   — auto-created on first run
```

`settings.json` is backed up with a timestamp before any change.

---

## How it works

```
Claude Code
   │
   ├── statusLine  →  pulse_statusline.py
   │     reads:   stdin  (live session JSON — context %, cost, rate limits)
   │              macm_pulse_config.json  ·  macm_pulse_stats.json
   │     writes:  nothing
   │     prints:  one ANSI-colored line
   │
   └── hooks  →  pulse_collector.py
         reads:   stdin  (hook event JSON)
         writes:  macm_pulse_stats.json
         prints:  {"continue": true}
```

The status line script runs after each response and does **not** consume API tokens.

---

## Security

```
Zero network requests  ·  Zero telemetry  ·  No subprocess  ·  No eval/exec
```

macm-hud reads only its own config/stats files and Claude Code's stdin. It writes only `~/.claude/macm_pulse_stats.json`. Nothing else is touched.

Full audit guide: [docs/SECURITY.md](docs/SECURITY.md)

Quick audit — all three should return **no output**:

```bash
grep -E "urllib|requests|socket|http\." ~/.claude/hooks/pulse_*.py
grep -E "subprocess|os\.system|os\.popen" ~/.claude/hooks/pulse_*.py
grep -E "\beval\b|\bexec\b|__import__" ~/.claude/hooks/pulse_*.py
```

---

## Uninstall

**One command — run from the cloned repo folder:**

```bash
python install.py --uninstall
```

Or via slash command inside Claude Code: `/hud-uninstall`

That's it. It removes the hook scripts, the CLI, all slash command files, and cleans `settings.json`. A backup of `settings.json` is created before any change.

Config and stats files are kept — delete them manually only if you want a full clean:

```bash
# Windows
python -c "import pathlib; [p.unlink(missing_ok=True) for p in [pathlib.Path.home()/'.claude'/'macm_pulse_config.json', pathlib.Path.home()/'.claude'/'macm_pulse_stats.json']]"

# macOS / Linux
rm ~/.claude/macm_pulse_config.json ~/.claude/macm_pulse_stats.json
```

---

<details>
<summary><strong>Troubleshooting</strong></summary>

<br>

**Status line not appearing**
- Send one message — it activates after the first response.
- Smoke test: `python %USERPROFILE%\.claude\hooks\pulse_statusline.py` (Windows) or `echo '{}' | python3 ~/.claude/hooks/pulse_statusline.py` (macOS/Linux)
- Check `disableAllHooks` is not `true` in your Claude Code settings.

**All values show 0 or blank**
- Fields from Claude Code are `null` before the first API call. Send one message.

**Config UI does not open**
- Run: `python %USERPROFILE%\.claude\hooks\hud.py config` (Windows) or `python3 ~/.claude/hooks/hud.py config`
- Check Python is in PATH: `python --version`

**Reinstall after update**
```bash
cd macm-hudclaudecodeskill && git pull
python install.py   # choose Reinstall
```

</details>

---

<div align="center">

**Documentation:** [English](README.md) · [Español](README.es.md) · [Config reference](docs/CONFIG.md) · [Security](docs/SECURITY.md)

MIT — [Miguel Angel Colorado Marin](https://miguelacm.es)

</div>
