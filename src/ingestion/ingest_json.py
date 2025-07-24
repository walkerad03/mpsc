import json
import logging
from collections import defaultdict
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from src.ingestion.dispatcher import route_observation

logger = logging.getLogger(__name__)


def ingest_json_dataset(raw_dir: Path) -> dict[str, pd.DataFrame]:
    if not raw_dir.exists():
        raise FileNotFoundError(f"{raw_dir} does not exist.")

    all_frames: dict[str, list[pd.DataFrame]] = defaultdict(list)

    files = list(raw_dir.glob("*.json"))

    logger.info(f"Found {len(files)} JSON files")

    for file_path in tqdm(files, desc="Parsing patient files", unit="file"):
        try:
            with file_path.open("r", encoding="utf-8") as f:
                patient_entries = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {file_path.name}: {e}")
            continue

        for param_set in patient_entries:
            patient_id = param_set.get("PatientId")
            start_time = param_set.get("StartTime")
            parameters = param_set.get("Parameters", [])

            for param in parameters:
                try:
                    obs_type, df = route_observation(param, patient_id, start_time)
                    all_frames[obs_type].append(df)
                except ValueError as e:
                    continue
                    logger.warning(f"Skipping param: {e}")

    combined = {
        obs: pd.concat(dfs, ignore_index=True) for obs, dfs in all_frames.items()
    }

    return combined
