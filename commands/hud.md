Toggle macm-hud on or off. Run immediately with Bash, no explanation:

```
python -c "import json,pathlib; p=pathlib.Path.home()/'.claude'/'macm_pulse_config.json'; c=json.loads(p.read_text()); c['enabled']=not c.get('enabled',True); p.write_text(json.dumps(c,indent=2)); print('macm-hud: ON' if c['enabled'] else 'macm-hud: OFF')"
```
