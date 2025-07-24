import codecs
import datetime
import json
import os


def now_with_timezone(whole_seconds_only) -> datetime:
    dt = datetime.datetime.now()
    if whole_seconds_only:
        dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    return dt.astimezone()


def parse_iso_date(text) -> datetime:
    # FromIsoFormat requires either no decimal portion after the seconds, or exactly 6 places after the decimal
    pos1 = text.find(".")
    pos2 = text.find("-", pos1)
    if pos2 == -1:
        pos2 = text.find("+", pos1)
    if pos1 != -1 and pos2 != -1:
        if (pos2 - pos1) > 7:
            text = text[0 : pos1 + 7] + text[pos2:]
        elif pos2 - pos1 < 7:
            text = text[0:pos2] + "0" * (7 - pos2 + pos1) + text[pos2:]
    dt = datetime.datetime(2000, 1, 1, 0, 0, 0)
    dt = dt.fromisoformat(text)
    return dt


class Parameter:
    def __init__(self, other):
        self._type_ = "MPSC.Data.Parameter, hero_types"
        if other is None:
            self.Observation = None
            self.Unit = None
            self.Value = 0
            self.Text = None
        else:
            # If we are reading JSON, other is a dictionary, so we need to use [] subscript operator
            # to get the field values. If we are copying an object, we can use the same code to copy
            # the object's internal dictionary.
            if isinstance(other, Parameter):
                other = other.__dict__
            self.Observation = other["Observation"]
            self.Unit = other["Unit"]
            self.Value = other["Value"]
            self.Text = other["Text"]

    def __repr__(self) -> str:
        return f"{type(self).__name__} {self.Observation} {self.Value} {self.Unit} {self.Text}"


class ParameterSet:
    def __init__(self, other):
        self._type_ = "MPSC.Data.ParameterSet, hero_types"
        if isinstance(other, str):
            other = json.loads(other)
        if other is None:
            self.ObjectId = None
            self.SiteId = None
            self.LayerId = None
            self.IsDeleted = False
            self.IsChanged = False
            self.PreviousVersionObjectId = None
            self.PatientId = None
            self.StartTime = None
            self.EndTime = None
            self.BedId = None  # WEK: by moving this down (it was before PatId), it takes lower precedence in sorting by the json string
            # self.LastUpdated = now_with_timezone(True)
            self.LastUpdated = None  # WEK: This messes up identifying duplicated data, but perhaps there's a better way?
            self.Category = ""
            self.Parameters = []
        else:
            # If we are reading JSON, other is a dictionary, so we need to use [] subscript operator
            # to get the values. If we are copying an object, we can use the same code to copy the
            # object's internal dictionary.
            if isinstance(other, ParameterSet):
                other = other.__dict__
            self.ObjectId = other["ObjectId"]
            self.SiteId = other["SiteId"]
            self.LayerId = other["LayerId"]
            self.IsDeleted = other["IsDeleted"]
            self.IsChanged = other["IsChanged"]
            self.PreviousVersionObjectId = other["PreviousVersionObjectId"]
            self.PatientId = other["PatientId"]
            if isinstance(other["StartTime"], str):
                self.StartTime = parse_iso_date(other["StartTime"])
            else:
                self.StartTime = other["StartTime"]
            if isinstance(other["EndTime"], str):
                self.EndTime = parse_iso_date(other["EndTime"])
            else:
                self.EndTime = other["EndTime"]
            self.BedId = other[
                "BedId"
            ]  # moved this after PatientID and StartTime/EndTime instead of before
            if isinstance(other["LastUpdated"], str):
                self.LastUpdated = parse_iso_date(other["LastUpdated"])
            else:
                self.LastUpdated = other["LastUpdated"]
            self.Category = other["Category"]
            self.Parameters = []
            for p in other["Parameters"]:
                self.Parameters.append(Parameter(p))

    def __repr__(self) -> str:
        s = f"{type(self).__name__} (Patient={self.PatientId}, StartTime={self.StartTime})\n"
        for p in self.Parameters:
            s += f"    {p}\n"
        return s

    def set_parameter(self, observation, unit, value, text):
        p = self.get_parameter(observation)
        if p is None:
            p = Parameter(None)
            self.Parameters.append(p)
        p.Observation = observation
        p.Unit = unit
        p.Value = value
        p.Text = text

    def get_parameter(self, observation) -> Parameter:
        for p in self.Parameters:
            if p.Observation == observation:
                return p
        return None

    def to_json(self) -> str:
        ps = ParameterSet(self.__dict__)
        if ps.StartTime is not None:
            # ps.StartTime = ps.StartTime.isoformat()
            ps.StartTime = str(
                ps.StartTime
            )  # wek: I'm using str() rather than isoformat() to be compatible with floats representing days since birth
        if ps.EndTime is not None:
            # ps.EndTime = ps.EndTime.isoformat()
            ps.EndTime = str(ps.EndTime)
        if ps.LastUpdated is not None:
            # ps.LastUpdated = ps.LastUpdated.isoformat()
            ps.LastUpdated = str(ps.LastUpdated)
        s = json.dumps(ps, default=lambda obj: obj.__dict__)
        s = s.replace("_type_", "$type")
        return s


class FileDB:
    def __init__(self, path):
        self.path = path
        self.ParameterSets = []
        self.TimeSeries = []
        self.Patients = []
        self.BedAssignments = []

    def read_file(self):
        file = codecs.open(self.path, "r", "utf8")
        data = json.load(file)
        file.close()
        for obj in data:
            # Since the type item starts with a $, we can't access it in the dictionary
            # so we need to re-serialize to JSON and pick the item out of the string.
            j = json.dumps(obj)
            if "MPSC.Data.Patient" in j:
                pass
            elif "MPSC.Data.ParameterSet" in j:
                # Append a ParameterSet copied from the file object.
                self.ParameterSets.append(ParameterSet(obj))
            elif "MPSC.Data.TimeSeries" in j:
                # Append the time series parameters as well. Note that TimeSeries has
                # all of the same properties as ParameterSet.
                self.ParameterSets.append(ParameterSet(obj))
            elif "MPSC.Data.BedAssignment" in j:
                pass

    def write_json_str(self, jsonStr):
        # Create or append to the file.
        if os.path.isfile(self.path):
            file = codecs.open(self.path, "rb+", "utf8")
        else:
            file = codecs.open(self.path, "ab", "utf8")
        # Start at the end of the file and back up until we find the final bracket ']'
        file.seek(0, 2)
        pos = file.tell()
        while pos > 0:
            pos = pos - 1
            file.seek(pos, 0)
            if file.read(1) == "]":
                break
        if pos == 0:
            file.write("[\r\n")
        else:
            file.seek(pos - 2, 0)
            file.write(",\r\n")
        file.write(jsonStr)
        file.write("\r\n]")
        file.close()

    def write_object(self, obj):
        write_json_str(self, obj.to_json())

    def get_parameter_values(
        self, category, observation, patientId, startTime, endTime
    ):
        times = list()
        values = list()
        if isinstance(startTime, str):
            d = datetime.datetime(2000, 1, 1, 0, 0, 0)
            startTime = d.fromisoformat(startTime).astimezone()
            print(startTime)
        if isinstance(endTime, str):
            d = datetime.datetime(2000, 1, 1, 0, 0, 0)
            endTime = d.fromisoformat(endTime).astimezone()
            print(endTime)
        # psList = list(filter(self.ParameterSets, lambda ps: ((patientId is None or patientId == ps.PatientId)#
        # and (category is None or category == ps.Category)
        # and (startTime is None or ps.StartTime is None or startTime <= ps.StartTime)
        # and (EndTime is None or ps.EndTime is None or endTime >= ps.EndTime))))
        # for ps in psList:
        # p = ps.get_parameter(observation)
        # if p is not None:
        # times.append(ps.StartTime)
        # values.append(p.Value)
        for ps in self.ParameterSets:
            if (
                (patientId is None or patientId == ps.PatientId)
                and (category is None or category == ps.Category)
                and (
                    startTime is None
                    or ps.StartTime is None
                    or startTime <= ps.StartTime
                )
                and (endTime is None or ps.EndTime is None or endTime >= ps.EndTime)
            ):
                p = ps.get_parameter(observation)
                if p is not None:
                    times.append(ps.StartTime)
                    values.append(p.Value)
        return (times, values)
