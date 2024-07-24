import pandas

from bunnyhop import config
import bunnyhop
import pytest


def test_retrieve_gnis():
    df = bunnyhop.retrieve.gnis_retrieve(config.GNIS_URL)
    assert(isinstance(df, pandas.DataFrame))