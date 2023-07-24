from . import load_data
from .src import data_preparation as data_prep

from .src.plots_plotly import electricity_plot
from .src.plots_highcharts import total_energy_supply_plot


def test_plotly():
    """ Sample plot using plotly """
    gdp, gdp_md, nrg_data = load_data.load_data()
    plot_country_codes = data_prep.find_all_available_country_codes_and_sanitize(gdp, nrg_data)

    return electricity_plot(2020, plot_country_codes, gdp, gdp_md, nrg_data)


def test_highcharts():
    """ Sample plot using Highcharts """
    gdp, gdp_md, nrg_data = load_data.load_data()
    plot_country_codes = data_prep.find_all_available_country_codes_and_sanitize(gdp, nrg_data)

    return total_energy_supply_plot(2020, plot_country_codes, gdp, gdp_md, nrg_data)