# macm-hud

**Monitor de estado en tiempo real para Claude Code.**  
Contexto %, límites de uso, coste, compactación — datos exactos de la API de Claude Code, mostrados en la barra bajo el cuadro de entrada.

```
 ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ COMPACT hace 23m │ 5H 28% (2h 14m) │ 7D 41% │ HOY 14 │ SESION 47m │ ~€0.17
```

> Sin estimaciones. Sin llamadas de red. Sin tokens consumidos. 100% local.

---

## Por qué

Claude Code ya no muestra un indicador visual del contexto. Sin él no puedes saber:

- A cuánto estás del próximo auto-compact
- Si te estás acercando al límite de 5 horas
- Cuánto ha costado la sesión hasta ahora
- Qué modelo está activo realmente

macm-hud añade una barra de estado persistente bajo el cuadro de entrada — se actualiza tras cada respuesta, con datos directamente de la API de Claude Code.

---

## Qué muestra

| Métrica | Fuente | ¿Exacto? |
|---|---|---|
| Nombre del modelo | API de Claude Code | Sí |
| Barra de contexto + % | API de Claude Code (`used_percentage`) | Sí |
| Tokens (`146k/200k`) | API de Claude Code | Sí |
| Tokens de caché | API de Claude Code | Sí |
| Límite 5h % + tiempo hasta reset | API de Claude Code | Sí |
| Límite 7 días % | API de Claude Code | Sí |
| Coste de sesión | API de Claude Code | Sí |
| Duración de sesión | API de Claude Code | Sí |
| Última compactación + tiempo transcurrido | Hook local (`PostCompact`) | Sí |
| Mensajes hoy / esta semana | Hook local (`UserPromptSubmit`) | Sí |
| Líneas de código modificadas | API de Claude Code | Sí |
| Hora pico de uso | Hook local (histograma horario) | Sí |
| Herramienta más usada | Hook local (`PreToolUse`) | Sí |
| Racha de días activos | Hook local (seguimiento diario) | Sí |

Cada métrica es un toggle independiente — muestra solo lo que te importa.

---

## Requisitos

- Claude Code CLI
- Python 3.8+
- Windows 10+, macOS 12+ o Linux

---

## Instalación

```bash
git clone https://github.com/m-a-c-m/macm-hudclaudecodeskill
cd macm-hudclaudecodeskill
python install.py
```

El instalador:
1. Copia los scripts de hook a `~/.claude/hooks/`
2. Modifica `~/.claude/settings.json` — hace una copia de seguridad antes
3. Abre la **interfaz de configuración** en el navegador

El status line se activa con tu próximo mensaje en Claude Code.

---

## Temas

Cinco temas con colores ANSI 256-color. La barra cambia de color automáticamente:

| Nivel | Color |
|---|---|
| Menos del 70% | Color del tema |
| 70 – 89% | Amarillo |
| 90%+ | Rojo |

```
cyan    ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ HOY 14 │ ~€0.17
green   ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ HOY 14 │ ~€0.17
purple  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ HOY 14 │ ~€0.17
orange  ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ HOY 14 │ ~€0.17
mono    ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ 5H 28% │ HOY 14 │ ~€0.17
```

---

## Idioma

**Inglés (por defecto):**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT 23m ago │ 5H 28% │ TODAY 14 │ SESSION 47m │ ~$0.18
```

**Español (`language: "es"`):**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT hace 23m │ 5H 28% │ HOY 14 │ SESION 47m │ ~€0.16
```

---

## Interfaz de configuración

Funciona como servidor local en `127.0.0.1` — ningún dato sale de tu máquina.

**Abrirla en cualquier momento:**

```bash
python ~/.claude/hooks/pulse_config_ui.py
```

**O mediante el skill:**

```
/hud config
```

### Qué puedes configurar

| Ajuste | Opciones |
|---|---|
| Tema | Cyan · Verde · Morado · Naranja · Mono |
| Diseño | Compacto (1 línea) · Completo (2 líneas) |
| Idioma | Inglés · Español |
| Moneda | USD · EUR |
| Umbral de alerta | % al que la barra se vuelve roja (por defecto: 85%) |
| Métricas | Toggle individual con previsualización en vivo |

---

## Comandos del skill

Copia `SKILL.md` a `~/.claude/skills/macm-hud/SKILL.md` y reinicia Claude Code para activar los comandos.

| Comando | Acción |
|---|---|
| `/hud` | Activar/desactivar status line |
| `/hud on` | Forzar activación |
| `/hud off` | Forzar desactivación (los hooks siguen recogiendo datos) |
| `/hud config` | Abrir UI de configuración en el navegador |
| `/hud stats` | Mostrar resumen de uso en el chat |
| `/hud reset` | Borrar estadísticas (con confirmación) |
| `/hud uninstall` | Eliminar macm-hud (con confirmación) |

---

## Cómo se integra con Claude Code

macm-hud usa dos puntos de extensión nativos de Claude Code: `statusLine` y `hooks`.

Tras la instalación, tu `~/.claude/settings.json` tendrá estas entradas:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python ~/.claude/hooks/pulse_statusline.py",
    "padding": 1
  },
  "hooks": {
    "UserPromptSubmit": [{ "matcher": "", "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pulse_collector.py" }] }],
    "PostCompact":      [{ "matcher": "", "hooks": [{ "type": "command", "command": "python ~/.claude/hooks/pulse_collector.py" }] }]
  }
}
```

**Archivos creados en `~/.claude/`:**

```
~/.claude/
├── hooks/
│   ├── pulse_collector.py      procesador de hooks — escribe estadísticas entre sesiones
│   ├── pulse_statusline.py     renderizador — lee el stdin de Claude Code
│   └── pulse_config_ui.py      UI web de configuración — solo local, 127.0.0.1
├── macm_pulse_config.json      tus preferencias
└── macm_pulse_stats.json       contadores de uso (se crea automáticamente)
```

`settings.json` se respalda con marca de tiempo antes de cualquier cambio. La desinstalación limpia cada entrada que macm-hud añadió.

---

## Cómo funciona

```
Claude Code
   │
   ├── statusLine  →  pulse_statusline.py
   │     lee:    stdin  (JSON en vivo de la sesión de Claude Code)
   │             macm_pulse_config.json
   │             macm_pulse_stats.json
   │     escribe: nada
   │     imprime: una línea con colores ANSI
   │
   └── hooks  →  pulse_collector.py
         lee:    stdin  (JSON del evento de hook)
         escribe: macm_pulse_stats.json
         imprime: {"continue": true}
```

El script del status line no consume tokens de API — está documentado en la documentación oficial de Claude Code.

---

## Seguridad

- Cero peticiones de red de ningún tipo
- Cero telemetría ni analíticas
- Solo lee sus propios archivos de config/stats y el stdin de Claude Code
- Solo escribe `~/.claude/macm_pulse_stats.json`
- Sin `subprocess`, sin `eval`, sin `exec`

Guía de auditoría completa: [docs/SECURITY.md](docs/SECURITY.md)

Auditoría rápida — estos comandos deben devolver vacío:

```bash
grep -E "urllib|requests|socket|http\." ~/.claude/hooks/pulse_*.py
grep -E "subprocess|os\.system|os\.popen" ~/.claude/hooks/pulse_*.py
grep -E "\beval\b|\bexec\b|__import__" ~/.claude/hooks/pulse_*.py
```

---

## Desinstalar

```bash
python install.py --uninstall
```

Elimina los scripts de hook y limpia `settings.json`. Los archivos de config y stats en `~/.claude/` se conservan — bórralos manualmente si no los necesitas:

```bash
rm ~/.claude/macm_pulse_config.json
rm ~/.claude/macm_pulse_stats.json
```

---

## Solución de problemas

**El status line no aparece**
- Envía un mensaje en Claude Code — se activa tras la primera respuesta.
- Smoke test: `echo '{}' | python ~/.claude/hooks/pulse_statusline.py`
- Comprueba que `disableAllHooks` no sea `true` en tu configuración de Claude Code.

**Todos los valores muestran 0 o están en blanco**
- Los campos de Claude Code son `null` antes de la primera llamada a la API. Envía un mensaje.

**La UI de configuración no se abre**
- Ejecútala manualmente: `python ~/.claude/hooks/pulse_config_ui.py`
- Comprueba que Python esté en PATH: `python --version`

**Reinstalar tras actualizar**

```bash
cd macm-hudclaudecodeskill && git pull
python install.py  # elige Reinstalar
```

---

## Documentación

- English: [README.md](README.md)
- Español: este archivo
- Referencia de configuración: [docs/CONFIG.md](docs/CONFIG.md)
- Guía de auditoría de seguridad: [docs/SECURITY.md](docs/SECURITY.md)

---

## Licencia

MIT — [Miguel Angel Colorado Marin](https://miguelacm.es)
