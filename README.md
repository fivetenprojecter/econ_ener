# econ_ener
Package to quickly compare economic and energy supply data for state-level entities.

# Work flow
I. The design idea behind the package is to use instances of __src.data_classes.WorldDataHandler__ to load and store data. 

II. These instances are then passed to functions within __src.data_preparation__ to be organized into structures that easily interface with _plotly_ and other plotting interfaces.

III. Finally, __src.plots_plotly__ and src.plots_highcharts contain plot-generation functions that make use of the structures generated via __src.data_preparation__.
# Package layout
## module functions
- __load_data__
  - returns __src.data_classes.WorldDataHandler__ sub-class instances containing the GDP, GDP-metadata, and energy data
- __test_plot__
  - draws an interactive [sample plot](https://fivetenprojecter.github.io/) to demonstrate the package

## data
Contains sample data to illustrate the functionality of the package
  - based on data compiled by the IEA and World Bank, available under Creative Commons 4.0
    - [IEA data](https://www.iea.org/data-and-statistics/data-product/world-energy-balances-highlights) (after creating a free account).
    - [World Bank data](https://databank.worldbank.org/reports.aspx?source=2&series=NY.GDP.MKTP.CD&country=#).  
## src
The _src_ sub-package contains all the under-the-hood functionality to the package.
### Modules
#### src.data_classes
- provides class __WorldDataHandler__ to read and query a dataset featuring datasets comparing variables for state-level entities
  - data is stored as pandas.DataFrames and should only be read from
  - contains methods to query data slices along common access patterns
- __WorldDataHandler__ has child classes __GDPData__ (via __GDPDataHandler__) and __IEAData__
  - each is designed to handle GDP or energy data and access it via _country_code_, a 3-digit unique identifier for each state-level entity

#### src.interpreters
- provides interpretation between the country names used in different data sets
- built around __build_long_name_interpreter__, which creates a function converting a given country name into a 3-digit country code
  - returns __long_name_interpreter__: this function takes two args, the first being the country name to be interpreted and the second a boolean to 
    enable command line output of the interpretation process (recommended to prevent data misallocation)
  - __build_long_name_interpreter__ takes two args
    - the first is a __parser_func__, which has identical args to __long_name_interpreter__ and performs the interpretation
    - the second arg is _edge_cases_, a dict[str]
      - keys represent country names that __parser_func__ can not match accurately
      - values for keys represent replacement country names that __parser_func__ can match accurately
  - __build_GDPMetadata_parser_func__ shows how to build __parser_func__ and _edge_cases_ given metadata gleaned from the GDP dataset
    - _data\country_name_edge_cases.txt_ contains all the edge cases required for the two present data sets

#### src.data_preparation
- provides functionality to generate variables that easily fit the input for common data visualization packages
  - __create_energy_dict__: Create a nested dict with keys matching flow and product fields in the IEA data set
    - wrapped by __create_electricity_dict__ to get an electricity related subset
  - __create_gdp_dict__: Create a dict with keys matching GDP sets in the World Bank data set
  - __create_colloquial_name_list__: Create a list of colloquial names based on list of country codes provided
  
#### src.plots_plotly
- sub-package for interactive plots using the __plotly__-package
#### src.plots_highcharts
- sub-package for interactive plots using __Highcharts__ 