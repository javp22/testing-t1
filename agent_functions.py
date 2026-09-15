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
    # Si no usa bloques markdown, remover triples comillas genéricas si existen
    return response_text.replace("```", "").strip()

def run_pytest(test_file_path: str) -> tuple[bool, str]:
    """Ejecuta pytest sobre el archivo de pruebas y retorna (éxito, logs)."""
    cmd = [sys.executable, "-m", "pytest", test_file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    success = result.returncode == 0
    output = result.stdout + "\n" + result.stderr
    return success, output

def measure_coverage(test_file_path: str, target_file_path: str, output_folder: str) -> tuple[float, float, str]:
    """
    Mide Line Coverage y Branch Coverage usando la librería 'coverage'.
    Retorna (line_coverage, branch_coverage, informe_texto).
    """
    coverage_file = os.path.join(output_folder, ".coverage")
    json_report = os.path.join(output_folder, "coverage.json")

    # 1. Ejecutar coverage
    cmd_run = [
        sys.executable, "-m", "coverage", "run",
        f"--data-file={coverage_file}",
        "--branch",
        "-m", "pytest", test_file_path
    ]
    subprocess.run(cmd_run, capture_output=True, text=True)

    # 2. Exportar reporte en formato JSON
    cmd_json = [
        sys.executable, "-m", "coverage", "json",
        f"--data-file={coverage_file}",
        "-o", json_report
    ]
    subprocess.run(cmd_json, capture_output=True, text=True)

    # 3. Leer métricas
    line_cov, branch_cov = 0.0, 0.0
    if os.path.exists(json_report):
        try:
            with open(json_report, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Buscar métricas correspondientes al archivo objetivo
            target_abs = os.path.abspath(target_file_path)
            files_data = data.get("files", {})
            
            file_stats = None
            for fname, stats in files_data.items():
                if os.path.abspath(fname) == target_abs or fname.endswith(os.path.basename(target_file_path)):
                    file_stats = stats
                    break

            if file_stats:
                summary = file_stats.get("summary", {})
                num_statements = summary.get("num_statements", 1)
                covered_statements = summary.get("covered_lines", 0)
                num_branches = summary.get("num_branches", 0)
                covered_branches = summary.get("covered_branches", 0)

                line_cov = covered_statements / num_statements if num_statements > 0 else 1.0
                branch_cov = covered_branches / num_branches if num_branches > 0 else 1.0
        except Exception as e:
            print(f"Error parseando coverage.json: {e}")

    # Reporte básico legible para el prompt de mejora
    report_summary = f"Line Coverage: {line_cov*100:.1f}%, Branch Coverage: {branch_cov*100:.1f}%"
    return line_cov, branch_cov, report_summary

def measure_mutation(test_file_path: str, target_file_path: str, output_folder: str) -> float:
    """
    Mide Mutation Score utilizando Cosmic Ray.
    """
    # NOTA: Debes adaptar los comandos según la configuración de cosmic-ray.toml del proyecto
    # Si cosmic-ray toma tiempo, puedes calcular una estimación o ejecutarlo rápido.
    mutation_score = 0  # Valor por defecto si no se logra ejecutar a tiempo
    try:
        # Ejemplo de comando genérico si cosmic-ray está configurado:
        # subprocess.run(["cosmic-ray", "exec", "cosmic-ray.toml", ...], capture_output=True)
        pass
    except Exception as e:
        print(f"Advertencia midiendo mutantes: {e}")
    
    return mutation_score