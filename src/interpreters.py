import pandas as pd
from src.data_classes import GDPMetadata


def build_long_name_interpreter(parser_func, edge_cases: dict[str]):
    """ Builds a long_name_interpreter given an interpreting function and edge cases the interpreting function can not handle

        :arg
            | parser_func: function taking two arguments, (1) long_name and (2) verbose and returns a 3-digit
                           country code. Should raise ValueError if no match can be found.
            | edge_cases (list[dict]): keys are long_name values that parser_func can not handle, dict entries are
                                       substituted and passed to parser_func instead
        :returns
            | (function): long_name interpreting function taking two arguments, (1) long_name and (2) verbose
        :raises
            | No exceptions raised.
    """
    def long_name_interpreter(long_name: str, verbose=False) -> str:
        """ Returns the country_code given a long name

            :arg
                | long_name (str): long name of a country that may or may not be the official name of the country
                | verbose (bool): whether or not to print the matching process
            :returns
                | (str): three-digit country code, or 'XXX' if no suitable match can be found.
            :raises
                | No exceptions raised.
         """
        if long_name in list(edge_cases.keys()):
            long_name = edge_cases[long_name]
        try:
            country_code = parser_func(long_name, verbose)
        except ValueError:
            country_code = 'XXX'
            if verbose:
                print(f'long_name_interpreter: no match found for {long_name}, returning {country_code} instead.')
        return country_code

    return long_name_interpreter


def build_GDPMetadata_parser_func(metadata: GDPMetadata):
    """ Builds an interpreter function based on a GDPMetadata object

        :arg
            | metadata (GDPMetadata): instance of GDPMetadata
        :returns
            | (function; dict[str]): function taking two arguments, (1) str and (2) bool, returning str; edge cases
        :raises
            No exceptions raised.
    """

    def load_edge_cases():
        filepath = './data/iea_name_edge_cases.txt'
        return pd.read_csv(filepath, sep='\t+', engine='python', header=0, index_col=0).to_dict()['Official Name']

    def parser_func(long_name, verbose):
        return metadata.get_country_code(metadata.match_colloquial_long_name(long_name, verbose))

    edge_cases = load_edge_cases()
    return parser_func, edge_cases
