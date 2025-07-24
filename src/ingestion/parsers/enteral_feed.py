from collections import defaultdict
from typing import Optional, Union

import pandas as pd

label_counts: dict[str, int] = defaultdict(int)


def parse(
    param: dict[str, Optional[Union[str, bool]]], patient_id: str, start_time: str
) -> pd.DataFrame:
    observation = param.get("Observation")

    assert isinstance(observation, str)
    rowID: str = observation.replace("&", "^").split("^")[0]

    assert isinstance(rowID, str)
    match rowID:
        case "304452001" | "304451901":
            fluid_label = observation.split(" Volume (mL)-")[1].split("^")[0]
        case "30460222601":
            fluid_label = observation.split(" (mL)-")[1].split("^")[0]
        case _:
            raise ValueError("Not an enteral feed observation")

    return pd.DataFrame(
        [
            {
                "ID": patient_id,
                "DateTime": start_time,
                "OBX": param.get("Observation"),
                "Label": fluid_label,
                "Value": param.get("Value"),
                "Unit": param.get("Unit"),
                "Text": param.get("Text"),
            }
        ]
    )
