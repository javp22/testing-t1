RULES_PROMPT = """
REGLAS ESTRICTAS QUE DEBES CUMPLIR:

1. SOLO puedes usar clases, métodos, funciones, atributos, excepciones,
   constantes, parámetros y módulos que aparezcan explícitamente en el
   código fuente entregado. NO inventes APIs.

2. Los imports deben corresponder exactamente a los módulos y rutas que
   pueden verificarse a partir del código fuente entregado. NO inventes
   módulos ni rutas de importación.

3. El resultado debe ser un archivo Python válido y ejecutable con pytest.

4. NO modifiques el código fuente que se está testeando. Solo puedes
   modificar la suite de tests.

5. Cada test debe verificar un comportamiento real del código. No uses
   aserciones triviales como:
       assert True
       assert False
       assert obj == obj
       assert result is not None
   salvo que la condición "is not None" sea específicamente el comportamiento
   que se desea verificar.

6. NO uses mocks, monkeypatch, MagicMock, Mock ni técnicas equivalentes para
   reemplazar la lógica que se quiere probar. Los tests deben ejecutar la
   implementación real.

7. Cuando pruebes excepciones, verifica la excepción concreta y, cuando sea
   posible, también el comportamiento asociado a ella.

8. NO asumas comportamiento que no pueda deducirse directamente del código
   fuente. Si un comportamiento no está definido explícitamente, no lo
   inventes.

9. Para valores esperados, usa únicamente resultados que puedan derivarse
   del código fuente.

10. Si la suite de tests existente ya contiene tests correctos, NO los
    elimines ni los debilites. Los cambios deben preservar su comportamiento.

11. Cuando se solicite mejorar cobertura o mutation score, modifica la suite
    de forma incremental. Prioriza agregar casos específicos antes que
    reescribir tests existentes.

12. Cada nuevo test debe tener una razón concreta:
    - cubrir una línea no cubierta,
    - cubrir una rama no cubierta,
    - detectar un mutante específico,
    - verificar un caso límite,
    - o verificar un comportamiento de error.

13. NO agregues tests cuyo único objetivo sea aumentar artificialmente una
    métrica.

14. Si un test existente ya detecta un caso, NO dupliques innecesariamente
    ese caso.

15. El código final debe contener todos los imports necesarios y debe ser
    autocontenido como archivo de tests.

16. Responde ÚNICAMENTE con un bloque de código Python delimitado por
    ```python y ```.
    NO incluyas explicaciones, texto adicional ni bloques adicionales.
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
    surviving_mutants_report: str,
) -> str:
    """
    Prompt de mejora de mutation score: se usa cuando los tests pasan y
    cumplen cobertura, pero existen mutantes sobrevivientes. Se entrega
    el detalle de cada mutante para que el modelo agregue o refuerce tests
    específicamente capaces de detectarlos.
    """
    return f"""
La siguiente suite de pruebas pasa y tiene buena cobertura, pero existen
mutantes de código que sobreviven a los tests.

Mutation Score actual:
{mutation_score * 100:.1f}%

Código fuente original:
```python
{source_code}
````

Suite de tests actual:

```python
{test_code}
```

Los siguientes son los mutantes que sobrevivieron a la última ejecución
de Cosmic Ray:

```text
{surviving_mutants_report}
```

Tu tarea es modificar la suite de tests para que los mutantes
sobrevivientes sean detectados y eliminados.

Para cada mutante sobreviviente:

1. Identifica qué cambio introduce el mutante.
2. Identifica qué comportamiento del código original permite distinguirlo
   del código mutado.
3. Agrega o modifica tests que verifiquen explícitamente ese comportamiento.
4. Usa valores concretos que hagan que el código original y el código
   mutado produzcan resultados diferentes.
5. Si el mutante cambia un operador (`>`, `<`, `==`, `!=`, `+`, `-`, etc.),
   prueba valores límite que permitan detectar específicamente ese cambio.
6. Si cambia un valor retornado, verifica el valor exacto esperado.
7. Si cambia una condición, crea casos que recorran ambos lados de la
   condición.
8. Si cambia una excepción o una rama de error, verifica explícitamente el
   comportamiento esperado.
9. No agregues tests únicamente para aumentar cobertura: cada test debe
   ser capaz de detectar uno o más de los mutantes sobrevivientes.
10. No elimines tests existentes que ya funcionan.

Es importante que NO asumas que todos los mutantes requieren un test
nuevo. Si un test existente puede reforzarse para detectar un mutante,
modifica ese test en lugar de duplicar lógica innecesariamente.

{RULES_PROMPT}

Devuelve la suite de tests completa y actualizada (no solo los tests nuevos).
"""
