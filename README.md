# Chess agent harness
Espectador en vivo de una partida compartida. Python 3.11+ y pnpm.

## Ejecutar
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
uvicorn backend.main:app --reload
```
En otra terminal:
```sh
pnpm --dir frontend install
pnpm --dir frontend dev
```
Abrir http://localhost:5173. Play inicia o reanuda; Pausar detiene el loop antes de la siguiente decisión y permite terminar la jugada en curso. Stop cancela la partida y restaura el tablero. Anterior y Siguiente navegan localmente por las posiciones recibidas. Todos los espectadores pueden controlar la partida compartida, sin autenticación.
Reconectar reproduce los eventos de la partida actual; reiniciar el backend inicia una nueva.
Los eventos se mantienen solo en RAM durante esa partida, sin almacenamiento persistente.

## LLM
Cambiar white o black en configs/game.yaml:
```yaml
white:
  type: llm
  provider: openai
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini
  mode: tools
```
Exportar OPENAI_API_KEY antes de ejecutar el backend. Para Ollama, vLLM o
LM Studio usar su URL OpenAI-compatible, provider: local y un modelo instalado.
El servidor debe admitir tool calling para tools; usar plain si no lo admite.
Cada decisión usa mensajes nuevos. Hay un máximo de cuatro rondas de tools.
Los fallos del proveedor terminan la partida; las jugadas ilegales usan fallback
si illegal_fallback está habilitado. max_plies termina con resultado * si no
hay resultado natural. Cambios YAML requieren reiniciar el backend.
Los campos ws documentan host/puerto deseados; pasarlos a uvicorn con --host/--port.

## Verificar
```sh
.venv/bin/python -m pytest
.venv/bin/python -m backend.core.game_loop
pnpm --dir frontend build
```
core emite eventos sin conocer ws. ws transporta eventos sin importar agentes.
Sin métricas, memoria entre partidas, autenticación ni interacción con piezas.
