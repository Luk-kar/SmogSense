"""
Types for air quality API data
"""

# Python
from typing import Literal


ANNUAL_STATISTICS_TYPES = {
    "indicator": Literal[
        "SO2",
        "NO2",
        "NOx",
        "CO",
        "O3",
        "C6H6",
        "PM10",
        "PM2,5",
        "Pb(PM10)",
        "As(PM10)",
        "Cd(PM10)",
        "Ni(PM10)",
        "BaP(PM10)",
        "WWA(PM10)",
        "Jony(PM2,5)",
        "Hg(TGM)",
        "Formaldehyd",
        "Depozycja",
    ]
}


MAP_POLLUTANT_TYPES = {
    "indicatorType": Literal["OZ", "OR"],
    "indicator": Literal[
        "PM10_sr_roczna",
        "PM25_sr_roczna",
        "NO2_sr_roczna",
        "O3_3letnia",
        "BaP_sr_roczna",
        "SO2_25h_max",
        "PM10_36_max",
        "NO2_19h_max",
        "SO2_4_max",
    ],
    "year": int,
}
