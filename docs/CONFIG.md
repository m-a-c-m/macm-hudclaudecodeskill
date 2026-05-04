# Configuration reference — macm-pulse

Config file: `~/.claude/macm_pulse_config.json`

Open the UI to edit it: `python ~/.claude/hooks/pulse_config_ui.py`

---

## Top-level fields

| Field | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | `true` | Master on/off switch. Toggle with `/pulse` |
| `theme` | string | `"cyan"` | Color theme: `cyan` `green` `purple` `orange` `mono` |
| `language` | string | `"en"` | Label language: `"en"` (English) or `"es"` (Spanish) |
| `density` | string | `"compact"` | Layout: `"compact"` (1 line) or `"full"` (2 lines) |
| `currency` | string | `"USD"` | Cost display: `"USD"` or `"EUR"` |
| `notify_at_pct` | int | `85` | Context % at which the bar turns red |

## show flags

Each metric can be independently toggled. All are booleans.

| Key | Default | What it shows |
|---|---|---|
| `model` | `true` | Active model name (e.g. `Sonnet 4.6`) |
| `context_bar` | `true` | Visual progress bar + percentage |
| `context_tokens` | `true` | Token count next to bar (`109k/200k`) |
| `cache` | `true` | Cache tokens read + created |
| `rate_limit_5h` | `true` | 5-hour rolling rate limit % |
| `rate_limit_7d` | `true` | 7-day rate limit % |
| `last_compact` | `true` | Time since last auto-compaction |
| `cost_session` | `true` | Estimated session cost |
| `session_time` | `true` | Session duration |
| `messages_today` | `true` | Prompts sent today (all sessions) |
| `messages_week` | `false` | Prompts sent this week |
| `lines_changed` | `false` | Lines of code added/removed |
| `peak_hour` | `false` | Hour of day with most usage |
| `top_tool` | `false` | Most-called tool this session |
| `streak` | `false` | Consecutive active days |
| `cost_today` | `false` | Accumulated cost today (all sessions) |

## Manual edit example

```json
{
  "enabled": true,
  "theme": "purple",
  "language": "es",
  "density": "compact",
  "currency": "EUR",
  "notify_at_pct": 80,
  "show": {
    "model": true,
    "context_bar": true,
    "context_tokens": false,
    "cache": false,
    "rate_limit_5h": true,
    "rate_limit_7d": false,
    "last_compact": true,
    "cost_session": true,
    "session_time": false,
    "messages_today": true,
    "messages_week": false,
    "lines_changed": false,
    "peak_hour": false,
    "top_tool": false,
    "streak": false,
    "cost_today": false
  }
}
```
