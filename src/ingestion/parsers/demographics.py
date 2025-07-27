from typing import Optional, Union

import pandas as pd


def parse(
    param: dict[str, Optional[Union[str, bool]]], patient_id: str, start_time: str
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID": patient_id,
                "DOB": None,
                "GA": None,
                "BW": None,
                "Sex": None,
                "DataStart": None,
                "DataEnd": None,
                "FluidStart": None,
                "FluidEnd": None,
            }
        ]
    )
