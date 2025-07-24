import datetime as dt
import os

import hero_fsdb
import pandas as pd
from tqdm import tqdm


def calculate_demographics(
    patientJSONDir: str, fluidIntakeRowIDs, output_dir: str
) -> None:
    outputList = list()

    with os.scandir(patientJSONDir) as it:
        for inputFileName in tqdm(it, desc="Demographics"):
            if ".json" not in inputFileName.name:
                continue

            db = hero_fsdb.FileDB(os.path.join(patientJSONDir, inputFileName.name))
            db.read_file()

            maxDOB = "19010101"
            gestationalAgeWeeks = "0"
            birthWeightGrams = "0"
            patientSex = "U"

            maxData = dt.datetime.fromisoformat("1901-01-01")
            minData = dt.datetime.fromisoformat("2222-02-02")

            maxFluid = dt.datetime.fromisoformat("1901-01-01")
            minFluid = dt.datetime.fromisoformat("2222-02-02")

            for ps in db.ParameterSets:
                for p in ps.Parameters:
                    if p.Observation == "YearOfBirth":
                        if p.Value > maxDOB:
                            maxDOB = p.Value
                    elif p.Observation == "Sex":
                        patientSex = p.Value
                    elif (
                        p.Observation
                        == "PEDIATRIC BIRTH WEIGHT (OZ)^PEDIATRIC BIRTH WEIGHT (OZ)"
                    ):
                        birthWeightGrams = str(
                            round(float(p.Value) * 28.3495)
                        )  # convert oz to grams
                    elif (
                        p.Observation
                        == "PEDIATRIC GESTATION AGE (WEEKS)^PEDIATRIC GESTATION AGE (WEEKS)"
                    ):
                        gestationalAgeWeeks = p.Value
                    elif (
                        p.Observation.replace("&", "^").split("^")[0]
                        in fluidIntakeRowIDs
                    ):
                        if ps.StartTime > maxFluid:
                            maxFluid = ps.StartTime
                        if ps.StartTime < minFluid:
                            minFluid = ps.StartTime
                if ps.StartTime is None:
                    continue
                if ps.StartTime > maxData:
                    maxData = ps.StartTime
                if ps.StartTime < minData:
                    minData = ps.StartTime

            rowDict = {
                "ID": inputFileName.name.split(".")[0],
                "DOB": f"{maxDOB}-01-01",
                "GA": gestationalAgeWeeks,
                "BW": birthWeightGrams,
                "Sex": patientSex,
                "DataStart": minData,
                "DataEnd": maxData,
                "FluidStart": minFluid,
                "FluidEnd": maxFluid,
            }

            outputList.append(rowDict)

    outputDF = pd.DataFrame(outputList)
    outputDF.to_csv(os.path.join(output_dir, "Demographics.csv"), index=False)


if __name__ == "__main__":
    os.chdir("/home/walkerdavis/projects/mpsc")
    patientJSONDir = "./data/raw"
    output_dir = "./data/processed"

    with open("scripts/FluidIntakeRowIDs.txt", "r") as fluidIntakeRowIDsFile:
        fluidIntakeRowIDs = fluidIntakeRowIDsFile.read().splitlines()

    calculate_demographics(patientJSONDir, fluidIntakeRowIDs, output_dir)
