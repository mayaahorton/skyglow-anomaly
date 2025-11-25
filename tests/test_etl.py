# tests/test_etl.py

import pandas as pd
import pytest

from src.skyglow.etl import parse_date_from_band_name


@pytest.mark.parametrize(
    "name, expected",
    [
        ("viirs_2015_01", pd.Timestamp(2015, 1, 1)),
        ("viirs_2020_12", pd.Timestamp(2020, 12, 1)),
    ],
)
def test_parse_date_from_band_name_valid(name, expected):
    assert parse_date_from_band_name(name) == expected


def test_parse_date_from_band_name_invalid():
    with pytest.raises(ValueError):
        parse_date_from_band_name("foo_2015_01")

