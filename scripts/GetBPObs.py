import os

import hero_fsdb
import pandas as pd
from tqdm import tqdm
from typing import Optional, Union


def calculate(patientJSONDir: str, output_dir: str) -> None:
    outputList: list[dict[str, Optional[Union[str, int]]]] = list()

    with os.scandir(patientJSONDir) as it:
        for inputFileName in tqdm(it, desc="Blood Pressure"):
            if ".json" not in inputFileName.name:
                continue
            if "T.json" in inputFileName.name:
                continue

            db = hero_fsdb.FileDB(os.path.join(patientJSONDir, inputFileName.name))
            db.read_file()

            for ps in db.ParameterSets:
                rowDict: dict[str, Optional[Union[str, int]]] = {}
                saveThis = False
                for p in ps.Parameters:
                    if p.Observation == "3040501^BP^LCHEROFS":
                        rowDict["ID"] = inputFileName.name.split(".")[0]
                        rowDict["DateTime"] = ps.StartTime
                        rowDict["OBX"] = p.Observation
                        rowDict["Value"] = p.Value
                        rowDict["Unit"] = p.Unit
                        rowDict["Text"] = p.Text

                        saveThis = True
                if saveThis:
                    outputList.append(rowDict)

    outputDF = pd.DataFrame(outputList)
    outputDF.to_csv(
        os.path.join(output_dir, "BPObservations.csv"), index=False
    )


if __name__ == "__main__":
    os.chdir("/home/walkerdavis/projects/mpsc")
    patientJSONDir = "./data/raw"
    output_dir = "./data/processed"

    calculate(patientJSONDir, output_dir)
