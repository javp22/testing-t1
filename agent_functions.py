import json
import os
import re
import subprocess
import sys

# Definir la raíz absoluta del proyecto según la ubicación de este archivo
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def clean_llm_code(response_text: str) -> str:
    """Extrae código de Python de la respuesta del LLM (quita bloques de markdown)."""
    match = re.search(r"```python\s*(.*?)\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return response_text.replace("```", "").strip()


def get_env_with_pythonpath(project_root: str = PROJECT_ROOT) -> dict:
    """Configura las variables de entorno agregando la raíz y Public_Proyects al PYTHONPATH."""
    env = os.environ.copy()
    abs_root = os.path.abspath(project_root)
    public_projects_path = os.path.abspath(os.path.join(abs_root, "Public_Proyects"))

    pythonpath_entries = [abs_root, public_projects_path]
    if "PYTHONPATH" in env and env["PYTHONPATH"]:
        pythonpath_entries.append(env["PYTHONPATH"])

    env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)
    return env


def run_pytest(test_file_path: str, project_root: str = PROJECT_ROOT) -> tuple[bool, str]:
    """Ejecuta pytest sobre el archivo de pruebas y retorna (éxito, logs)."""
    env = get_env_with_pythonpath(project_root)
    abs_test_path = os.path.abspath(test_file_path)
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=short", abs_test_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=project_root, timeout=15)
        success = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Error: Ejecución de pytest excedió el tiempo límite (Timeout)."
    except Exception as e:
        return False, f"Error ejecutando pytest: {e}"


def measure_coverage(test_file_path: str, target_file_path: str, output_folder: str) -> tuple[float, float, str]:
    """Mide Line Coverage y Branch Coverage usando 'coverage'."""
    abs_output = os.path.abspath(output_folder)
    os.makedirs(abs_output, exist_ok=True)

    coverage_file = os.path.join(abs_output, ".coverage")
    json_report = os.path.join(abs_output, "coverage.json")
    env = get_env_with_pythonpath(PROJECT_ROOT)

    target_abs = os.path.abspath(target_file_path)
    test_abs = os.path.abspath(test_file_path)

    # 1. Ejecutar coverage run acotando al archivo objetivo
    cmd_run = [
        sys.executable, "-m", "coverage", "run",
        f"--data-file={coverage_file}",
        f"--include={target_abs}",
        "--branch",
        "-m", "pytest", test_abs
    ]
    res_run = subprocess.run(cmd_run, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT, timeout=20)

    if res_run.returncode != 0:
        print(f"\n[Coverage Warning] Fallo en 'coverage run':\n{res_run.stdout}\n{res_run.stderr}")

    # 2. Generar reporte JSON
    cmd_json = [
        sys.executable, "-m", "coverage", "json",
        f"--data-file={coverage_file}",
        "-o", json_report
    ]
    res_json = subprocess.run(cmd_json, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT, timeout=10)

    if res_json.returncode != 0:
        print(f"\n[Coverage Warning] Fallo en 'coverage json':\n{res_json.stderr}")

    line_cov, branch_cov = 0.0, 0.0
    missing_lines_info = ""

    # 3. Leer y parsear el reporte JSON
    if os.path.exists(json_report):
        try:
            with open(json_report, "r", encoding="utf-8") as f:
                data = json.load(f)

            files_data = data.get("files", {})

            file_stats = None
            for fname, stats in files_data.items():
                if os.path.abspath(fname) == target_abs or fname.endswith(os.path.basename(target_file_path)):
                    file_stats = stats
                    break

            if file_stats:
                summary = file_stats.get("summary", {})
                num_statements = summary.get("num_statements", 0)
                covered_statements = summary.get("covered_lines", 0)
                num_branches = summary.get("num_branches", 0)
                covered_branches = summary.get("covered_branches", 0)

                line_cov = covered_statements / num_statements if num_statements > 0 else 1.0
                branch_cov = covered_branches / num_branches if num_branches > 0 else 1.0

                missing_lines = file_stats.get("missing_lines", [])
                missing_branches = file_stats.get("missing_branches", [])

                if missing_lines:
                    missing_lines_info += f"\nLíneas no cubiertas: {missing_lines}"
                if missing_branches:
                    missing_lines_info += f"\nRamas no cubiertas: {missing_branches}"

        except Exception as e:
            print(f"[Tools] Error al leer reporte de cobertura: {e}")

    report_summary = (
        f"Line Coverage: {line_cov * 100:.1f}%\n"
        f"Branch Coverage: {branch_cov * 100:.1f}%"
        f"{missing_lines_info}"
    )
    return line_cov, branch_cov, report_summary

def measure_mutation(test_file_path: str, target_file_path: str, output_folder: str, config_file: str = "cosmic-ray.toml") -> float:
    """
    Mide Mutation Score ejecutando Cosmic Ray y procesando la salida oficial
    del comando 'cr-rate' vía subprocess.
    """
    abs_output = os.path.abspath(output_folder)
    os.makedirs(abs_output, exist_ok=True)

    # Normalizar rutas con barras inclinadas (compatibilidad Windows/Linux)
    python_exec = sys.executable.replace("\\", "/")
    rel_target = os.path.relpath(os.path.abspath(target_file_path), PROJECT_ROOT).replace("\\", "/")
    rel_test = os.path.relpath(os.path.abspath(test_file_path), PROJECT_ROOT).replace("\\", "/")

    temp_config_path = os.path.join(abs_output, "cosmic-ray-run.toml")

    # Se agrega -x a pytest para abortar la suite en cuanto un test falle contra el mutante
    config_content = f"""[cosmic-ray]
module-path = "{rel_target}"
timeout = 3.0
excluded-modules = []
test-command = "{python_exec} -m pytest -x -q --tb=no {rel_test}"

[cosmic-ray.distributor]
name = "local"
"""
    with open(temp_config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    session_db = os.path.join(abs_output, "session.sqlite")
    env = get_env_with_pythonpath(PROJECT_ROOT)

    if os.path.exists(session_db):
        try:
            os.remove(session_db)
        except OSError:
            pass

    try:
        # 1. Inicializar Cosmic Ray
        cmd_init = ["cosmic-ray", "init", temp_config_path, session_db]
        res_init = subprocess.run(cmd_init, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT, timeout=15)

        if res_init.returncode != 0:
            print(f"[Mutation Warning] Cosmic Ray init falló:\n{res_init.stderr.strip() or res_init.stdout.strip()}")
            return 0.0

        # 2. Ejecutar mutantes
        cmd_exec = ["cosmic-ray", "exec", temp_config_path, session_db]
        try:
            subprocess.run(cmd_exec, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT, timeout=40)
        except subprocess.TimeoutExpired:
            print("[Mutation Warning] Tiempo límite alcanzado en 'exec'. Procesando resultados parciales mediante cr-rate...")

        # 3. Calcular Mutation Score mediante la herramienta oficial 'cr-rate'
        mutation_score = 0.0
        if os.path.exists(session_db):
            cmd_rate = ["cr-rate", session_db]
            res_rate = subprocess.run(cmd_rate, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT, timeout=15)

            if res_rate.returncode == 0:
                stdout_text = res_rate.stdout.strip()

                # cr-rate reporta habitualmente el "Survival rate: X.XX%"
                match_survival = re.search(r"Survival rate:\s*([\d\.]+)%", stdout_text, re.IGNORECASE)

                if match_survival:
                    survival_rate = float(match_survival.group(1))
                    # Mutation score (porcentaje de mutantes eliminados) = 100% - Survival rate
                    mutation_score = round(max(0.0, (100.0 - survival_rate) / 100.0), 2)
                else:
                    # Búsqueda fallback por si la salida reporta un score directo o flotante
                    match_score = re.search(r"([\d\.]+)", stdout_text)
                    if match_score:
                        val = float(match_score.group(1))
                        mutation_score = round(val / 100.0 if val > 1.0 else val, 2)

                print(f"\n[Mutation Metrics] Resumen para: {rel_target}")
                print(f" ├─ Salida cr-rate      : {stdout_text}")
                print(f" └─ Mutation Score Final: {mutation_score * 100:.1f}%\n")
            else:
                print(f"[Mutation Warning] cr-rate no pudo procesar la sesión:\n{res_rate.stderr.strip()}")

        return mutation_score

    except FileNotFoundError:
        print("[Mutation Warning] 'cosmic-ray' o 'cr-rate' no están disponibles en el PATH.")
    except Exception as e:
        print(f"[Mutation Warning] Error ejecutando medición de mutación: {e}")

    return 0.0