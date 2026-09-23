import json
from pathlib import Path

RESULTS_DIR = Path("Results")
OUTPUT_FILE = RESULTS_DIR / "metrics_average.json"


def main():
    metrics_files = list(RESULTS_DIR.rglob("metrics.json"))

    # Evitar incluir el archivo de promedio si se vuelve a ejecutar
    metrics_files = [path for path in metrics_files if path != OUTPUT_FILE]

    if not metrics_files:
        print("No se encontraron archivos metrics.json.")
        return

    totals = {}
    counts = {}

    for metrics_file in metrics_files:
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                metrics = json.load(f)

            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    totals[key] = totals.get(key, 0) + value
                    counts[key] = counts.get(key, 0) + 1

        except (json.JSONDecodeError, OSError) as e:
            print(f"Error leyendo {metrics_file}: {e}")

    averages = {key: totals[key] / counts[key] for key in totals}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(averages, f, indent=4)

    print(f"Se procesaron {len(metrics_files)} archivos.")
    print(f"Archivo generado: {OUTPUT_FILE}")
    print(json.dumps(averages, indent=4))


if __name__ == "__main__":
    main()
