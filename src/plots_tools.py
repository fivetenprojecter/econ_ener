def get_color_based_on_region(region):
    """ Returns a hexadecimal colour to use for region plotting. Region names are based on World Bank data. """
    region_colors = {'South Asia': '#E27D60',
                     'Europe & Central Asia': '#4D6D9A',
                     'Middle East & North Africa': '#41B3A3',
                     'East Asia & Pacific': '#C38D9E',
                     'Sub-Saharan Africa': '#85CDCA',
                     'Latin America & Caribbean': '#E8A87C',
                     'North America': '#116466'}
    return region_colors[region]
