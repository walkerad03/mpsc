from pathlib import Path

from src.pipeline import run_pipeline

PROJECT_ROOT = Path(__file__).resolve().parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
FEATURE_DIR = PROJECT_ROOT / "data" / "features"


def main() -> None:
    run_pipeline(raw_data_dir=RAW_DATA_DIR, feature_output_dir=FEATURE_DIR)


if __name__ == "__main__":
    main()
