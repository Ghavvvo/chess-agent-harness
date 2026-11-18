# chess-agent-harness

**Un framework para que cualquier LLM juegue al ajedrez lo mejor posible, sin hacer trampas.**

No es un bot ni un benchmark de fuerza. Es una capa de arquitectura entre el
LLM y las reglas del ajedrez: el modelo decide y un entorno determinista mantiene
el estado, presenta las jugadas disponibles y verifica cada acción.

El MVP ya permite observar y controlar una partida completa desde una interfaz
web. El proyecto crecerá por fases para estudiar qué arquitectura ayuda de verdad
a un LLM a jugar mejor, sin convertir un motor de ajedrez en su oráculo.

## ¿Qué es esto?

`chess-agent-harness` es un entorno de agentes donde un LLM juega partidas
completas mediante un contrato estructurado. La posición vive en `ChessEnv`,
`python-chess` es la autoridad sobre las reglas y cada agente devuelve una
acción UCI como `e2e4`.

El agente LLM admite dos modos:

- `tools`: expone `legal_moves` y `make_move` mediante tool calling. La posición
  actual se entrega en la observación y `make_move` restringe la elección a las
  jugadas legales conocidas por el entorno.
- `plain`: entrega FEN y jugadas legales en el prompt y pide una única jugada
  UCI. Este modo permite usar servidores OpenAI-compatible sin tool calling.

En ambos casos, el entorno vuelve a validar la acción. Si el LLM propone una
jugada ilegal y el fallback está habilitado, se emite un evento visible y la
partida continúa con una jugada legal aleatoria.

| Otros proyectos | `chess-agent-harness` |
|---|---|
| Miden y clasifican modelos | Busca mejorar la arquitectura de cualquier LLM |
| Preguntan qué modelo gana | Pregunta qué contexto y herramientas le ayudan |
| El motor puede decidir la jugada | El LLM decide y el entorno verifica |
| Se centran en el resultado agregado | Se centra en el ciclo de decisión del agente |

## Qué funciona hoy

El MVP actual incluye:

- partidas `random vs random`, `LLM vs random` o `LLM vs LLM`;
- clientes OpenAI-compatible para OpenAI, Ollama, vLLM y LM Studio;
- selección por tool calling o respuesta UCI en texto plano;
- validación de legalidad y finales mediante `python-chess`;
- fallback configurable ante jugadas ilegales;
- límite configurable de medias jugadas;
- eventos en vivo mediante FastAPI y WebSocket;
- tablero React con historial, Play/Pausa, Stop, Anterior y Siguiente;
- una partida compartida por todos los espectadores conectados;
- estado y eventos solo en memoria durante la ejecución;
- PGN fuera del flujo obligatorio del MVP.

## Qué no es

- **No es un motor de ajedrez.** No pretende competir con Stockfish.
- **No es un benchmark todavía.** No hay leaderboard, métricas agregadas ni
  ranking de modelos.
- **No usa un motor como oráculo.** La verificación solo comprueba reglas y
  legalidad; no recomienda la mejor jugada.
- **No conserva memoria entre partidas.** Cada partida comienza desde cero.
- **No tiene autenticación ni salas.** Todos los clientes conectados observan y
  controlan la misma partida.
- **No persiste una traza por ply.** El historial existe en RAM para transportar
  el estado y navegar en la interfaz.
- **No es un producto final.** Es un núcleo usable sobre el que ejecutar
  experimentos controlados.

## Para qué sirve

1. **Harness de desarrollo.** Observar cómo un LLM actúa en un dominio con
   estado formal, reglas verificables y horizonte largo.
2. **Base experimental.** Comparar prompts, contratos de tools, memoria o
   verificadores sin reescribir las reglas ni la interfaz de los agentes.
3. **Demo en vivo.** Mostrar una partida en tiempo real, pausarla, reiniciarla y
   recorrer las posiciones recibidas.
4. **Banco de pruebas futuro.** Añadir evaluación y reproducción cuando el core
   sea estable, manteniendo separadas ejecución y medición.

## Principios de diseño

1. **El estado vive en el entorno.** El modelo recibe una observación; no es la
   fuente de verdad del tablero.
2. **Tools-first.** Siempre que el proveedor lo permita, el agente elige mediante
   herramientas con argumentos estructurados.
3. **El LLM decide.** Ningún motor selecciona jugadas en nombre del modelo.
4. **Verificación determinista.** `python-chess` resuelve legalidad, turnos y
   condiciones de final de partida.
5. **Separación de responsabilidades.** El loop emite eventos sin conocer
   WebSocket o React; el transporte no contiene lógica de agentes.
6. **Extensión por fases.** Memoria, métricas y evaluación deben integrarse
   alrededor de los contratos existentes.

## Arquitectura del MVP

```text
frontend React
    │  comandos: start / pause / resume / stop
    │  eventos: game_started / move / illegal / control / game_over / game_reset
    ▼
FastAPI WebSocket ── ConnectionManager
    │
    ▼
game_loop ── Agent.act(Observation) → Action
    │                 ├── RandomAgent
    │                 └── LLMAgent (plain | tools)
    ▼
ChessEnv ── python-chess
```

```text
backend/
├── main.py              aplicación FastAPI y control de la partida compartida
├── core/
│   ├── env.py           estado y reglas mediante python-chess
│   ├── schemas.py       contratos Observation y Action
│   └── game_loop.py     ciclo independiente que emite eventos
├── agents/
│   ├── base.py          interfaz común de agentes
│   ├── random_agent.py  agente de referencia
│   └── llm_agent.py     cliente OpenAI-compatible
└── ws/
    └── manager.py       conexiones, broadcast y replay en memoria

frontend/src/
├── App.tsx              estado del espectador y controles
└── components/Board.tsx tablero de solo lectura

configs/game.yaml        agentes y límites de la partida
```

`game_loop` no importa `ws` ni frontend. `ConnectionManager` no importa agentes.
`main.py` actúa como composition root: construye los agentes, conecta el loop con
el transporte y procesa los comandos del usuario.

## Cómo se controla una partida

- **Play** crea una partida nueva o reanuda una partida pausada.
- **Pausar** detiene el loop antes de la siguiente decisión; una llamada al LLM
  que ya esté en curso puede terminar.
- **Stop** cancela la tarea, limpia el historial y restaura la posición inicial.
- **Anterior** y **Siguiente** recorren localmente las posiciones recibidas sin
  modificar el estado compartido del backend.

Al reconectar, el servidor reproduce los eventos conservados en RAM. Reiniciar
el proceso del backend elimina ese estado.

## Instalación

Requisitos: Python 3.11 o posterior y pnpm.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pnpm --dir frontend install
```

Inicia el backend:

```sh
source .venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

En otra terminal, inicia el frontend:

```sh
pnpm --dir frontend dev
```

Abre [http://localhost:5173](http://localhost:5173).

## Configuración de agentes

El proyecto arranca como `random vs random` para funcionar sin credenciales. La
configuración vive en `configs/game.yaml`:

```yaml
white:
  type: llm
  provider: openai
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini
  mode: tools

black:
  type: random

max_plies: 200
illegal_fallback: true
move_delay: 0.4
ws:
  host: 0.0.0.0
  port: 8000
```

Para OpenAI, exporta la clave antes de iniciar el servidor:

```sh
export OPENAI_API_KEY='tu-clave'
```

Para Ollama, vLLM o LM Studio, usa su endpoint OpenAI-compatible, establece
`provider: local` y selecciona un modelo disponible. Usa `mode: plain` si el
servidor o modelo no admite tool calling. Los cambios al YAML requieren reiniciar
el backend.

## Verificación

```sh
.venv/bin/python -m pytest
.venv/bin/python -m backend.core.game_loop
pnpm --dir frontend build
```

Las pruebas actuales cubren FEN válidos durante el loop, recuperación ante una
jugada ilegal y el flujo básico de eventos WebSocket, incluido el reset.

## Hacia dónde va el proyecto

La evolución prevista está organizada para validar cada capacidad antes de
incorporar la siguiente:

### Fase 1 — Núcleo jugable

Estabilizar los contratos de observación y acción, el ciclo de partida, los
controles y la compatibilidad con proveedores OpenAI-compatible. Esta es la fase
actual.

### Fase 2 — Reproducibilidad y evaluación

Añadir identificadores de partida, semillas, PGN persistente opcional, eventos
reproducibles y métricas separadas del loop. Esto permitirá comparar estrategias
sin convertir el core en un benchmark runner.

### Fase 3 — Mejor contexto para el LLM

Evaluar memoria dentro de una partida, resúmenes estructurados, planes y
recuperación de posiciones similares. Cada incorporación deberá demostrar una
mejora medible frente al agente base.

### Fase 4 — Verificación táctica controlada

Explorar verificadores y crítica de candidatos. Si se integra Stockfish, su rol
será oponente, evaluador posterior o componente experimental explícito; nunca un
canal oculto que entregue al LLM la jugada correcta.

### Fase 5 — Escala

Incorporar múltiples salas, aislamiento de partidas, autenticación, workers y un
runner de experimentos sin cambiar los contratos fundamentales de `ChessEnv` y
`Agent`.

La hoja de ruta es una dirección de diseño, no una promesa de funcionalidades ya
implementadas.

## Licencia

Distribuido bajo la [licencia MIT](LICENSE).
