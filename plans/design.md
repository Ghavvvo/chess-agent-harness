# Diseño
Simplificación final: solo cuatro botones visibles (Play/Pausa, Stop, Anterior y Siguiente). Stop cancela la tarea y restaura tablero e historial. El historial deja de ser interactivo. En escritorio, tablero y panel ocupan la altura disponible y solo el historial tiene desplazamiento interno.
Verificación: build TypeScript/Vite aprobado. Revisión visual bloqueada: el host de navegador de la herramienta no está disponible. Pendiente confirmar render móvil y escritorio.
Revisión UX: tablero y navegación en una columna; control de partida e historial en otra. En móvil se apilan sin anchos mínimos. Cabecera compacta, controles táctiles de 44px, foco visible y estado seleccionado textual. Eliminar el titular promocional para dar espacio al juego. Mantener paleta azul y tipografía de torneo; una superficie lateral, sin tarjetas repetidas.
Wireframe: [marca / conexión] [tablero + navegación | estado + acción + historial]. Móvil: [marca] [tablero] [navegación] [control + historial].
Tablero protagonista: una mesa de torneo azul, acompañada por una planilla de jugadas.
Paleta: papel #f5f7fb, tinta #20314c, azul #496b9b, casilla clara #dee7f2, blanco #ffffff, aviso #9a451c.
Tipografía: Trebuchet MS para interfaz y títulos; cifras tabulares para jugadas.
Alineación izquierda; tablero cuadrado dominante, registro lateral; apilado en móvil.
Wireframe: [nombre / conexión] [tablero | jugadores + planilla] [estado].
Alternativa descartada: tarjetas de métricas; no sirven al alcance.
Revisión: concentrar identidad en el tablero azul y la planilla; eliminar hero comercial y adornos.
