import os

import src.hero_fsdb as hero_fsdb
import pandas as pd
from tqdm import tqdm


def calculate_entral_feed_obs(patientJSONDir: str, output_dir: str) -> None:
    labelCountDict = {}

    with os.scandir(patientJSONDir) as it:
        for inputFileName in tqdm(it, desc="Entral Feed Observations"):
            if ".json" not in inputFileName.name:
                continue
            if "T.json" in inputFileName.name:
                continue

            db = hero_fsdb.FileDB(os.path.join(patientJSONDir, inputFileName.name))
            db.read_file()

            for ps in db.ParameterSets:
                for p in ps.Parameters:
                    rowID = p.Observation.replace("&", "^").split("^")[0]
                    match rowID:
                        case "304452001" | "304451901":  # | "30460222601":
                            fluidLabel = p.Observation.split(" Volume (mL)-")[1].split(
                                "^"
                            )[0]
                        case "30460222601":
                            fluidLabel = p.Observation.split(" (mL)-")[1].split("^")[0]
                        case _:
                            continue

                    if fluidLabel in labelCountDict:
                        labelCountDict[fluidLabel] += 1
                    else:
                        labelCountDict[fluidLabel] = 1

    pd.DataFrame.from_dict(data=labelCountDict, orient="index").to_csv(
        os.path.join(output_dir, "EnterFeedLabels.csv"), header=False
    )
