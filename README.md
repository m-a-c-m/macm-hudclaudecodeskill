# macm-pulse

**Real-time Claude Code status line monitor.**  
Context %, rate limits, cost, compaction — all exact data from the Claude Code API, displayed in the bar below your input.

> **Documentacion en Espanol:** [README.es.md](README.es.md)

```
 ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ COMPACT 23m ago │ 5H 28% (2h 14m) │ 7D 41% │ TODAY 14 │ ~$0.18
```

> No estimations. No network calls. No tokens consumed. 100% local.

---

## What it shows

| Metric | Source | Exact? |
|---|---|---|
| Model name | Claude Code API | Yes |
| Context bar + % | Claude Code API (`used_percentage`) | Yes |
| Token count (`109k/200k`) | Claude Code API | Yes |
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

Every metric is a toggle — show only what you care about.

---

## Requirements

- Claude Code CLI
- Python 3.8+
- Windows 10+, macOS 12+, or Linux

---

## Install

```bash
git clone https://github.com/m-a-c-m/macm-pulse
cd macm-pulse
python install.py
```

The installer:
1. Copies the hook scripts to `~/.claude/hooks/`
2. Patches `~/.claude/settings.json` (backs it up first)
3. Opens the **configuration UI** in your browser

After saving in the UI, the status line is active on your next Claude Code message.

---

## Configuration UI

The UI runs as a local web server on `127.0.0.1` — no data ever leaves your machine.

**To open it at any time:**

```bash
python ~/.claude/hooks/pulse_config_ui.py
```

**Or via the skill:**

```
/pulse config
```

### What you can configure

- **Theme** — Cyan / Green / Purple / Orange / Mono (with live preview)
- **Layout** — Compact (1 line) or Full (2 lines)
- **Language** — English or Spanish labels (`TODAY` vs `HOY`, `SESSION` vs `SESION`)
- **Currency** — USD or EUR
- **Alert threshold** — % at which the context bar turns red (default: 85%)
- **Metrics** — toggle each one individually with live preview

### Language options

**English (default):**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT 23m ago │ 5H 28% │ TODAY 14 │ SESSION 47m │ ~$0.18
```

**Spanish:**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT hace 23m │ 5H 28% │ HOY 14 │ SESION 47m │ ~€0.16
```

Set it in the UI under **Labels: English / Spanish**.

---

## Skill commands

Install the skill by placing `SKILL.md` in `~/.claude/skills/macm-pulse/SKILL.md`,  
then restart Claude Code.

| Command | Action |
|---|---|
| `/pulse` | Toggle status line on/off |
| `/pulse on` | Force enable |
| `/pulse off` | Force disable (hooks keep collecting data) |
| `/pulse config` | Open configuration UI in browser |
| `/pulse stats` | Print usage summary to chat |
| `/pulse reset` | Clear stats (with confirmation) |
| `/pulse uninstall` | Remove macm-pulse (with confirmation) |

---

## Themes

| Name | Preview color |
|---|---|
| `cyan` (default) | Bright blue-teal |
| `green` | Terminal green |
| `purple` | Violet |
| `orange` | Warm amber |
| `mono` | Neutral grey |

Context bar color changes automatically by fill level:

- `< 70%` → theme color
- `70–89%` → yellow
- `≥ 90%` → red

---

## Uninstall

```bash
python install.py --uninstall
```

This removes the hook scripts and cleans `settings.json`. Config and stats files at `~/.claude/` are kept — delete them manually if needed:

```bash
rm ~/.claude/macm_pulse_config.json
rm ~/.claude/macm_pulse_stats.json
```

---

## How it works

```
Claude Code
   │
   ├── statusLine script  →  pulse_statusline.py
   │     reads: stdin (live session JSON from Claude Code)
   │             ~/.claude/macm_pulse_config.json
   │             ~/.claude/macm_pulse_stats.json
   │     writes: nothing
   │     prints: one formatted line
   │
   └── hooks (6 events)  →  pulse_collector.py
         reads:  stdin (hook event JSON)
         writes: ~/.claude/macm_pulse_stats.json
         output: {"continue": true}
```

The status line script runs after each Claude response — it does not consume API tokens (documented in the Claude Code official docs).

---

## Files created on install

```
~/.claude/
├── hooks/
│   ├── pulse_collector.py      hook event processor
│   ├── pulse_statusline.py     status line renderer
│   └── pulse_config_ui.py      configuration web UI
├── macm_pulse_config.json      your preferences
└── macm_pulse_stats.json       usage counters (auto-created)
```

`~/.claude/settings.json` is edited to add `statusLine` and `hooks` entries. A timestamped backup is created before any change.

---

## Security

- Zero network calls
- Zero telemetry
- Reads only its own config/stats files and Claude Code's stdin
- Writes only `~/.claude/macm_pulse_stats.json`
- No `subprocess`, no `eval`, no `exec`
- Audit in ~2 minutes: see [docs/SECURITY.md](docs/SECURITY.md)

---

## Troubleshooting

**Status line not appearing**

- Send a message in Claude Code — it activates after the first interaction.
- Run the smoke test: `echo '{}' | python ~/.claude/hooks/pulse_statusline.py`
- Check Claude Code is not running with `disableAllHooks: true` in settings.

**All values show 0 or blank**

- Fields from Claude Code (%, cost, rate limits) are `null` before the first API call. Send one message.

**Config UI does not open**

- Run manually: `python ~/.claude/hooks/pulse_config_ui.py`
- Check Python is in your PATH: `python --version`

**Reinstall / update after pulling new version**

```bash
cd macm-pulse && git pull
python install.py  # choose option 1 (Reinstall)
```

---

## License

MIT — [Miguel Angel Colorado Marin](https://miguelacm.es)
