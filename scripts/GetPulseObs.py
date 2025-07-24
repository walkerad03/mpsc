import os

import hero_fsdb
import pandas as pd


os.chdir(os.path.join("/", "home", "walkerdavis", "projects", "mpsc"))
patientJSONDir = os.path.join(".", "data", "raw")
output_dir = "./data/processed"


with open(
    os.path.join("scripts", "FluidIntakeRowIDs.txt"), "r"
) as fluidIntakeRowIDsFile:
    fluidIntakeRowIDs = fluidIntakeRowIDsFile.read().splitlines()

outputList = list()

with os.scandir(patientJSONDir) as it:
    for inputFileName in it:
        if ".json" not in inputFileName.name:
            continue
        if "T.json" in inputFileName.name:
            continue

        print(inputFileName.name)

        db = hero_fsdb.FileDB(os.path.join(patientJSONDir, inputFileName.name))
        db.read_file()

        for ps in db.ParameterSets:
            for p in ps.Parameters:
                if p.Observation == "3040801^Pulse^LCHEROFS":
                    rowDict = {
                        "ID": inputFileName.name.split(".")[0],
                        "DateTime": ps.StartTime,
                        "OBX": p.Observation,
                        "Value": p.Value,
                        "Unit": p.Unit,
                        "Text": p.Text,
                    }
                    outputList.append(rowDict)

print("Writing output file")
outputDF = pd.DataFrame(outputList)
outputDF.to_csv(os.path.join(output_dir, "PulseObservations.csv"), index=False)

print("Finished")
