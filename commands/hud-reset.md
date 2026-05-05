Reset macm-hud stats. Ask the user to confirm first. If confirmed, run:

```
python -c "import pathlib; p=pathlib.Path.home()/'.claude'/'macm_pulse_stats.json'; p.unlink(missing_ok=True); print('Stats reset.')"
```
