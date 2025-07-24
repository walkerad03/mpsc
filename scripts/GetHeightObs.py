import os

import hero_fsdb
import pandas as pd
from tqdm import tqdm


def calculate_height_obs(patientJSONDir: str, output_dir: str) -> None:
    outputList = list()

    with os.scandir(patientJSONDir) as it:
        for inputFileName in tqdm(it, desc="Height Observations"):
            if ".json" not in inputFileName.name:
                continue
            if "T.json" in inputFileName.name:
                continue

            db = hero_fsdb.FileDB(os.path.join(patientJSONDir, inputFileName.name))
            db.read_file()

            for ps in db.ParameterSets:
                for p in ps.Parameters:
                    if p.Observation == "3041101^Height^LCHEROFS":
                        rowDict = {
                            "ID": inputFileName.name.split(".")[0],
                            "DateTime": ps.StartTime,
                            "OBX": p.Observation,
                            "Value": p.Value,
                            "Unit": p.Unit,
                            "Text": p.Text,
                        }
                        outputList.append(rowDict)

    outputDF = pd.DataFrame(outputList)
    outputDF.to_csv(os.path.join(output_dir, "HeightObservations.csv"), index=False)
