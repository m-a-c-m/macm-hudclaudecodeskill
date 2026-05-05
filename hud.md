Controls macm-hud, the real-time status line monitor for Claude Code.

Read the argument in $ARGUMENTS and act accordingly. Always execute the action directly with Bash — never show code for the user to copy. Use Python's `pathlib.Path.home()` for all paths so it works on Windows, macOS, and Linux.

---

## /hud (no argument or "toggle")

Toggle `enabled` on/off in the config file. Run and report the result:

```python
import json, pathlib
p = pathlib.Path.home() / ".claude" / "macm_pulse_config.json"
c = json.loads(p.read_text())
c["enabled"] = not c.get("enabled", True)
p.write_text(json.dumps(c, indent=2))
print("macm-hud:", "ON" if c["enabled"] else "OFF")
```

## /hud on

Set `enabled: true`:

```python
import json, pathlib
p = pathlib.Path.home() / ".claude" / "macm_pulse_config.json"
c = json.loads(p.read_text())
c["enabled"] = True
p.write_text(json.dumps(c, indent=2))
print("macm-hud: ON")
```

## /hud off

Set `enabled: false`:

```python
import json, pathlib
p = pathlib.Path.home() / ".claude" / "macm_pulse_config.json"
c = json.loads(p.read_text())
c["enabled"] = False
p.write_text(json.dumps(c, indent=2))
print("macm-hud: OFF")
```

## /hud config

Open the configuration UI in the browser:

```python
import importlib.util, pathlib
ui = pathlib.Path.home() / ".claude" / "hooks" / "pulse_config_ui.py"
spec = importlib.util.spec_from_file_location("pulse_config_ui", ui)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.run(open_browser=True)
```

## /hud stats

Read `macm_pulse_stats.json` using pathlib and display a formatted summary with:
- Messages today and this week
- Last compaction time and how long ago
- Most used tools this session
- Top 3 busiest hours today
- Active streak in consecutive days

Load the file with:
```python
import json, pathlib
p = pathlib.Path.home() / ".claude" / "macm_pulse_stats.json"
stats = json.loads(p.read_text()) if p.exists() else {}
```

## /hud reset

Ask the user to confirm. Then:

```python
import pathlib
p = pathlib.Path.home() / ".claude" / "macm_pulse_stats.json"
p.unlink(missing_ok=True)
print("Stats reset.")
```

## /hud uninstall

Ask the user to confirm. Then ask for the repo path and run `install.py --uninstall` from it.

## If macm-hud is not installed

Tell the user to run:
```
git clone https://github.com/m-a-c-m/macm-hudclaudecodeskill
cd macm-hudclaudecodeskill
python install.py
```
