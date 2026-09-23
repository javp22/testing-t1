import argparse
import json
import os
import sys
import time

from dotenv import load_dotenv
from google import genai

from agent_functions import (
    clean_llm_code,
    run_pytest,
    measure_coverage,
    measure_mutation,
    get_surviving_mutants_report,
)
from prompts import (
    build_coverage_prompt,
    build_fix_prompt,
    build_generation_prompt,
    build_mutation_prompt,
)
from utils import ExecutionTimer, save_metrics_json

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Budget total con margen de seguridad
MAX_TIME_BUDGET = 105.0

# Umbrales mínimos exigidos por el enunciado
MIN_LINE_COVERAGE = 0.80
MIN_BRANCH_COVERAGE = 0.50
MIN_MUTATION_SCORE = 0.50

# Margen mínimo de tiempo para arriesgarse a pedirle algo más al LLM. Sin
# esto, el agente podía entrar a una vuelta más del loop con, por ejemplo,
# 1 segundo restante, y la llamada a Gemini se cortaba a medio camino.
MIN_TIME_FOR_LLM_CALL = 8.0


def write_test_file(test_file_path: str, test_code: str) -> None:
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_code)


def ask_llm(
    chat,
    prompt: str,
    timer: ExecutionTimer = None,
    max_retries: int = 3,
    initial_delay: float = 2.0,
) -> str:
    """Envía un prompt al chat de Gemini con sistema de reintentos y control de tiempo."""
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        if timer and (timer.is_expired() or timer.time_left() < MIN_TIME_FOR_LLM_CALL):
            raise TimeoutError("Tiempo insuficiente para realizar la solicitud al LLM.")

        try:
            response = chat.send_message(prompt)
            return clean_llm_code(response.text)
        except Exception as e:
            if attempt == max_retries:
                print(
                    f"[Agent Warning] Se agotaron los {max_retries} intentos con Gemini: {e}"
                )
                raise e

            if timer and timer.time_left() < delay + MIN_TIME_FOR_LLM_CALL:
                print(
                    f"[Agent Warning] Tiempo restante insuficiente para esperar reintento ({timer.time_left():.1f}s)."
                )
                raise e

            print(
                f"[Agent Warning] Falló la llamada a Gemini (intento {attempt}/{max_retries}): {e}. Reintentando en {delay:.1f}s..."
            )
            time.sleep(delay)
            delay *= 1.5


def main(ruta_archivo, output_folder):

    timer = ExecutionTimer(max_seconds=MAX_TIME_BUDGET)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: No se encontró la variable GEMINI_API_KEY en el entorno.")
        sys.exit(1)

    ruta_archivo_abs = os.path.abspath(ruta_archivo)

    if not os.path.isfile(ruta_archivo_abs):
        print(f"Error: El archivo objetivo no existe: {ruta_archivo_abs}")
        sys.exit(1)

    class_name = os.path.splitext(os.path.basename(ruta_archivo_abs))[0]
    os.makedirs(output_folder, exist_ok=True)
    test_file_path = os.path.join(output_folder, f"test_{class_name}.py")

    coverage_output = os.path.join(output_folder, "_coverage_data")
    mutation_output = os.path.join(output_folder, "_mutation_data")

    print("Iniciando Agente de Testing Automático...")
    print(f"Ruta del archivo: {ruta_archivo_abs}")
    print(f"Directorio de salida: {output_folder}")

    with open(ruta_archivo_abs, "r", encoding="utf-8") as f:
        source_code = f.read()

    client = genai.Client()
    chat = client.chats.create(model="gemini-3.1-flash-lite")

    test_code = ""
    best_test_code = ""
    best_line_cov, best_branch_cov, best_mutation_score = 0.0, 0.0, 0.0

    # --- Generación inicial ----------------------------------------------------
    try:
        prompt = build_generation_prompt(source_code, class_name, ruta_archivo_abs)
        test_code = ask_llm(chat, prompt, timer)
        write_test_file(test_file_path, test_code)
    except Exception as e:
        print(f"[Agent] Error en la generación inicial: {e}")
        save_metrics_json(output_folder, 0.0, 0.0, 0.0)
        sys.exit(1)

    # --- Corrección de errores de ejecución --------------------------------
    passing = False
    fix_attempt = 0
    while not timer.is_expired() and timer.time_left() >= MIN_TIME_FOR_LLM_CALL:
        fix_attempt += 1

        success, logs = run_pytest(test_file_path, PROJECT_ROOT)
        if success:
            passing = True
            best_test_code = test_code
            print(f"[Agent] pytest exitoso (intento {fix_attempt}).")
            break

        print(
            f"[Agent] pytest falló (intento {fix_attempt}). Reintentando con feedback del error..."
        )
        try:
            prompt = build_fix_prompt(source_code, test_code, logs)
            test_code = ask_llm(chat, prompt, timer)
            write_test_file(test_file_path, test_code)
        except Exception as e:
            print(f"[Agent] Error al pedir corrección al LLM: {e}")
            break
    else:
        print("[Agent] Tiempo agotado durante la corrección de errores.")

    if not passing:
        success, _ = run_pytest(test_file_path, PROJECT_ROOT)
        if success:
            passing = True
            best_test_code = test_code

    # --- Mejora de cobertura -------------------------------------------------
    line_cov, branch_cov = 0.0, 0.0
    if passing:
        coverage_attempt = 0
        while (
            not timer.is_expired()
            and timer.time_left() >= MIN_TIME_FOR_LLM_CALL
            and not (
                line_cov >= MIN_LINE_COVERAGE and branch_cov >= MIN_BRANCH_COVERAGE
            )
        ):
            coverage_attempt += 1

            line_cov, branch_cov, report = measure_coverage(
                test_file_path, ruta_archivo_abs, coverage_output
            )
            print(
                f"[Agent] Cobertura (intento {coverage_attempt}): line={line_cov * 100:.1f}% branch={branch_cov * 100:.1f}%"
            )

            if line_cov >= best_line_cov and branch_cov >= best_branch_cov:
                best_test_code = test_code
                best_line_cov, best_branch_cov = line_cov, branch_cov

            if line_cov >= MIN_LINE_COVERAGE and branch_cov >= MIN_BRANCH_COVERAGE:
                break

            try:
                prompt = build_coverage_prompt(
                    source_code, test_code, report, line_cov, branch_cov
                )
                candidate_code = ask_llm(chat, prompt, timer)
                write_test_file(test_file_path, candidate_code)
            except Exception as e:
                print(f"[Agent] Error al pedir mejora de cobertura al LLM: {e}")
                break

            success, logs = run_pytest(test_file_path, PROJECT_ROOT)
            if success:
                test_code = candidate_code
            else:
                print(
                    "[Agent] La mejora de cobertura rompió pytest; se descarta y se conserva la versión estable."
                )
                write_test_file(test_file_path, best_test_code)
                test_code = best_test_code
                break
        else:
            print("[Agent] Tiempo agotado durante la mejora de cobertura.")

    # --- Mejora de mutation score ---------------------------------------------
    mutation_score = 0.0
    if passing:
        mutation_attempt = 0
        while mutation_score < MIN_MUTATION_SCORE and not timer.is_expired():
            mutation_attempt += 1

            mutation_score = measure_mutation(
                test_file_path, ruta_archivo_abs, mutation_output
            )

            print(
                f"[Agent] Mutation score (intento {mutation_attempt}): "
                f"{mutation_score * 100:.1f}%"
            )

            if mutation_score >= best_mutation_score:
                best_test_code = test_code
                best_mutation_score = mutation_score

            if mutation_score >= MIN_MUTATION_SCORE:
                break

            if timer.time_left() < MIN_TIME_FOR_LLM_CALL:
                print(
                    "[Agent] Tiempo insuficiente para pedir otro refuerzo de mutación."
                )
                break

            # Obtener los mutantes que sobrevivieron a la ejecución de Cosmic Ray
            session_db = os.path.join(mutation_output, "session.sqlite")
            surviving_mutants_report = get_surviving_mutants_report(
                session_db,
                PROJECT_ROOT,
            )

            if not surviving_mutants_report:
                print(
                    "[Agent] No se encontraron mutantes sobrevivientes para "
                    "entregar al LLM."
                )
                break

            print("[Agent] Mutantes sobrevivientes encontrados.")
            print(surviving_mutants_report)

            try:
                prompt = build_mutation_prompt(
                    source_code,
                    test_code,
                    mutation_score,
                    surviving_mutants_report,
                )

                candidate_code = ask_llm(chat, prompt, timer)
                write_test_file(test_file_path, candidate_code)

            except Exception as e:
                print(f"[Agent] Error al pedir mejora de mutation score al LLM: {e}")
                break

            success, logs = run_pytest(test_file_path, PROJECT_ROOT)

            if success:
                test_code = candidate_code
                line_cov, branch_cov, _ = measure_coverage(
                    test_file_path, ruta_archivo_abs, coverage_output
                )
            else:
                print(
                    "[Agent] El refuerzo de mutation rompió pytest; "
                    "se descarta y se conserva la versión estable."
                )
                write_test_file(test_file_path, best_test_code)
                test_code = best_test_code
                break

    # --- Exportación de mejor código -------------------------------------------
    final_code = best_test_code if best_test_code else test_code

    final_line_cov = best_line_cov if best_line_cov else line_cov
    final_branch_cov = best_branch_cov if best_branch_cov else branch_cov
    final_mutation_score = (
        best_mutation_score if best_mutation_score else mutation_score
    )

    # Comparar contra un resultado previo en la misma carpeta de salida (si
    # existe)
    previous_metrics_path = os.path.join(output_folder, "metrics.json")
    should_overwrite = True

    if os.path.exists(previous_metrics_path):
        try:
            with open(previous_metrics_path, "r", encoding="utf-8") as f:
                previous_metrics = json.load(f)

            prev_line = previous_metrics.get("line_coverage", 0.0)
            prev_branch = previous_metrics.get("branch_coverage", 0.0)
            prev_mutation = previous_metrics.get("mutation_score", 0.0)

            # Una métrica mejora si estaba bajo el mínimo y ahora aumenta
            mejora_line = prev_line < MIN_LINE_COVERAGE and final_line_cov > prev_line

            mejora_branch = (
                prev_branch < MIN_BRANCH_COVERAGE and final_branch_cov > prev_branch
            )

            mejora_mutation = (
                prev_mutation < MIN_MUTATION_SCORE
                and final_mutation_score > prev_mutation
            )

            mejora_minimo = mejora_line or mejora_branch or mejora_mutation

            # Las métricas que ya estaban sobre el mínimo no pueden caer bajo él
            line_se_mantuvo = (
                prev_line < MIN_LINE_COVERAGE or final_line_cov >= MIN_LINE_COVERAGE
            )

            branch_se_mantuvo = (
                prev_branch < MIN_BRANCH_COVERAGE
                or final_branch_cov >= MIN_BRANCH_COVERAGE
            )

            mutation_se_mantuvo = (
                prev_mutation < MIN_MUTATION_SCORE
                or final_mutation_score >= MIN_MUTATION_SCORE
            )

            # Guardar si:
            # 1. Se mejoró alguna métrica que estaba bajo el mínimo.
            # 2. Ninguna métrica que ya cumplía el mínimo pasó a incumplirlo.
            if (
                mejora_minimo
                and line_se_mantuvo
                and branch_se_mantuvo
                and mutation_se_mantuvo
            ):
                should_overwrite = True
            else:
                should_overwrite = False

        except Exception as e:
            print(
                f"[Agent Warning] No se pudo leer metrics.json previo, se sobrescribe igual: {e}"
            )

    if should_overwrite:
        write_test_file(test_file_path, final_code)
        save_metrics_json(
            output_folder, final_line_cov, final_branch_cov, final_mutation_score
        )

    print(
        f"\n[Agent] Tiempo total de ejecución: {MAX_TIME_BUDGET - timer.time_left():.1f}s"
    )
    print(f"[Agent] Suite de tests final: {test_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agente basado en LLM para generación iterativa de tests."
    )

    parser.add_argument(
        "ruta_archivo",
        type=str,
        help="Ruta relativa al archivo de código fuente (ej. Proyectos_Publicos/bridge/base.py)",
    )
    parser.add_argument(
        "output_folder",
        type=str,
        help="Directorio general donde se guardarán los resultados (ej. Resultados)",
    )

    args = parser.parse_args()

    main(args.ruta_archivo, args.output_folder)
