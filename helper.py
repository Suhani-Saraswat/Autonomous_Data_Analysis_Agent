from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / "datasets"

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

def load_dataframe(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")

def discover_demo_dataset() -> Path:
    candidates = [
        DATASET_DIR / "superstore_fixed_benchmark_10000plus.csv",
        DATASET_DIR / "superstore_live_stream_10000plus.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("No demo dataset found in datasets/")

def clean_scalar(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value
