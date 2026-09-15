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
    Mide Mutation Score utilizando Cosmic Ray con reporte detallado y parseo de respaldo.
    """
    abs_output = os.path.abspath(output_folder)
    os.makedirs(abs_output, exist_ok=True)

    # Normalizar rutas con barras inclinadas para compatibilidad con TOML en Windows/Linux
    rel_target = os.path.relpath(os.path.abspath(target_file_path), PROJECT_ROOT).replace("\\", "/")
    rel_test = os.path.relpath(os.path.abspath(test_file_path), PROJECT_ROOT).replace("\\", "/")

    temp_config_path = os.path.join(abs_output, "cosmic-ray-run.toml")
    config_content = f"""[cosmic-ray]
module-path = "{rel_target}"
timeout = 3.0
excluded-modules = []
test-command = "{sys.executable} -m pytest -q --tb=no {rel_test}"

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
        # 1. Inicializar Cosmic Ray (Genera la lista de mutantes)
        cmd_init = ["cosmic-ray", "init", temp_config_path, session_db]
        res_init = subprocess.run(cmd_init, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT, timeout=15)

        if res_init.returncode != 0:
            print(f"[Mutation Warning] Cosmic Ray init falló:\n{res_init.stderr.strip() or res_init.stdout.strip()}")
            return 0.0

        # 2. Ejecutar pruebas contra cada mutante
        cmd_exec = ["cosmic-ray", "exec", temp_config_path, session_db]
        try:
            subprocess.run(cmd_exec, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT, timeout=50)
        except subprocess.TimeoutExpired:
            print("[Mutation Warning] Tiempo límite alcanzado. Evaluando mutantes procesados...")

        # 3. Obtener el resumen de resultados
        cmd_summary = ["cosmic-ray", "summary", session_db]
        res_summary = subprocess.run(cmd_summary, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT, timeout=10)
        output = res_summary.stdout + "\n" + res_summary.stderr

        # Extraer métricas con expresiones regulares
        killed_match = re.search(r"killed:\s*(\d+)", output, re.IGNORECASE)
        survived_match = re.search(r"survived:\s*(\d+)", output, re.IGNORECASE)
        total_match = re.search(r"(?:total jobs|total):\s*(\d+)", output, re.IGNORECASE)

        killed = int(killed_match.group(1)) if killed_match else 0
        survived = int(survived_match.group(1)) if survived_match else 0
        total = int(total_match.group(1)) if total_match else 0

        # Respando: Consulta directa a la base de datos SQLite si el parser de texto falla
        if total == 0 and os.path.exists(session_db):
            try:
                import sqlite3
                conn = sqlite3.connect(session_db)
                cursor = conn.cursor()
                
                cursor.execute("SELECT count(*) FROM work_items")
                total = cursor.fetchone()[0]

                cursor.execute("SELECT count(*) FROM work_items WHERE test_outcome LIKE '%KILLED%' OR worker_outcome LIKE '%NORMAL%' AND test_outcome NOT LIKE '%SURVIVED%'")
                killed = cursor.fetchone()[0]

                cursor.execute("SELECT count(*) FROM work_items WHERE test_outcome LIKE '%SURVIVED%'")
                survived = cursor.fetchone()[0]

                conn.close()
            except Exception:
                pass

        if total == 0:
            print(f"[Mutation Warning] No se generaron mutantes para '{rel_target}'. Verifica que la ruta apunte a un archivo Python con código ejecutable.")
            return 0.0

        # Calcular Mutation Score: (Mutantes Eliminados / Total de Mutantes)
        mutation_score = round(killed / total, 2)

        # Trazabilidad extendida en consola
        print(f"\n[Mutation Metrics] Resumen para: {rel_target}")
        print(f" ├─ Mutantes Totales Generados : {total}")
        print(f" ├─ Mutantes Eliminados (Killed): {killed}")
        print(f" ├─ Mutantes Sobrevivientes      : {survived}")
        print(f" └─ Mutation Score Final        : {mutation_score * 100:.1f}% ({killed}/{total})\n")

        return mutation_score

    except FileNotFoundError:
        print("[Mutation Warning] El comando 'cosmic-ray' no está instalado en el PATH.")
    except Exception as e:
        print(f"[Mutation Warning] Error ejecutando Cosmic Ray: {e}")

    return 0.0