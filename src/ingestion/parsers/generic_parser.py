from typing import Union

import pandas as pd


def parse(
    param: dict[str, Union[str, None, bool]], patient_id: str, start_time: str
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID": patient_id,
                "DateTime": start_time,
                "OBX": param.get("Observation"),
                "Value": param.get("Value"),
                "Unit": param.get("Unit"),
                "Text": param.get("Text"),
            }
        ]
    )
