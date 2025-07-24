import os

import hero_fsdb
import pandas as pd
from tqdm import tqdm


def calculate_spo2_obs(patientJSONDir: str, output_dir: str) -> None:
    outputList = list()

    with os.scandir(patientJSONDir) as it:
        for inputFileName in tqdm(it, desc="SPO2 Observations"):
            if ".json" not in inputFileName.name:
                continue
            if "T.json" in inputFileName.name:
                continue

            db = hero_fsdb.FileDB(os.path.join(patientJSONDir, inputFileName.name))
            db.read_file()

            for ps in db.ParameterSets:
                rowDict = {}
                saveThis = False
                for p in ps.Parameters:
                    if p.Observation == "3041001^SpO2^LCHEROFS":
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
        os.path.join(output_dir, "SPO2Obs.csv"), index=False
    )

if __name__ == "__main__":
    os.chdir("/home/walkerdavis/projects/mpsc")
    patientJSONDir = "./data/raw"
    output_dir = "./data/processed"

    calculate_spo2_obs(patientJSONDir, output_dir)