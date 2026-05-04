"""
macm-pulse · pulse_config_ui.py  v1.0.0
──────────────────────────────────────────────────────────────────────
PURPOSE:    Local web UI for configuring macm-pulse. No external deps.
READS:      ~/.claude/macm_pulse_config.json
WRITES:     ~/.claude/macm_pulse_config.json  (on Save)
NETWORK:    localhost only — binds 127.0.0.1, never external
SUBPROCESS: none  |  eval/exec: none
──────────────────────────────────────────────────────────────────────
"""
import json
import copy
import socket
import threading
import webbrowser
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOME        = Path.home()
CONFIG_PATH = HOME / ".claude" / "macm_pulse_config.json"

DEFAULT_CONFIG = {
    "enabled": True, "theme": "cyan", "language": "en",
    "density": "compact", "currency": "USD", "notify_at_pct": 85,
    "show": {
        "model": True, "context_bar": True, "context_tokens": True,
        "cache": True, "cost_session": True, "cost_today": False,
        "session_time": True, "lines_changed": False,
        "rate_limit_5h": True, "rate_limit_7d": True,
        "messages_today": True, "messages_week": False,
        "last_compact": True, "peak_hour": False,
        "top_tool": False, "streak": False,
    },
}

METRIC_LABELS = [
    ("model",          "Model name",               "Always useful to know which model you're on"),
    ("context_bar",    "Context bar + %",           "Visual bar showing how full your context is"),
    ("context_tokens", "Token count (e.g. 109k/200k)", "Exact numbers next to the bar"),
    ("cache",          "Cache tokens",              "Tokens read/created from prompt cache"),
    ("rate_limit_5h",  "5-hour rate limit",         "% of your 5h rolling usage limit consumed"),
    ("rate_limit_7d",  "7-day rate limit",          "% of your weekly usage limit consumed"),
    ("last_compact",   "Last compaction",           "How long ago context was auto-compacted"),
    ("cost_session",   "Session cost",              "Estimated USD/EUR cost for this session"),
    ("session_time",   "Session duration",          "How long the current session has been active"),
    ("messages_today", "Messages today",            "Total prompts sent today across all sessions"),
    ("messages_week",  "Messages this week",        "Total prompts sent this week"),
    ("lines_changed",  "Lines of code changed",     "Lines added and removed in this session"),
    ("peak_hour",      "Peak hour",                 "The hour of day you use Claude the most"),
    ("top_tool",       "Most used tool",            "Tool called most in the current session"),
    ("streak",         "Active streak",             "Consecutive days using Claude Code"),
    ("cost_today",     "Cost today (all sessions)", "Accumulated cost across all sessions today"),
]

_shutdown_flag = threading.Event()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>macm-pulse · Configuration</title>
<style>
  :root {
    --bg:        #080d16;
    --bg2:       #0d1526;
    --bg3:       #111d33;
    --border:    #1a3050;
    --cyan:      #00d4ff;
    --cyan2:     #0099cc;
    --cyan3:     #005577;
    --cyan-dim:  #004466;
    --text:      #cce8f5;
    --text-dim:  #5a8099;
    --text-muted:#2a4a66;
    --green:     #00ff88;
    --yellow:    #ffd700;
    --orange:    #ff8c00;
    --purple:    #bf7fff;
    --red:       #ff4444;
    --mono:      #aaaaaa;
    --radius:    6px;
    --font:      'Consolas', 'Courier New', monospace;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 14px;
    line-height: 1.6;
    min-height: 100vh;
  }
  /* Header */
  header {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 20px 32px;
    display: flex;
    align-items: center;
    gap: 16px;
  }
  header h1 { color: var(--cyan); font-size: 18px; letter-spacing: 0.1em; }
  header span { color: var(--text-dim); font-size: 12px; }
  .version-badge {
    margin-left: auto;
    background: var(--cyan3);
    color: var(--cyan);
    border: 1px solid var(--cyan2);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 11px;
    letter-spacing: 0.05em;
  }
  /* Layout */
  main { max-width: 960px; margin: 0 auto; padding: 32px 24px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  @media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
  /* Preview */
  .preview-box {
    grid-column: 1 / -1;
    background: #000811;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }
  .preview-label {
    background: var(--bg3);
    border-bottom: 1px solid var(--border);
    padding: 8px 16px;
    font-size: 11px;
    color: var(--text-dim);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .preview-terminal {
    padding: 8px 16px 10px;
    display: flex;
    align-items: center;
    min-height: 44px;
  }
  #preview-line {
    font-family: var(--font);
    font-size: 13px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    letter-spacing: 0.02em;
  }
  .preview-cursor {
    display: inline-block;
    width: 8px;
    height: 14px;
    background: var(--cyan);
    margin-left: 2px;
    animation: blink 1.2s step-end infinite;
    vertical-align: middle;
    opacity: 0.7;
  }
  @keyframes blink { 0%,100%{opacity:0.7} 50%{opacity:0} }
  /* Card */
  .card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
  }
  .card h2 {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }
  /* Theme Swatches */
  .theme-grid { display: flex; gap: 10px; flex-wrap: wrap; }
  .theme-swatch {
    cursor: pointer;
    border: 2px solid transparent;
    border-radius: var(--radius);
    padding: 10px 14px;
    background: var(--bg3);
    display: flex;
    align-items: center;
    gap: 8px;
    transition: border-color .15s, background .15s;
    font-size: 13px;
    color: var(--text);
  }
  .theme-swatch:hover { background: #162040; }
  .theme-swatch.active { border-color: var(--cyan); background: #0d1e3a; }
  .theme-dot { width: 12px; height: 12px; border-radius: 50%; }
  .dot-cyan   { background: var(--cyan); box-shadow: 0 0 6px var(--cyan); }
  .dot-green  { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .dot-purple { background: var(--purple); box-shadow: 0 0 6px var(--purple); }
  .dot-orange { background: var(--orange); box-shadow: 0 0 6px var(--orange); }
  .dot-mono   { background: var(--mono); }
  /* Radio / Select rows */
  .option-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 0;
  }
  .radio-btn {
    cursor: pointer;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 6px 14px;
    font-family: var(--font);
    font-size: 12px;
    color: var(--text-dim);
    transition: all .15s;
  }
  .radio-btn:hover { border-color: var(--cyan2); color: var(--text); }
  .radio-btn.active {
    background: var(--cyan3);
    border-color: var(--cyan);
    color: var(--cyan);
  }
  /* Toggle switches */
  .metrics-list { display: flex; flex-direction: column; gap: 2px; }
  .metric-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 10px;
    border-radius: var(--radius);
    transition: background .1s;
    cursor: pointer;
  }
  .metric-row:hover { background: var(--bg3); }
  .metric-info { flex: 1; }
  .metric-name { font-size: 13px; color: var(--text); }
  .metric-desc { font-size: 11px; color: var(--text-dim); margin-top: 1px; }
  /* Toggle */
  .toggle { position: relative; width: 36px; height: 20px; flex-shrink: 0; }
  .toggle input { opacity: 0; width: 0; height: 0; position: absolute; }
  .toggle-track {
    position: absolute; inset: 0;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 20px;
    transition: background .2s, border-color .2s;
    cursor: pointer;
  }
  .toggle-thumb {
    position: absolute;
    top: 3px; left: 3px;
    width: 12px; height: 12px;
    border-radius: 50%;
    background: var(--text-dim);
    transition: transform .2s, background .2s;
  }
  .toggle input:checked + .toggle-track { background: var(--cyan3); border-color: var(--cyan); }
  .toggle input:checked + .toggle-track .toggle-thumb {
    transform: translateX(16px);
    background: var(--cyan);
    box-shadow: 0 0 6px var(--cyan);
  }
  /* Number input */
  .field-row { display: flex; align-items: center; gap: 12px; margin-top: 4px; }
  .field-row label { font-size: 12px; color: var(--text-dim); flex: 1; }
  .num-input {
    width: 80px;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 5px 10px;
    font-family: var(--font);
    font-size: 13px;
    color: var(--cyan);
    text-align: center;
    outline: none;
    transition: border-color .15s;
  }
  .num-input:focus { border-color: var(--cyan); }
  /* Save button */
  .save-row {
    grid-column: 1 / -1;
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    align-items: center;
  }
  .save-status { font-size: 12px; color: var(--text-dim); }
  .btn {
    background: var(--cyan3);
    border: 1px solid var(--cyan);
    border-radius: var(--radius);
    color: var(--cyan);
    font-family: var(--font);
    font-size: 13px;
    padding: 10px 28px;
    cursor: pointer;
    letter-spacing: 0.06em;
    transition: background .15s, box-shadow .15s;
  }
  .btn:hover { background: #005f8a; box-shadow: 0 0 12px rgba(0,212,255,.2); }
  .btn:active { transform: scale(0.98); }
  .btn-secondary {
    background: transparent;
    border-color: var(--border);
    color: var(--text-dim);
  }
  .btn-secondary:hover { border-color: var(--cyan2); color: var(--text); }
  /* Saved flash */
  .saved-flash {
    color: var(--green);
    font-size: 12px;
    opacity: 0;
    transition: opacity .3s;
  }
  .saved-flash.show { opacity: 1; }
  /* Divider */
  .section-gap { margin-top: 16px; }
</style>
</head>
<body>
<header>
  <span style="color:var(--cyan);font-size:20px">◈</span>
  <h1>macm-pulse</h1>
  <span>Claude Code Status Line</span>
  <span class="version-badge">v1.0.0</span>
</header>

<main>
  <div class="grid">

    <!-- LIVE PREVIEW -->
    <div class="preview-box">
      <div class="preview-label">Live preview</div>
      <div class="preview-terminal">
        <span id="preview-line"></span>
        <span class="preview-cursor"></span>
      </div>
    </div>

    <!-- THEME -->
    <div class="card">
      <h2>Theme</h2>
      <div class="theme-grid">
        <div class="theme-swatch" data-theme="cyan" onclick="setTheme('cyan')">
          <span class="theme-dot dot-cyan"></span> Cyan
        </div>
        <div class="theme-swatch" data-theme="green" onclick="setTheme('green')">
          <span class="theme-dot dot-green"></span> Green
        </div>
        <div class="theme-swatch" data-theme="purple" onclick="setTheme('purple')">
          <span class="theme-dot dot-purple"></span> Purple
        </div>
        <div class="theme-swatch" data-theme="orange" onclick="setTheme('orange')">
          <span class="theme-dot dot-orange"></span> Orange
        </div>
        <div class="theme-swatch" data-theme="mono" onclick="setTheme('mono')">
          <span class="theme-dot dot-mono"></span> Mono
        </div>
      </div>
    </div>

    <!-- LAYOUT & LANGUAGE -->
    <div class="card">
      <h2>Layout &amp; Language</h2>

      <p style="font-size:11px;color:var(--text-dim);margin-bottom:8px">Density</p>
      <div class="option-row">
        <button class="radio-btn" data-group="density" data-val="compact" onclick="setOpt('density','compact',this)">Compact (1 line)</button>
        <button class="radio-btn" data-group="density" data-val="full"    onclick="setOpt('density','full',this)">Full (2 lines)</button>
      </div>

      <p style="font-size:11px;color:var(--text-dim);margin-top:14px;margin-bottom:8px">Labels</p>
      <div class="option-row">
        <button class="radio-btn" data-group="language" data-val="en" onclick="setOpt('language','en',this)">English</button>
        <button class="radio-btn" data-group="language" data-val="es" onclick="setOpt('language','es',this)">Spanish</button>
      </div>

      <p style="font-size:11px;color:var(--text-dim);margin-top:14px;margin-bottom:8px">Currency</p>
      <div class="option-row">
        <button class="radio-btn" data-group="currency" data-val="USD" onclick="setOpt('currency','USD',this)">$ USD</button>
        <button class="radio-btn" data-group="currency" data-val="EUR" onclick="setOpt('currency','EUR',this)">€ EUR</button>
      </div>

      <div class="field-row section-gap">
        <label>Alert at context % (bar turns red near this)</label>
        <input class="num-input" type="number" id="notify_at_pct" min="50" max="99"
               oninput="cfg.notify_at_pct=parseInt(this.value)||85; updatePreview()">
      </div>
    </div>

    <!-- METRICS -->
    <div class="card" style="grid-column:1/-1">
      <h2>Metrics — toggle what appears in the status line</h2>
      <div class="metrics-list" id="metrics-list"></div>
    </div>

    <!-- SAVE -->
    <div class="save-row">
      <span class="saved-flash" id="saved-flash">Saved</span>
      <button class="btn btn-secondary" onclick="resetDefaults()">Reset defaults</button>
      <button class="btn" onclick="saveConfig()">Save &amp; close</button>
    </div>

  </div>
</main>

<script>
// ── Config state ─────────────────────────────────────────────────────
let cfg = __CONFIG__;

// ── Theme colors for preview (matches Python) ────────────────────────
const THEME_COLORS = {
  cyan:   { bright: '#00d4ff', dim: '#0099bb' },
  green:  { bright: '#00ff88', dim: '#00aa55' },
  purple: { bright: '#bf7fff', dim: '#8844cc' },
  orange: { bright: '#ff8c00', dim: '#cc5500' },
  mono:   { bright: '#eeeeee', dim: '#888888' },
};
const YELLOW = '#ffd700';
const RED    = '#ff4444';

function themeColor(theme, variant) {
  return (THEME_COLORS[theme] || THEME_COLORS.cyan)[variant];
}

function barColor(pct, theme) {
  if (pct >= 90) return RED;
  if (pct >= 70) return YELLOW;
  return themeColor(theme, 'bright');
}

// ── Build HTML preview ───────────────────────────────────────────────
function span(text, color, dim) {
  const c = dim ? themeColor(cfg.theme, 'dim') : color;
  return `<span style="color:${c}">${text}</span>`;
}

function makeBar(pct, width=14) {
  const f = Math.min(width, Math.floor(width * pct / 100));
  return '█'.repeat(f) + '░'.repeat(width - f);
}

function fmtTokens(n) { return n >= 1000 ? Math.floor(n/1000)+'k' : String(n); }

// Mock data for preview
const MOCK = {
  model: 'Sonnet 4.6',
  pct: 73, inp_tok: 146000, ctx_size: 200000,
  cache: 39000, compact_ago: '23m ago',
  pct_5h: 28, rst_5h: '2h 14m', pct_7d: 41,
  msgs_today: 14, msgs_week: 89,
  dur: '47m', cost: 0.18, lines_add: 42, lines_rem: 11,
  streak: 5, top_tool: 'Read', peak_hour: '15:00',
};

function updatePreview() {
  const show = cfg.show;
  const th   = cfg.theme;
  const br   = themeColor(th, 'bright');
  const di   = themeColor(th, 'dim');
  const sep  = `<span style="color:${di}"> │ </span>`;
  const cur  = cfg.currency === 'EUR' ? '€' : '$';
  const lbl  = cfg.language === 'es';
  const parts = [];

  if (show.model)
    parts.push(`<span style="color:${br}">◈ ${MOCK.model}</span>`);

  if (show.context_bar) {
    const bc  = barColor(MOCK.pct, th);
    const bar = makeBar(MOCK.pct);
    let tok = '';
    if (show.context_tokens)
      tok = ` <span style="color:${di}">${fmtTokens(MOCK.inp_tok)}/${fmtTokens(MOCK.ctx_size)}</span>`;
    parts.push(`<span style="color:${bc}">${bar} ${MOCK.pct}%</span>${tok}`);
  }

  if (show.cache && MOCK.cache > 0)
    parts.push(`<span style="color:${di}">CACHE ${fmtTokens(MOCK.cache)}</span>`);

  if (show.last_compact)
    parts.push(`<span style="color:${di}">COMPACT ${MOCK.compact_ago}</span>`);

  if (show.rate_limit_5h) {
    const bc = barColor(MOCK.pct_5h, th);
    parts.push(`<span style="color:${bc}">5H ${MOCK.pct_5h}%</span><span style="color:${di}"> (${MOCK.rst_5h})</span>`);
  }
  if (show.rate_limit_7d) {
    const bc = barColor(MOCK.pct_7d, th);
    parts.push(`<span style="color:${bc}">7D ${MOCK.pct_7d}%</span>`);
  }

  if (show.messages_today)
    parts.push(`<span style="color:${br}">${lbl?'HOY':'TODAY'} ${MOCK.msgs_today}</span>`);
  if (show.messages_week)
    parts.push(`<span style="color:${di}">${lbl?'SEMANA':'WEEK'} ${MOCK.msgs_week}</span>`);
  if (show.session_time)
    parts.push(`<span style="color:${di}">${lbl?'SESION':'SESSION'} ${MOCK.dur}</span>`);
  if (show.lines_changed)
    parts.push(`<span style="color:${di}">+${MOCK.lines_add} -${MOCK.lines_rem}</span>`);
  if (show.cost_session)
    parts.push(`<span style="color:${di}">~${cur}${MOCK.cost.toFixed(2)}</span>`);
  if (show.peak_hour)
    parts.push(`<span style="color:${di}">PEAK ${MOCK.peak_hour}</span>`);
  if (show.top_tool)
    parts.push(`<span style="color:${di}">TOP ${MOCK.top_tool}</span>`);
  if (show.streak && MOCK.streak > 1)
    parts.push(`<span style="color:${di}">STREAK ${MOCK.streak}d</span>`);

  document.getElementById('preview-line').innerHTML =
    parts.length ? ' ' + parts.join(sep) + ' ' : '<span style="color:var(--text-muted)">nothing to show — enable at least one metric</span>';
}

// ── Theme ─────────────────────────────────────────────────────────────
function setTheme(t) {
  cfg.theme = t;
  document.querySelectorAll('.theme-swatch').forEach(el =>
    el.classList.toggle('active', el.dataset.theme === t)
  );
  updatePreview();
}

// ── Generic option (density / language / currency) ───────────────────
function setOpt(key, val, el) {
  cfg[key] = val;
  document.querySelectorAll(`.radio-btn[data-group="${key}"]`).forEach(b =>
    b.classList.toggle('active', b.dataset.val === val)
  );
  updatePreview();
}

// ── Metrics list ─────────────────────────────────────────────────────
const METRIC_DEFS = __METRICS__;

function buildMetrics() {
  const list = document.getElementById('metrics-list');
  list.innerHTML = '';
  METRIC_DEFS.forEach(([key, label, desc]) => {
    const id  = 'tog_' + key;
    const row = document.createElement('div');
    row.className = 'metric-row';
    row.onclick   = () => {
      const inp = document.getElementById(id);
      inp.checked = !inp.checked;
      cfg.show[key] = inp.checked;
      updatePreview();
    };
    row.innerHTML = `
      <div class="metric-info">
        <div class="metric-name">${label}</div>
        <div class="metric-desc">${desc}</div>
      </div>
      <label class="toggle" onclick="event.stopPropagation()">
        <input type="checkbox" id="${id}" ${cfg.show[key] ? 'checked' : ''}
               onchange="cfg.show['${key}']=this.checked; updatePreview()">
        <span class="toggle-track"><span class="toggle-thumb"></span></span>
      </label>`;
    list.appendChild(row);
  });
}

// ── Init UI from config ───────────────────────────────────────────────
function initUI() {
  setTheme(cfg.theme);
  ['density','language','currency'].forEach(k => {
    const btn = document.querySelector(`.radio-btn[data-group="${k}"][data-val="${cfg[k]}"]`);
    if (btn) btn.classList.add('active');
  });
  const notifyInput = document.getElementById('notify_at_pct');
  notifyInput.value = cfg.notify_at_pct || 85;
  buildMetrics();
  updatePreview();
}

// ── Reset ─────────────────────────────────────────────────────────────
function resetDefaults() {
  fetch('/defaults').then(r => r.json()).then(d => { cfg = d; initUI(); });
}

// ── Save ─────────────────────────────────────────────────────────────
function saveConfig() {
  fetch('/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cfg),
  }).then(r => r.json()).then(d => {
    if (d.ok) {
      const fl = document.getElementById('saved-flash');
      fl.classList.add('show');
      setTimeout(() => { fl.classList.remove('show'); window.close(); }, 800);
    }
  });
}

initUI();
</script>
</body>
</html>
"""

METRIC_DEFS_JS = json.dumps(METRIC_LABELS)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # silence request logs

    def _send(self, code, ctype, body):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/index.html":
            config = _load_config()
            html   = HTML.replace("__CONFIG__", json.dumps(config))
            html   = html.replace("__METRICS__", METRIC_DEFS_JS)
            self._send(200, "text/html; charset=utf-8", html)

        elif path == "/config":
            self._send(200, "application/json", json.dumps(_load_config()))

        elif path == "/defaults":
            self._send(200, "application/json", json.dumps(DEFAULT_CONFIG))

        else:
            self._send(404, "text/plain", "Not found")

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            try:
                new_cfg = json.loads(body)
                _save_config(new_cfg)
                self._send(200, "application/json", '{"ok":true}')
                threading.Timer(0.5, _shutdown_flag.set).start()
            except Exception as e:
                self._send(500, "application/json", json.dumps({"ok": False, "error": str(e)}))
        else:
            self._send(404, "text/plain", "Not found")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def _load_config():
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return copy.deepcopy(DEFAULT_CONFIG)


def _save_config(data):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _find_port(start=45678, attempts=20):
    for port in range(start, start + attempts):
        try:
            with socket.socket() as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return start


def run(open_browser=True):
    port   = _find_port()
    url    = f"http://127.0.0.1:{port}"
    server = HTTPServer(("127.0.0.1", port), Handler)

    print(f"\n  macm-pulse config UI  →  {url}")
    print("  Saving closes the browser tab and the server.\n")

    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    while not _shutdown_flag.is_set():
        server.handle_request()

    server.server_close()
    print("  Config saved.")


if __name__ == "__main__":
    run()
