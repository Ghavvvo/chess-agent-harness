# Plan de implementación
Control de usuario: inicio manual, pausa cooperativa entre jugadas y reanudación por WebSocket. Navegación local por FEN sin alterar la partida compartida. Verificar comandos y build.
1. Crear entorno validado, contratos y agentes random/LLM.
2. Implementar loop con eventos y fallback configurable.
3. Servir una partida compartida por WebSocket, con sincronización al conectar.
4. Construir espectador React responsive.
5. Verificar tests y build; documentar ejecución con pip y pnpm.
