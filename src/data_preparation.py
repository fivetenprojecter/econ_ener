import numpy as np
from functools import reduce

from .data_classes import IEAData, GDPData


def create_energy_dict(flows: list[str], products: list[str],
                       plot_country_codes: list[str], plot_year: int,
                       iea: IEAData) -> dict[dict[list[float]]]:
    """ Create a nested dict with keys matching flow and product fields in the IEA data set

        :arg
            | flows (list[str]): list of all flows to return in the results dictionary
            | products (list[str]): list of all products to return for each flow in the results dictionary
            | country_codes (list[str]): list of 3-digit country codes for which to query results
            | plot_year (int): year at which to query
            | iea (IEAData): energy data set
        :returns
            | (dict[dict[list[float]]]): nested dictionaries: first layer is different flows, second layer is products
        :raises
            No exceptions raised.
    """
    energy_dict = {flow: {product: [] for product in products} for flow in flows}

    for flow in flows:
        for country_code in plot_country_codes:
            info_flow = iea.get_flow_rows(iea.get_info(country_code), flow)
            for product in energy_dict[flow].keys():
                years, vals = iea.create_time_series_for_info(iea.get_product_rows(info_flow, product))
                # Extend only if there are available values for the given flow/product combination
                if vals.__len__() > 0:
                    energy_dict[flow][product].extend(vals[years == plot_year])
        # Convert lists into numpy arrays
        energy_dict[flow] = {product: np.asarray(energy_dict[flow][product]) for product in energy_dict[flow].keys()}

    return energy_dict


def get_electricity_makeup() -> (list[str], list[str]):
    """ Get the flow and product fields for electricity production """
    flows = ['Electricity output (GWh)']
    products = ['Total', 'Fossil fuels', 'Nuclear', 'Renewable sources']
    return flows, products


def create_electricity_dict(country_codes: list[str], plot_year: int, iea: IEAData) -> dict[list[float]]:
    """ Wrapper for create_energy_dict to get the energy_dict for electricity production only. """
    flows, products = get_electricity_makeup()
    return create_energy_dict(flows, products, country_codes, plot_year, iea)[flows[0]]


def create_gdp_dict(gdp_variables: list[str],
                    country_codes: list[str], plot_year: int,
                    gdp: GDPData) -> dict[list[float]]:
    """ Create a dict with keys matching GDP sets in the World Bank data set

        :arg
            | gdp_variables (list[str]): list of all GDP variables to return in the results dictionary
            | country_codes (list[str]): list of 3-digit country codes for which to query results
            | plot_year (int): year at which to query
            | gdp (GDPData): GDP data set
        :returns
            | (dict[list[float]]): dict with one field for each GDP variable queried
        :raises
            No exceptions raised.
    """
    gdp_dict = {gdp_variable: [] for gdp_variable in gdp_variables}

    for gdp_variable in gdp_variables:
        for country_code in country_codes:
            years, vals = gdp.create_timeseries_for_country_by_series_name(country_code, gdp_variable)
            gdp_dict[gdp_variable].extend(vals[years == plot_year])
        gdp_dict[gdp_variable] = np.array(gdp_dict[gdp_variable])

    return gdp_dict


def create_colloquial_name_list(country_codes: list[str], iea: IEAData) -> list[str]:
    """ Create a list of colloquial names based on list of country codes provided """
    return [iea.get_colloquial_name(country_code) for country_code in country_codes]


def determine_common_values(array_list: list[list]) -> list:
    """ Intersection between multiple arrays """
    return reduce(np.intersect1d, array_list).tolist()


def find_all_available_country_codes(gdp: GDPData, nrg_data: IEAData) -> list[str]:
    """ Returns all available country codes that are present both provided data sets"""
    return determine_common_values([gdp.available_country_codes, nrg_data.available_country_codes])


def find_all_available_country_codes_and_sanitize(gdp: GDPData, nrg_data: IEAData) -> list[str]:
    """ Returns all available country codes that are present both provided data sets, minus the WORLD code """
    country_codes = determine_common_values([gdp.available_country_codes, nrg_data.available_country_codes])
    country_codes.remove('WLD')
    return country_codes

