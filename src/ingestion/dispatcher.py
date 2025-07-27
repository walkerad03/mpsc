from typing import Union

from src.ingestion.parsers import enteral_feed, generic_parser

PARSERS = {
    "3040801^Pulse^LCHEROFS": generic_parser.parse,
    "3041401^Weight^LCHEROFS": generic_parser.parse,
    "3041601^Head Circumference^LCHEROFS": generic_parser.parse,
    "3041101^Height^LCHEROFS": generic_parser.parse,
    "Calculated Energy": generic_parser.parse,
    "3040901^Resp^LCHEROFS": generic_parser.parse,
    "3041001^SpO2^LCHEROFS": generic_parser.parse,
    "EnteralFeed": enteral_feed.parse,
    "YearOfBirth": generic_parser.parse,
    "Sex": generic_parser.parse,
    "PEDIATRIC BIRTH WEIGHT (OZ)^PEDIATRIC BIRTH WEIGHT (OZ)": generic_parser.parse,
    "PEDIATRIC GESTATION AGE (WEEKS)^PEDIATRIC GESTATION AGE (WEEKS)": generic_parser.parse,
}

with open("resources/FluidIntakeRowIDs.txt", "r") as f:
    FLUID_INTAKE_ROW_IDS = [line.strip() for line in f]


def route_observation(
    param: dict[str, Union[str, None, bool]], patient_id: str, start_time: str
):
    obs = param.get("Observation")
    assert isinstance(obs, str)

    rowID = obs.replace("&", "^").split("^")[0]

    match rowID:
        case "304452001" | "304451901" | "30460222601":
            return "EnteralFeed", PARSERS["EnteralFeed"](param, patient_id, start_time)
        case _:
            pass

    if obs not in PARSERS:
        raise ValueError(f"Unknown observation: {obs}")
    parser = PARSERS[obs]
    return obs, parser(param, patient_id, start_time)
