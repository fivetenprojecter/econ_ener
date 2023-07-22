from .src import interpreters as interp
from .src.data_classes import GDPMetadata, GDPData, IEAData

import os
from os.path import join, split


def load_data():
    """ Load the economic and energy data """
    data_directory = join(os.path.dirname(__file__), 'data')

    # [ECONOMIC DATA] GDP METADATA AND DATA
    # Path definitions
    filepath_metadata = join(data_directory, 'GDP_metadata.csv')
    filepath_gdp_per_capita_data = join(data_directory, 'GDP_percapita_allData.txt')

    gdp_md = GDPMetadata(filepath_metadata)
    gdp = GDPData(filepath_gdp_per_capita_data)

    # [ENERGY DATA] IEA
    # Path definitions
    filepath_iea_data = join(data_directory, 'World Energy Balances Highlights 2022.xlsx')

    parser_func, edge_cases = interp.build_GDPMetadata_parser_func(gdp_md)
    lni = interp.build_long_name_interpreter(parser_func, edge_cases)

    nrg_data = IEAData(filepath_iea_data, long_name_interpreter=lni)

    return gdp, gdp_md, nrg_data