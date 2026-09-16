import json
import os
import time

class ExecutionTimer:
    """Clase para asegurar que la ejecución no supere el límite del Time Budget."""
    def __init__(self, max_seconds: int = 110):
        self.start_time = time.time()
        self.max_seconds = max_seconds

    def time_left(self) -> float:
        elapsed = time.time() - self.start_time
        return max(0.0, self.max_seconds - elapsed)

    def is_expired(self) -> bool:
        return self.time_left() <= 0


def save_metrics_json(output_folder: str, line_cov: float, branch_cov: float, mutation_score: float):
    """Guarda las métricas finales en el formato JSON estricto requerido."""
    os.makedirs(output_folder, exist_ok=True)
    metrics_path = os.path.join(output_folder, "metrics.json")
    
    data = {
        "line_coverage": round(float(line_cov), 2),
        "branch_coverage": round(float(branch_cov), 2),
        "mutation_score": round(float(mutation_score), 2)
    }
    
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print(f"[Utils] Métricas exportadas exitosamente en {metrics_path}")