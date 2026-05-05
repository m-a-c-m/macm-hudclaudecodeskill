Open the macm-hud configuration UI in the browser. Run immediately with Bash:

```
python -c "import importlib.util,pathlib; p=pathlib.Path.home()/'.claude'/'hooks'/'pulse_config_ui.py'; s=importlib.util.spec_from_file_location('u',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.run()"
```

Tell the user: configuration UI is open in the browser — save there to apply, server closes automatically.
