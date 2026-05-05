Show macm-hud usage stats. First get the file path:

```
python -c "import pathlib; print(pathlib.Path.home()/'.claude'/'macm_pulse_stats.json')"
```

Then read that file and display a clean summary: messages today and this week, streak in days, last compaction time, top tools used this session with counts, top 3 busiest hours today.
