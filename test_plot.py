from . import load_data
from .src.plots import electricity_plot


def test_plot():
    gdp, gdp_md, nrg_data = load_data.load_data()
    return electricity_plot(2020, gdp, gdp_md, nrg_data)