import pandas as pd
import numpy as np
import re


class WorldDataHandler:
    """ Parent class for dealing with information from annually-resolved global data sets """

    continent_descriptors = ['Africa', 'America', 'Asia', 'Europe', 'Pacific', 'Middle East']

    def __init__(self, filepath):
        # Load data
        self.filepath = filepath
        self.data = self.load_data()

        # Create a list of all available country codes and names
        self.available_country_codes = self.create_country_code_list()
        self.available_long_names = self.create_long_name_list()

    def load_data(self) -> pd.DataFrame:
        """ Data loading function

            OVERWRITE FOR SPECIFIC DATASET

        """
        return None

    def create_country_code_list(self) -> list:
        """ Create a list of abbreviated country identifiers

            OVERWRITE FOR SPECIFIC DATASET

        """
        return list()

    def create_long_name_list(self) -> list:
        """ Create a list of descriptive country names identifier

            OVERWRITE FOR SPECIFIC DATASET

        """
        return list()

    def check_country_code_availability(self, country_code: str):
        """ Check whether or not country code matches an available country codes """
        if country_code in self.available_country_codes:
            return True
        else:
            raise KeyError(f'{country_code} is not recognized as an available country code.')

    def check_long_name_availability(self, long_name: str):
        """ Check whether or not country name matches an available country names """
        if long_name in self.available_long_names:
            return True
        else:
            raise KeyError(f'{long_name} is not recognized as an available country name.')

    def get_info(self, country_code: str):
        """ Get all available info given a specific country code

            :arg
                | country_code (str): three letter country code
            ::return
                | (pd.DataFrame): DataFrame row matching the sought country code
            :raises
                No exceptions raised.
        """
        if self.check_country_code_availability(country_code):
            return self.data.loc[self.data['Country Code'] == country_code]

    def extract_year_from_column(self, column: str) -> int:
        """ Function detects whether or not given column title is a year indicator. Must return the year as an integer
            or None if column_title does not match the pattern.

            OVERWRITE FOR SPECIFIC DATASET

            :arg
                | column (str): column title that can contain the year of the data in the column
            ::return
                | (int): :return int if year is found, otherwise None
            :raises
                No exceptions raised.
        """
        return None

    def extract_value_for_year(self, info: pd.DataFrame, column: str) -> float:
        """ Function detects whether or not given column title is a year indicator. Must return the year as an integer
            or None if column_title does not match the pattern.

            OVERWRITE FOR SPECIFIC DATASET

            :arg
                | info (pd.DataFrame): subsection of the DataFrame
                | column (str): column title that can contain the year of the data in the column
            :return:
                | (float): value at given column
            Raises:
                No exceptions raised.
        """
        value = info[column].values[0]
        if value == '..':
            value = np.nan
        else:
            value = float(value)
        return value

    def create_time_series_for_info(self, info: pd.DataFrame) -> (np.ndarray, np.ndarray):
        years, values = [], []
        for column in info.columns:
            year = self.extract_year_from_column(column)
            if year:
                years.append(year)
                values.append(self.extract_value_for_year(info, column))

        return np.array(years), np.array(values)


class GDPDataHandler(WorldDataHandler):
    """ Parent class for dealing with GDP datasets """

    def __init__(self, filepath):
        super().__init__(filepath)
        self.additional_initialization()

    def create_country_code_list(self):
        """ Create a list of all available country codes """
        return self.data['Country Code'].to_list()

    def create_long_name_list(self):
        """ Create a list of all available long country names """
        return self.data['Country Name'].to_list()

    def additional_initialization(self):
        """ Placeholder function for additional initialization steps without calling super """
        pass

    def load_data(self):
        """ Load the GDP datasets via pandas.read_csv

            :arg
                | None
            :return
                | (pd.DataFrame): DataFrame containing data as loaded.
            :raises
                No exceptions raised.
        """
        return pd.read_csv(self.filepath, sep='\t+', engine='python', encoding='ansi')

    def create_timeseries_for_country_by_series_name(self, country_code: str, series_name: str):
        return self.create_time_series_for_info(self.get_info_by_series_name(country_code, series_name))

    def get_info_by_series_name(self, country_code: str, series_name: str):
        info = self.get_info(country_code)
        return info.loc[info['Series Name'] == series_name]

    def get_info_by_series_code(self, country_code: str, series_code: str):
        info = self.get_info(country_code)
        return info.loc[info['Series Code'] == series_code]


class GDPMetadata(GDPDataHandler):
    """ Class to get metadata information for specific countries in the World Bank Data set """

    def additional_initialization(self):
        # Create a list of all available regions
        self.regions = self.get_regions()

    def get_regions(self):
        """ Returns a list of all available regions, filtering out non-geographic descriptors (i.e. World, etc.)

            :arg
                | None
            :return
                | (np.ndarray): array of strings for unique regions
            :raises
                No exceptions raised.
        """
        def is_continental_region(region: str) -> bool:
            """ True if region is part of a continental region, i.e. Middle East, Africa, Asia

                :arg
                    | region (str): name of a region
                :returns
                    | (bool): True if region is part of a continental region
                :raises
                    No exceptions raised.
            """
            is_geographic_region = False
            for region_nam in self.continent_descriptors:
                if region:
                    if region_nam in region:
                        is_geographic_region = True
                        break
            return is_geographic_region

        return [region for region in self.data['Region'].unique() if is_continental_region(region)]

    def get_long_name(self, country_code: str) -> str:
        """ Returns the long name for a given country code """
        return self.get_info(country_code)['Long Name'].values[0]

    def get_country_code(self, long_name: str) -> str:
        """ Returns the country code for a given long name """
        if self.check_long_name_availability(long_name):
            idx = np.argwhere(self.data['Country Name'].to_numpy() == long_name)[0][0]
            return self.available_country_codes[idx]

    def get_region(self, country_code: str):
        return self.get_info(country_code)['Region'].values[0]

    def match_colloquial_long_name(self, colloquial_name: str, verbose=True):
        """ Returns an official name for a colloquially used country name
            E.g. 'Germany' -> 'Federal Republic of Germany'

            :arg
                | colloquial_name (str): colloquial country name
                | verbose (bool): if True prints the found match
            :returns
                | (str): official country name
            :raises
                ValueError: is raised if no official match can be found.
        """
        if colloquial_name not in self.available_long_names:
            idx = 0
            while idx < 5:
                if idx == 0:
                    shortened_name = colloquial_name
                else:
                    shortened_name = colloquial_name[:-idx]

                for lm in self.available_long_names:
                    if shortened_name in lm:
                        if verbose:
                            print(f'Matched {colloquial_name:<20} -> {lm}')
                        return lm
                idx += 1
            raise ValueError(f'Could not match {colloquial_name} to any official country.')
        else:
            return colloquial_name


class GDPData(GDPDataHandler):
    def load_data(self):
        """ Overwrites the parent class function. """
        return pd.read_csv(self.filepath, sep='\t+', engine='python', encoding='ansi')

    def extract_year_from_column(self, column: str) -> int:
        """ Overwrites the parent class function.

            Return the year from the column title. :return None if no year is found.

        """
        res = re.search(r'[\d]+ \[YR[\d]+\]', column)
        if res:
            # Column name matches pattern
            return int(res[0][:4])
        else:
            return None


class IEAData(WorldDataHandler):
    """ For handling International Energy Agency data """

    def __init__(self, filepath, long_name_interpreter):
        """ Overwrites the default __init__ function"""
        self.long_name_interpreter = long_name_interpreter
        super().__init__(filepath)

    def load_data(self) -> pd.DataFrame:
        """ Overwrites the default load_data function """
        df = pd.read_excel(self.filepath, 'TimeSeries_1971-2021', skiprows=[0])
        df['Country Code'] = [self.long_name_interpreter(long_name, verbose=False) for long_name in df['Country']]
        return df

    def filter_long_name_list(self, long_name_list: list[str]) -> list[str]:
        """ Removes any non-physical regions considered in the IEA dataset """
        filtered_list = []
        banned_terms = ['IEA', 'OECD']

        for long_name in long_name_list:
            add_to_list = True
            # Remove continents
            if long_name in self.continent_descriptors:
                add_to_list = False
            # Remove banned terms
            for banned_term in banned_terms:
                if banned_term in long_name:
                    add_to_list = False

            if add_to_list:
                filtered_list.append(long_name)
        return filtered_list

    def create_country_code_list(self):
        """ Overwrites default create_country_code_list """
        self.country_code_dict = self.create_colloquial_name_parser()
        return list(self.country_code_dict.keys())

    def create_colloquial_name_list(self):
        return list(self.data['Country'].unique())

    def create_long_name_list(self):
        """ Overwrites default create_long_name_list """
        return self.create_colloquial_name_list()

    def create_colloquial_name_parser(self) -> dict:
        """ Create a dictionary that features country codes as keys, matching their respective colloquial names """
        filtered_list = self.filter_long_name_list(self.create_colloquial_name_list())
        country_code_dict = {}
        for colloquial_name in filtered_list:
            country_code_dict[self.long_name_interpreter(colloquial_name, verbose=True)] = colloquial_name
        return country_code_dict

    def get_colloquial_name(self, country_code: str):
        if self.check_country_code_availability(country_code):
            return self.country_code_dict[country_code]

    @staticmethod
    def get_flow_rows(info: pd.DataFrame, flow: str) -> pd.DataFrame:
        return info.loc[info['Flow'] == flow]

    @staticmethod
    def get_product_rows(info: pd.DataFrame, product: str) -> pd.DataFrame:
        return info.loc[info['Product'] == product]

    def get_product_and_flow_rows(self, info: pd.DataFrame, product: str, flow: str) -> pd.DataFrame:
        return self.get_flow_rows(self.get_product_rows(info, product), flow)

    def get_product_and_flow_rows_for_country(self, country_code: str, product: str, flow: str) -> pd.DataFrame:
        return self.get_product_and_flow_rows(self.get_info(country_code), product, flow)

    def get_electricity_output(self, country_code: str) -> pd.DataFrame:
        return self.get_flow_rows(self.get_info(country_code), 'Electricity output (GWh)')

    def extract_year_from_column(self, column) -> int:
        """ Overwrites the parent class function.

            Return the year from the column title. Returns None if no year is found.
            Uses the fact that pd.read_xlsx converts possible integers into integers
        """
        if type(column) is int and column < 3000:
            # Column name matches pattern
            return column
        else:
            return None

    def print_available_column_values(self, column: str) -> list[str]:
        """ Print unique column values for a given column """
        print(f'Available values for {column}:')
        print('----------------------------------------------------------')
        unique_entries = self.data[column].unique()
        for entry in unique_entries:
            print(f'  {entry}')
        return unique_entries

    def print_available_flows(self):
        return self.print_available_column_values('Flow')

    def print_available_products(self):
        return self.print_available_column_values('Product')
