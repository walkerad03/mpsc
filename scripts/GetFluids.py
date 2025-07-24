import datetime as dt
import glob
import os

import hero_fsdb
import pandas as pd

os.chdir("/home/walkerdavis/projects/mpsc")

with open("scripts/FluidOutputRowIDs.txt", "r") as fluidOutputRowIDsFile:
    fluidOutputRowIDs = fluidOutputRowIDsFile.read().splitlines()

with open("scripts/FluidIntakeRowIDs.txt", "r") as fluidIntakeRowIDsFile:
    fluidIntakeRowIDs = fluidIntakeRowIDsFile.read().splitlines()

# set the path to the JSON directory...
jsonFileDirectory = "./data/raw"


# let's get the n most recent patients...
flowsheetFileNames = (
    (os.stat(fileName).st_mtime, fileName)
    for fileName in glob.glob(jsonFileDirectory + "/Lurie_*.json")
)
# print('Files: %d' % len(flowsheetFileNames))

count = 0
patIDs = []
for st_mtime, fileName in sorted(flowsheetFileNames, reverse=True):
    patID = fileName.split("_")[1].split(".")[0]
    patIDs.append(patID)
    # print('%10.3f: %s, %s' % (st_mtime, patID, fileName))
    count += 1
    if count > 1000:
        break
# patIDs=["000044"]

dailyIOList = list()

print(len(patIDs))

for patID in sorted(patIDs):
    print("%s" % patID)

    db = hero_fsdb.FileDB(
        os.path.join(jsonFileDirectory, str("Lurie_" + patID + ".json"))
    )
    db.read_file()

    # OK, so now we need to go through each rectified OBX message
    # and calculate the date (since we're going from d1@0001 to d2@0000)
    # and then accumulate the fluids for that date
    if len(db.ParameterSets) > 0:
        fluidIntakeDictionary = {}
        fluidOutputDictionary = {}
        weightDictionary = {}
        growthDictionary = {}
        priorLocationsDictionary = {}
        fluidIntakeDetailsFile = open(
            "JSON Fluid Reports/Lurie_%s_FluidIntakeDetails.txt" % patID, "w"
        )
        fluidOutputDetailsFile = open(
            "JSON Fluid Reports/Lurie_%s_FluidOutputDetails.txt" % patID, "w"
        )
        weightDetailsFile = open(
            "JSON Fluid Reports/Lurie_%s_WeightDetails.txt" % patID, "w"
        )
        patientLocation = None

        for ps in db.ParameterSets:
            for p in ps.Parameters:
                #        for k, m in msgDictionary.items():
                #            try:
                if p.Observation == "Prior Location":
                    msgDate = (ps.StartTime - dt.timedelta(minutes=1)).date()
                    priorLocationsDictionary[msgDate] = str(p.Value)
                    continue
                if p.Observation.replace("&", "^").split("^")[0] in fluidOutputRowIDs:
                    if len(p.Value) > 0:
                        msgVolume = float(p.Value)
                    else:
                        msgVolume = 0
                    # the line below properly moves obx's from midnight to the day before
                    msgDate = (ps.StartTime - dt.timedelta(minutes=1)).date()
                    fluidOutputDetailsFile.write(
                        "%s|%s|%6.3f|%s\n"
                        % (msgDate.isoformat(), str(ps.StartTime), msgVolume, str(p))
                    )
                    if msgDate in fluidOutputDictionary:
                        fluidOutputDictionary[msgDate] += msgVolume
                    else:
                        fluidOutputDictionary[msgDate] = msgVolume
                    continue
                if p.Observation.replace("&", "^").split("^")[0] in fluidIntakeRowIDs:
                    if len(p.Value) > 0:
                        msgVolume = float(p.Value)
                    else:
                        msgVolume = 0
                    # the line below properly moves obx's from midnight to the day before
                    msgDate = (ps.StartTime - dt.timedelta(minutes=1)).date()
                    fluidIntakeDetailsFile.write(
                        "%s|%s|%6.3f|%s\n"
                        % (msgDate.isoformat(), str(ps.StartTime), msgVolume, str(p))
                    )
                    if msgDate in fluidIntakeDictionary:
                        fluidIntakeDictionary[msgDate] += msgVolume
                    else:
                        fluidIntakeDictionary[msgDate] = msgVolume
                    continue
                if p.Unit == "ml":
                    # so it's a fluid, but we don't recognize it as an intake...
                    with open("scripts/UnaccumulatedFluids.txt", "a") as UnaccumulatedFile:
                        UnaccumulatedFile.write(
                            "Lurie_%s %s: %s\n"
                            % (patID, dt.datetime.today().isoformat(), str(ps))
                        )
                    continue
                if (
                    p.Observation.replace("&", "^").split("^")[0] == "304492701"
                ):  # if it's a "Dosing Weight" (in ounces)
                    msgWeight = float(p.Value)
                    # the line below properly moves obx's from midnight to the day before
                    msgDate = (ps.StartTime - dt.timedelta(minutes=1)).date()
                    weightDetailsFile.write(
                        "%s|%6.0f (g)|%s\n"
                        % (msgDate.isoformat(), 28.3495 * msgWeight, str(p))
                    )
                    weightDictionary[msgDate] = msgWeight
                    # growthDictionary[(msgDate, "Dosing Weight")] = m[5][0]
                    growthDictionary[(ps.StartTime, "Dosing Weight")] = msgWeight
                    continue
                if p.Observation.split("^")[0] in (
                    "3041101",
                    "3041601",
                    "3041401",
                    "304275801",
                ):  # Height, Head Circum, Weight, Weight Source
                    # msgDate = (
                    #    dt.datetime.strptime(m[14][0], "%Y%m%d%H%M%S")
                    #    - dt.timedelta(minutes=1)
                    # ).date()
                    # growthDictionary[(msgDate, m[3][0][1][0])] = m[5][0]
                    growthDictionary[(ps.StartTime, p.Observation.split("^")[1])] = (
                        p.Value
                    )
                continue
            #            except (IndexError, ValueError):
            #                print("********************************************")
            #                print("Error: " + str(m))
            #                print("********************************************")
            #                with open("CalcFluidsErrors.txt", "a") as errorFile:
            #                    errorFile.write(
            #                        "%s: %s\n" % (dt.datetime.today().isoformat(), str(m))
            #                    )
            #                continue
            if patientLocation != ps.BedId and ps.BedId != None:
                patientLocation = ps.BedId

        fluidIntakeDetailsFile.close()
        fluidOutputDetailsFile.close()
        weightDetailsFile.close()

        with open(
            "JSON Fluid Reports/Lurie_%s_FluidIntakeSummary.txt" % patID, "w"
        ) as fluidIntakeSummaryFile:
            lastWeight = 0
            for d, v in sorted(fluidIntakeDictionary.items())[
                :-1
            ]:  # the [:-1] causes us to skip the last row (which is always incomplete)
                lastWeight = weightDictionary.get(d, lastWeight)
                print(
                    "%s: Intake: %6.3f (mL), Patient Weight: %6.3f (oz)"
                    % (d.isoformat(), v, lastWeight)
                )
                normalizedIntake = -1
                if lastWeight != 0:
                    normalizedIntake = (
                        35.274 * v / lastWeight
                    )  # 35.274 converts from mL/oz to mL/kg
                fluidIntakeSummaryFile.write(
                    "%s: Intake: %6.3f (mL), Patient Weight: %6.0f (g), Normalized Intake: %6.3f (mL/kg), Prior Loc: %s\n"
                    % (
                        d.isoformat(),
                        v,
                        28.3495 * lastWeight,
                        normalizedIntake,
                        priorLocationsDictionary.get(d, ""),
                    )
                )
                dailyIORowDict = {
                    "ID": str("Lurie_" + patID),
                    "StartDate": d.isoformat(),
                    "OBX": "DailyFluidIntake",
                    "Value": "%6.3f" % v,
                    "Unit": "mL",
                    "PriorLoc": priorLocationsDictionary.get(d, ""),
                }
                dailyIOList.append(dailyIORowDict)

        with open(
            "JSON Fluid Reports/Lurie_%s_FluidOutputSummary.txt" % patID, "w"
        ) as fluidOutputSummaryFile:
            d = dt.datetime.fromisoformat("2021-01-01")
            for d, v in sorted(fluidOutputDictionary.items()):
                print("%s: %6.3f (mL)" % (d.isoformat(), v))
                fluidOutputSummaryFile.write("%s: %6.3f (mL)\n" % (d.isoformat(), v))
                dailyIORowDict = {
                    "ID": str("Lurie_" + patID),
                    "StartDate": d.isoformat(),
                    "OBX": "DailyFluidOutput",
                    "Value": "%6.3f" % v,
                    "Unit": "mL",
                    "PriorLoc": priorLocationsDictionary.get(d, ""),
                }
                dailyIOList.append(dailyIORowDict)

            lastData = d.isoformat()

        with open(
            "JSON Fluid Reports/Lurie_%s_GrowthSummary.txt" % patID, "w"
        ) as growthSummaryFile:
            for d, v in sorted(growthDictionary.items(), reverse=True):
                # print("%s: %s: %s" % (d[0].isoformat(), d[1], v))
                print("%s: %s: %s" % (d[0], d[1], v))
                conversionStr = ""
                if v != "":
                    if d[1] in ("Dosing Weight", "Weight"):
                        conversionStr = "%.0f (g)" % float(28.3495 * float(v))
                    if d[1] in ("Head Circumference", "Height"):
                        conversionStr = "%.1f (cm)" % float(2.54 * float(v))
                # growthSummaryFile.write("%s: %s: %s (%s)\n" % (d[0].isoformat(), d[1], v, conversionStr))
                growthSummaryFile.write(
                    "%s: %s: %s (%s)\n" % (d[0], d[1], v, conversionStr)
                )

        censusDictionary = {}
        if os.path.isfile("JSON Fluid Reports/Census.txt"):
            with open("JSON Fluid Reports/Census.txt", "r") as censusFile:
                for censusLine in censusFile:
                    censusDictionary[censusLine.split(maxsplit=3)[0]] = (
                        censusLine.split(maxsplit=3)[1],
                        censusLine.split(maxsplit=3)[2],
                    )
        censusDictionary[patID] = (patientLocation, lastData)
        with open("JSON Fluid Reports/Census.txt", "w") as censusFile:
            for d, v in sorted(censusDictionary.items()):
                censusFile.write("%s %s %s\n" % (str(d), str(v[0]), str(v[1])))

print("Writing daily I/O CSV file")
outputDF = pd.DataFrame(dailyIOList)
outputDF.to_csv("DailyIO.csv", index=False)

# quick little detour here to record all the services that are not "NEO"
# if len(servicesDictionary) > 0:
#    with open("JSON Fluid Reports\Services.txt", "w") as servicesFile:
#        for d, v in sorted(servicesDictionary.items()):
#            servicesFile.write("%s: %s\n" % (str(d), str(v)))
