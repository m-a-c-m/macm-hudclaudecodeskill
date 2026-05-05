Disable macm-hud. Run immediately with Bash:

```
python -c "import json,pathlib; p=pathlib.Path.home()/'.claude'/'macm_pulse_config.json'; c=json.loads(p.read_text()); c['enabled']=False; p.write_text(json.dumps(c,indent=2)); print('macm-hud: OFF')"
```
