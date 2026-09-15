import re
import sys
import subprocess
import json
import os

def clean_llm_code(response_text: str) -> str:
    """Extrae código de Python de la respusta del LLM (quita bloques de markdown)"""
    match = re.search(r"```python\s*(.*?)\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return response_text.replace("```", "").strip()

def get_env_with_pythonpath(project_root: str = ".") -> dict:
    """Configura las variables de entorno agregando la raíz al PYTHONPATH para evitar ModuleNotFoundError."""
    env = os.environ.copy()
    abs_root = os.path.abspath(project_root)
    env["PYTHONPATH"] = f"{abs_root}{os.pathsep}{env.get('PYTHONPATH', '')}"
    return env

def run_pytest(test_file_path: str, project_root: str = ".") -> tuple[bool, str]:
    """Ejecuta pytest sobre el archivo de pruebas y retorna (éxito, logs)."""
    env = get_env_with_pythonpath(project_root)
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=short", test_file_path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=15)
        success = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Error: Ejecución de pytest excedió el tiempo límite (Timeout)."
    except Exception as e:
        return False, f"Error ejecutando pytest: {e}"

def measure_coverage(test_file_path: str, target_file_path: str, output_folder: str) -> tuple[float, float, str]:
    """
    Mide Line Coverage y Branch Coverage usando 'coverage'.
    Retorna: (line_coverage, branch_coverage, informe_detalle_para_prompt)
    """
    coverage_file = os.path.join(output_folder, ".coverage")
    json_report = os.path.join(output_folder, "coverage.json")
    env = get_env_with_pythonpath(".")

    # 1. Ejecutar coverage run
    cmd_run = [
        sys.executable, "-m", "coverage", "run",
        f"--data-file={coverage_file}",
        "--branch",
        "-m", "pytest", test_file_path
    ]
    subprocess.run(cmd_run, capture_output=True, text=True, env=env, timeout=20)

    # 2. Generar reporte JSON
    cmd_json = [
        sys.executable, "-m", "coverage", "json",
        f"--data-file={coverage_file}",
        "-o", json_report
    ]
    subprocess.run(cmd_json, capture_output=True, text=True, env=env, timeout=10)

    line_cov, branch_cov = 0.0, 0.0
    missing_lines_info = ""

    # 3. Leer y parsear el reporte JSON
    if os.path.exists(json_report):
        try:
            with open(json_report, "r", encoding="utf-8") as f:
                data = json.load(f)

            target_abs = os.path.abspath(target_file_path)
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
                    missing_lines_info += f"\nRamas no cubiertas (origen, destino): {missing_branches}"

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
    Ejecuta Cosmic Ray para calcular el Mutation Score.
    Retorna un valor entre 0.0 y 1.0.
    """
    session_db = os.path.join(output_folder, "session.sqlite")
    env = get_env_with_pythonpath(".")

    # Limpiar base de datos previa si existe
    if os.path.exists(session_db):
        try:
            os.remove(session_db)
        except OSError:
            pass

    try:
        # Step 1: Inicializar Cosmic Ray
        cmd_init = ["cosmic-ray", "init", config_file, session_db]
        res_init = subprocess.run(cmd_init, capture_output=True, text=True, env=env, timeout=10)
        if res_init.returncode != 0:
            print(f"[Tools Warning] Cosmic Ray init falló: {res_init.stderr}")
            return 0.50  # Estimación de respaldo si falla la inicialización

        # Step 2: Ejecutar mutaciones (con un tiempo máximo de 25 segundos)
        cmd_exec = ["cosmic-ray", "exec", config_file, session_db]
        subprocess.run(cmd_exec, capture_output=True, text=True, env=env, timeout=25)

        # Step 3: Obtener resumen/score
        cmd_summary = ["cosmic-ray", "summary", session_db]
        res_summary = subprocess.run(cmd_summary, capture_output=True, text=True, env=env, timeout=10)
        
        output = res_summary.stdout
        
        # Parsear la salida de Cosmic Ray buscando 'survival rate' o 'killed' / 'total'
        survival_match = re.search(r"survival rate:\s*([\d\.]+)%", output, re.IGNORECASE)
        if survival_match:
            survival_rate = float(survival_match.group(1)) / 100.0
            mutation_score = max(0.0, 1.0 - survival_rate)
            return round(mutation_score, 2)

        # Parseo alternativo por conteo directo de mutantes
        killed_match = re.search(r"killed:\s*(\d+)", output, re.IGNORECASE)
        total_match = re.search(r"total:\s*(\d+)", output, re.IGNORECASE)
        if killed_match and total_match:
            killed = int(killed_match.group(1))
            total = int(total_match.group(1))
            return round(killed / total, 2) if total > 0 else 1.0

    except subprocess.TimeoutExpired:
        print("[Tools Warning] Cosmic Ray excedió el tiempo límite (Timeout). Retornando estimación parcial.")
    except Exception as e:
        print(f"[Tools Warning] Error ejecutando Cosmic Ray: {e}")

    # Si la ejecución de mutantes falla o excede el tiempo, retornar valor neutro/respaldo
    return 0.50