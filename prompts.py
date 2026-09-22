RULES_PROMPT = """
Reglas estrictas que DEBES cumplir:
1. SOLO puedes usar clases, métodos, atributos y funciones que aparezcan
   explícitamente en el código fuente que se te entrega. Está prohibido
   inventar métodos, parámetros o atributos que no existan.
2. El archivo de salida debe ser código Python válido y ejecutable 
   completamente con `pytest` (con todos los imports necesarios).
3. Los imports deben corresponder exactamente a la ruta/módulo indicado.
4. Evita aserciones triviales (ej. assert True, o comparar un
   objeto contra sí mismo). Cada test debe validar un comportamiento real 
   de la clase (casos normales, casos borde y casos de error/excepciones 
   cuando aplique).
5. NO inventes métodos, atributos, clases o módulos que no existan en el
   código fuente entregado. Usa únicamente lo que puedas verificar en el
   código fuente.
6. No modifiques ni asumas codigo fuente adicional fuera del entregado.
7. Responde ÚNICAMENTE con un bloque de código Python delimitado por
   ```python y ```. No incluyas explicaciones, texto adicional ni
   comentarios fuera del bloque de código.
8. NO uses mocks para reemplazar la lógica que se quiere probar.
"""


def build_generation_prompt(source_code: str, class_name: str, file_path: str) -> str:
    """Prompt inicial: generar la primera versión de la suite de tests."""
    return f"""
Eres un ingeniero de software especializado en testing con pytest.
Tu única tarea es generar código de pruebas unitarias en Python 3.14 usando
exclusivamente la librería estándar de pytest.
 
Archivo objetivo: {file_path}
Nombre del módulo: {class_name}
 
Código fuente a testear:
```python
{source_code}
```
 
Objetivo de las pruebas:
- Cubrir la mayor cantidad posible de líneas y ramas (if/else, try/except,
  loops, casos borde) del código fuente.
- Probar casos normales, casos límite y casos de error/excepción cuando el
  código los contemple.
- Cada función/método público relevante debe tener al menos un test.
 
{RULES_PROMPT}
 
Genera ahora la suite de tests completa.
"""


def build_fix_prompt(source_code: str, test_code: str, error_log: str) -> str:
    """
    Prompt de corrección: se usa cuando pytest falla (error de sintaxis,
    de importación, o aserciones que no pasan). Se le entrega el log de
    error completo para que el modelo pueda diagnosticar la causa exacta.
    """
    return f"""
La siguiente suite de pruebas que generaste falló al ejecutarse con pytest.
 
Código fuente original (no lo modifiques, solo úsalo de referencia):
```python
{source_code}
```
 
Suite de tests actual (con errores):
```python
{test_code}
```
 
Log de error obtenido al ejecutar pytest:
```
{error_log}
```
 
Analiza el error cuidadosamente y corrige la suite de tests para que:
- Compile sin errores de sintaxis.
- Se ejecute sin errores de importación.
- Todas las aserciones pasen correctamente contra el código fuente real.
 
Si el error indica que usaste un método, atributo o import que no existe,
revisa el código fuente original y corrígelo usando solo lo que realmente
existe ahí.
 
{RULES_PROMPT}
 
Devuelve la suite de tests completa y corregida (no solo el fragmento que
cambia).
"""


def build_coverage_prompt(
    source_code: str,
    test_code: str,
    coverage_report: str,
    line_coverage: float,
    branch_coverage: float,
) -> str:
    """
    Prompt de mejora de cobertura: se usa cuando los tests pasan pero no
    alcanzan los umbrales mínimos (Line Coverage >= 80%, Branch Coverage
    >= 50%). Se entregan las líneas y ramas no cubiertas para que el modelo
    agregue casos de prueba dirigidos específicamente a esos puntos.
    """
    return f"""
La siguiente suite de pruebas pasa correctamente, pero su cobertura es
insuficiente.
 
Cobertura actual:
- Line Coverage: {line_coverage * 100:.1f}% (objetivo: >= 80%)
- Branch Coverage: {branch_coverage * 100:.1f}% (objetivo: >= 50%)
 
Reporte detallado de cobertura:
```
{coverage_report}
```
 
Código fuente original:
```python
{source_code}
```
 
Suite de tests actual:
```python
{test_code}
```
 
Agrega o modifica los tests necesarios para cubrir específicamente las
líneas y ramas no cubiertas indicadas en el reporte (por ejemplo, casos
que activen las ramas else/except no probadas, condiciones límite,
parámetros distintos que recorran otros caminos del código). No elimines
tests existentes que ya funcionan; solo agrega o ajusta lo necesario.
 
{RULES_PROMPT}
 
Devuelve la suite de tests completa y actualizada (no solo el fragmento
nuevo).
"""


def build_mutation_prompt(
    source_code: str,
    test_code: str,
    mutation_score: float,
) -> str:
    """
    Prompt de mejora de mutation score: se usa cuando los tests pasan y
    cumplen cobertura, pero el mutation score sigue bajo el umbral (>= 50%).
    Esto generalmente indica que las aserciones son débiles o triviales
    (cubren la línea pero no verifican el resultado real), por lo que se
    le pide al modelo reforzar las aserciones en vez de solo agregar más
    tests.
    """
    return f"""
La siguiente suite de pruebas pasa y tiene buena cobertura de líneas y
ramas, pero su Mutation Score es de solo {mutation_score * 100:.1f}%
(objetivo: >= 50%). Un mutation score bajo con buena cobertura generalmente
significa que las aserciones son débiles, triviales, o no verifican
valores concretos de retorno/estado (por ejemplo, solo verifican que no
haya excepción, en vez de comparar el resultado exacto esperado).
 
Código fuente original:
```python
{source_code}
```
 
Suite de tests actual:
```python
{test_code}
```
 
Refuerza la suite de tests para matar más mutantes:
- Reemplaza aserciones débiles (assertIsNotNone, assert sin comparación de
  valor, try/except que solo verifica que no truene) por comparaciones
  exactas del valor/resultado esperado.
- Verifica valores límite exactos (por ejemplo, si hay comparaciones como
  `>`, prueba también el caso `==` para detectar mutaciones de operador).
- Verifica el estado interno del objeto después de cada operación relevante,
  no solo el valor de retorno.
- No elimines cobertura ya lograda; refuerza sin romper tests que ya
  funcionan.
 
{RULES_PROMPT}
 
Devuelve la suite de tests completa y actualizada (no solo el fragmento
nuevo).
"""
