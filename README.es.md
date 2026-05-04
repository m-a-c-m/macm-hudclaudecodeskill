# macm-pulse

**Monitor de estado en tiempo real para Claude Code.**  
Contexto %, límites de uso, coste, compactación — datos exactos de la API de Claude Code, mostrados en la barra bajo el cuadro de entrada.

```
 ◈ Sonnet 4.6  ████████████░░ 73%  146k/200k │ CACHE 39k │ COMPACT hace 23m │ 5H 28% (2h 14m) │ 7D 41% │ HOY 14 │ ~€0.17
```

> Sin estimaciones. Sin llamadas de red. Sin tokens consumidos. 100% local.

---

## Qué muestra

| Métrica | Fuente | ¿Exacto? |
|---|---|---|
| Nombre del modelo | API de Claude Code | Sí |
| Barra de contexto + % | API de Claude Code (`used_percentage`) | Sí |
| Tokens (`109k/200k`) | API de Claude Code | Sí |
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

Cada métrica es un toggle — muestra solo lo que te importa.

---

## Requisitos

- Claude Code CLI
- Python 3.8+
- Windows 10+, macOS 12+ o Linux

---

## Instalación

```bash
git clone https://github.com/m-a-c-m/macm-pulse
cd macm-pulse
python install.py
```

El instalador:
1. Copia los scripts de hook a `~/.claude/hooks/`
2. Modifica `~/.claude/settings.json` (hace una copia de seguridad antes)
3. Abre la **interfaz de configuración** en el navegador

Tras guardar en la UI, el status line se activa con tu próximo mensaje en Claude Code.

---

## Interfaz de configuración

La UI funciona como servidor web local en `127.0.0.1` — ningún dato sale de tu máquina.

**Para abrirla en cualquier momento:**

```bash
python ~/.claude/hooks/pulse_config_ui.py
```

**O mediante el skill:**

```
/pulse config
```

### Qué puedes configurar

- **Tema** — Cyan / Verde / Morado / Naranja / Mono (con previsualización en vivo)
- **Diseño** — Compacto (1 línea) o Completo (2 líneas)
- **Idioma** — Inglés o Español (`TODAY` vs `HOY`, `SESSION` vs `SESION`)
- **Moneda** — USD o EUR
- **Umbral de alerta** — % al que la barra de contexto se vuelve roja (por defecto: 85%)
- **Métricas** — activa o desactiva cada una individualmente con previsualización en vivo

### Opciones de idioma

**Inglés (por defecto):**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT 23m ago │ 5H 28% │ TODAY 14 │ SESSION 47m │ ~$0.18
```

**Español:**
```
 ◈ Sonnet 4.6  ████████░░ 73% │ COMPACT hace 23m │ 5H 28% │ HOY 14 │ SESION 47m │ ~€0.16
```

Configúralo en la UI bajo **Etiquetas: Inglés / Español**.

---

## Comandos del skill

Instala el skill copiando `SKILL.md` a `~/.claude/skills/macm-pulse/SKILL.md` y reinicia Claude Code.

| Comando | Acción |
|---|---|
| `/pulse` | Activar/desactivar status line |
| `/pulse on` | Forzar activación |
| `/pulse off` | Forzar desactivación (los hooks siguen recogiendo datos) |
| `/pulse config` | Abrir UI de configuración en el navegador |
| `/pulse stats` | Mostrar resumen de uso en el chat |
| `/pulse reset` | Borrar estadísticas (con confirmación) |
| `/pulse uninstall` | Eliminar macm-pulse (con confirmación) |

---

## Temas

| Nombre | Color |
|---|---|
| `cyan` (por defecto) | Azul-cian brillante |
| `green` | Verde de terminal |
| `purple` | Violeta |
| `orange` | Ámbar cálido |
| `mono` | Gris neutro |

El color de la barra de contexto cambia automáticamente según el nivel:

- `< 70%` → color del tema
- `70–89%` → amarillo
- `≥ 90%` → rojo

---

## Desinstalar

```bash
python install.py --uninstall
```

Esto elimina los scripts de hook y limpia `settings.json`. Los archivos de configuración y estadísticas en `~/.claude/` se conservan — bórralos manualmente si no los necesitas:

```bash
rm ~/.claude/macm_pulse_config.json
rm ~/.claude/macm_pulse_stats.json
```

---

## Cómo funciona

```
Claude Code
   │
   ├── script statusLine  →  pulse_statusline.py
   │     lee:    stdin (JSON en vivo de la sesión de Claude Code)
   │             ~/.claude/macm_pulse_config.json
   │             ~/.claude/macm_pulse_stats.json
   │     escribe: nada
   │     imprime: una línea formateada
   │
   └── hooks (6 eventos)  →  pulse_collector.py
         lee:    stdin (JSON del evento de hook)
         escribe: ~/.claude/macm_pulse_stats.json
         salida:  {"continue": true}
```

El script del status line se ejecuta tras cada respuesta de Claude — no consume tokens de API (documentado en la documentación oficial de Claude Code).

---

## Archivos creados al instalar

```
~/.claude/
├── hooks/
│   ├── pulse_collector.py      procesador de eventos de hook
│   ├── pulse_statusline.py     renderizador del status line
│   └── pulse_config_ui.py      UI web de configuración
├── macm_pulse_config.json      tus preferencias
└── macm_pulse_stats.json       contadores de uso (se crea automáticamente)
```

`~/.claude/settings.json` se edita para añadir las entradas `statusLine` y `hooks`. Se crea una copia de seguridad con marca de tiempo antes de cualquier cambio.

---

## Seguridad

- Cero llamadas de red
- Cero telemetría
- Solo lee sus propios archivos de configuración/estadísticas y el stdin de Claude Code
- Solo escribe `~/.claude/macm_pulse_stats.json`
- Sin `subprocess`, sin `eval`, sin `exec`
- Auditable en ~2 minutos: ver [docs/SECURITY.md](docs/SECURITY.md)

---

## Solución de problemas

**El status line no aparece**

- Envía un mensaje en Claude Code — se activa tras la primera interacción.
- Ejecuta el smoke test: `echo '{}' | python ~/.claude/hooks/pulse_statusline.py`
- Comprueba que Claude Code no esté ejecutándose con `disableAllHooks: true` en settings.

**Todos los valores muestran 0 o están en blanco**

- Los campos de Claude Code (%, coste, límites) son `null` antes de la primera llamada a la API. Envía un mensaje.

**La UI de configuración no se abre**

- Ejecútala manualmente: `python ~/.claude/hooks/pulse_config_ui.py`
- Comprueba que Python esté en tu PATH: `python --version`

**Reinstalar / actualizar tras descargar una nueva versión**

```bash
cd macm-pulse && git pull
python install.py  # elige opción 1 (Reinstalar)
```

---

## Licencia

MIT — [Miguel Angel Colorado Marin](https://miguelacm.es)
