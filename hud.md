macm-hud controller. Run the command for $ARGUMENTS immediately using Bash, no explanation needed.

- (none) or toggle: `python -c "import json,pathlib; p=pathlib.Path.home()/'.claude'/'macm_pulse_config.json'; c=json.loads(p.read_text()); c['enabled']=not c.get('enabled',True); p.write_text(json.dumps(c,indent=2)); print('ON' if c['enabled'] else 'OFF')"`
- on: same but force `c['enabled']=True`
- off: same but force `c['enabled']=False`
- config: `python -c "import importlib.util,pathlib; p=pathlib.Path.home()/'.claude'/'hooks'/'pulse_config_ui.py'; s=importlib.util.spec_from_file_location('u',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.run()"`
- stats: `python -c "import pathlib; print(pathlib.Path.home()/'.claude'/'macm_pulse_stats.json')"` then Read that file and summarise: messages today/week, streak, last compact, top tools.
- reset: confirm then `python -c "import pathlib; pathlib.Path.home().joinpath('.claude','macm_pulse_stats.json').unlink(missing_ok=True); print('reset')"`
