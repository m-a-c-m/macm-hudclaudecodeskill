Controls macm-hud, the real-time status line monitor for Claude Code.

Read the argument in $ARGUMENTS and act accordingly. Always execute actions directly — never show code for the user to copy.

---

## /hud (no argument or "toggle")

Toggle `enabled` on/off. Run with Bash and report result:

```
python -c "import json,pathlib; p=pathlib.Path.home()/'.claude'/'macm_pulse_config.json'; c=json.loads(p.read_text()); c['enabled']=not c.get('enabled',True); p.write_text(json.dumps(c,indent=2)); print('macm-hud: ON' if c['enabled'] else 'macm-hud: OFF')"
```

## /hud on

```
python -c "import json,pathlib; p=pathlib.Path.home()/'.claude'/'macm_pulse_config.json'; c=json.loads(p.read_text()); c['enabled']=True; p.write_text(json.dumps(c,indent=2)); print('macm-hud: ON')"
```

## /hud off

```
python -c "import json,pathlib; p=pathlib.Path.home()/'.claude'/'macm_pulse_config.json'; c=json.loads(p.read_text()); c['enabled']=False; p.write_text(json.dumps(c,indent=2)); print('macm-hud: OFF')"
```

## /hud config

Run with Bash — opens a local server in the browser and waits for the user to save:

```
python -c "import importlib.util,pathlib; p=pathlib.Path.home()/'.claude'/'hooks'/'pulse_config_ui.py'; s=importlib.util.spec_from_file_location('ui',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.run()"
```

Tell the user: "Config UI open in your browser — save there to apply changes, the server closes automatically."

## /hud stats

First get the stats file path:
```
python -c "import pathlib; print(pathlib.Path.home()/'.claude'/'macm_pulse_stats.json')"
```

Then read that file and display a clean summary including:
- Messages today and this week
- Streak (consecutive active days)
- Last compaction time
- Top tools used this session with counts
- Top 3 busiest hours today

## /hud reset

Ask the user to confirm first. If yes:

```
python -c "import pathlib; p=pathlib.Path.home()/'.claude'/'macm_pulse_stats.json'; p.unlink(missing_ok=True); print('Stats reset.')"
```

## /hud uninstall

Ask the user to confirm. Then ask for the repo path and run:
```
python <repo_path>/install.py --uninstall
```

## If macm-hud is not installed

Tell the user to run:
```
git clone https://github.com/m-a-c-m/macm-hudclaudecodeskill
cd macm-hudclaudecodeskill
python install.py
```
