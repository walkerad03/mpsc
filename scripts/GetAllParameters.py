import os

import src.hero_fsdb as hero_fsdb
import pandas as pd
from tqdm import tqdm


def get_all_params(patientJSONDir: str, output_dir: str) -> None:
    param_list: dict[str, int] = {}

    with os.scandir(patientJSONDir) as it:
        for inputFileName in tqdm(it, desc="Fetching Parameters"):
            if ".json" not in inputFileName.name:
                continue
            if "T.json" in inputFileName.name:
                continue

            db = hero_fsdb.FileDB(os.path.join(patientJSONDir, inputFileName.name))
            db.read_file()

            for ps in db.ParameterSets:
                for p in ps.Parameters:
                    if p.Observation in param_list:
                        param_list[p.Observation] += 1
                    else:
                        param_list[p.Observation] = 1

            if len(param_list) == 0:
                return

    df = pd.DataFrame(list(param_list.items()), columns=["parameter", "count"])
    sorted_df = df.sort_values(by="count", ascending=False)

    output_path = os.path.join(output_dir, "param_list.csv")
    sorted_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    patientJSONDir = "./data/raw"
    output_dir = "./data"

    get_all_params(patientJSONDir, output_dir)
