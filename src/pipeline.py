import logging
from pathlib import Path

import pandas as pd

from src.ingestion.ingest_json import ingest_json_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_pipeline(raw_data_dir: Path, feature_output_dir: Path):
    logger.info("Starting JSON ingestion...")
    parsed_dataframes = ingest_json_dataset(raw_data_dir)
    logger.info(f"Parsed {len(parsed_dataframes)} entry types.")

    feature_output_dir.mkdir(parents=True, exist_ok=True)

    for entry_type, df in parsed_dataframes.items():
        output_path = feature_output_dir / f"{entry_type}.csv"
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {entry_type} to {output_path}")
    logger.info("Saved all dataframes to csv")

    if "EnteralFeed" in parsed_dataframes:
        df = parsed_dataframes["EnteralFeed"]
        value_counts = df["Label"].value_counts()
        label_counts = pd.DataFrame(
            {"fluid_label": value_counts.index, "count": value_counts.values}
        )
        label_counts.to_csv(feature_output_dir / "EnteralFeedLabels.csv", index=False)
