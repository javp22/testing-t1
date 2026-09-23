# Agente de generación automática de tests

## Estrategia y arquitectura

El agente recibe un archivo Python y genera una suite `pytest` en cuatro fases. `build_generation_prompt` solicita una primera suite usando únicamente el código fuente, con casos normales, límites y excepciones. Si `pytest` falla, `build_fix_prompt` entrega al LLM la suite y el log para corregir imports, APIs o aserciones. Cuando la suite pasa, se mide cobertura de líneas y ramas con `coverage`; si no alcanza 80% y 50%, `build_coverage_prompt` solicita casos dirigidos a las líneas y ramas faltantes. Finalmente, Cosmic Ray calcula el mutation score mediante `cr-rate` y los mutantes sobrevivientes se entregan a `build_mutation_prompt` para reforzar las pruebas. Los candidatos que rompen `pytest` se descartan y se conserva la última versión estable. Cada objetivo tiene un presupuesto de 105 segundos.

Los prompts restringen al modelo al código entregado, prohíben aserciones triviales y exigen código Python ejecutable. La cobertura detecta caminos no recorridos, mientras la mutación evalúa si las aserciones distinguen el comportamiento original del mutado.

## Desafíos y calidad

La integración de Cosmic Ray fue la principal complicación: requiere rutas relativas, una configuración temporal, una base SQLite, ejecución de mutantes con timeout y conversión de supervivencia a mutation score. También hubo imports y dependencias ausentes. En algunos casos el LLM usó `MagicMock` o modificó `sys.modules` para hacer ejecutables los tests, lo que reduce su fidelidad al sistema real pese a estar prohibido por el prompt.

Se generaron 20 suites, con 174 tests y 387 verificaciones explícitas. En 14/20 objetivos se alcanzaron los umbrales de cobertura y en 12/20 se obtuvo mutation score >= 50%. Entre las 12 sesiones con score no nulo, los promedios fueron 98.7% de líneas, 87.9% de ramas y 83.3% de mutación. Sin embargo, hubo seis resultados con todas las métricas en cero y casos con cobertura alta pero mutation score cero, demostrando que cubrir líneas no garantiza calidad semántica.

Hay aserciones útiles de valores, estados y excepciones; por ejemplo, `gin_rummy/dealer` verifica el reparto y el agotamiento del mazo. También hay fragilidad: `fuzzywuzzy/StringMatcher` simula completamente `Levenshtein` y algunos tests usan mocks para módulos enteros. Los mutantes sobrevivientes muestran qué comportamientos no fueron especificados. Por esto, las suites son un buen borrador, pero requieren revisión humana para reducir mocks, duplicación y casos poco significativos.

## Comportamiento iterativo y limitaciones

Los logs muestran 43 intentos de `pytest` en las 12 suites que alcanzaron las tres metas, aproximadamente 3.6 intentos por objetivo. El mínimo fue 2 (`blackjack/base`) y el máximo 9 (`mahjong/game`), incluyendo la generación inicial y las correcciones. Sumando una medición de cobertura y otra de mutación, se obtienen aproximadamente 5.6 fases de validación por suite exitosa. Este valor no equivale exactamente al número de llamadas al LLM, porque no se registraron todos los prompts.

Los primeros fallos se debieron a imports, APIs inferidas, aserciones incompatibles y dependencias externas. Además, la API gratuita y de alta demanda produjo errores 503, respuestas tardías y ejecuciones agotadas por el límite de tiempo. Cosmic Ray también puede entregar resultados parciales por timeout: el mutation score cambió entre corridas, por ejemplo, de 15% a 80% en `mahjong/player`. Por tanto, los promedios son observaciones aproximadas, no garantías reproducibles. Una mejora sería registrar por llamada el intento, duración, resultado de `pytest` y métricas antes y después.
