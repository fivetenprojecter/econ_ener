from . import data_preparation as data_prep
from . import plots_tools
from .data_classes import GDPData, GDPMetadata, IEAData

from highcharts_core.chart import Chart
from highcharts_core.options import HighchartsOptions

import numpy as np


def get_options_as_dict():
    """ Standard options to create a plot based on the Highcharts package"""
    options_as_dict = dict(
        chart=dict(
            type='bubble',
            plotBorderWidth=1,
            zoomType='xy'
        ),

        legend=dict(
            enabled=False
        ),

        title=dict(
            text="title['text']"
        ),

        subtitle=dict(
            text="subtitle['text']"
        ),

        xAxis=dict(
            gridLineWidth=1,
            title=dict(
                text="xAxis['title']['text']"
            ),
            labels=dict(
                format="xAxis['labels']['format']"
            ),
        ),

        yAxis=dict(
            startOnTick=False,
            endOnTick=False,
            title=dict(
                text="yAxis['title']['text']"
            ),
            labels=dict(
                format="xAxis['labels']['format']"
            ),
            maxPadding=0.2
        ),

        tooltip=dict(
            useHTML=True,
            headerFormat="tooltip['headerFormat']",
            pointFormat="tooltip['pointFormat']",
            footerFormat="tooltip['footerFormat']",
            followPointer=True
        ),

        plotOptions=dict(
            series=dict(
                dataLabels=dict(
                    enabled=True,
                    format="plotOptions['series']['dataLabels']['format']"
                )
            )
        ),

        series=[dict(
            data=[],
            colorByPoint=True
        )])
    return options_as_dict


def add_label(options_dict: dict, text: str, x: float, y: float) -> dict:
    """ [UNFINISHED] Work in progress. """
    if 'annotations' not in options_dict:
        options_dict['annotations'] = {}
    if 'label' not in options_dict['annotations']:
        options_dict['annotations'] = {[]}

    options_dict['annotations']['labels'].append({
            'point': {'x': x, 'y': y},
            'text': text})

    return options_dict


def total_energy_supply_plot(plot_year: int, plot_country_codes: list[str], gdp: GDPData, gdp_md: GDPMetadata, nrg_data: IEAData):

    minBubbleSize, maxBubbleSize = 1, 100

    """ A plot of total energy supply broken down into contributing sources """
    # DATA PREPARATION
    # ------------------------------------------------------------------------------------------------------------------

    # List of all countries that are to be included in the plot
    colloquial_names = data_prep.create_colloquial_name_list(plot_country_codes, nrg_data)

    # Gross-Domestic Product (GDP) data
    gdp_variable = 'GDP per capita (constant 2015 US$)'
    gdp_list = data_prep.create_gdp_dict([gdp_variable], plot_country_codes, plot_year, gdp)[gdp_variable]

    # Energy data
    flows = ['Total energy supply (PJ)']
    products = ['Total',
                'Renewables and waste',
                'Nuclear',
                'Heat',
                'Electricity',
                'Natural gas',
                'Oil products',
                'Coal, peat and oil shale',
                'Crude, NGL and feedstocks']

    energy_dict = data_prep.create_energy_dict(flows, products, plot_country_codes, plot_year, nrg_data)[flows[0]]

    # Group the different product streams into larger categories
    fossil_products = ['Natural gas', 'Oil products', 'Coal, peat and oil shale', 'Crude, NGL and feedstocks']
    nuclear_products = ['Nuclear']
    heat_products = ['Heat']
    elec_products = ['Electricity']
    renew_products = ['Renewables and waste']

    # Create the regional data lists

    def create_graph_string(title: str, data=dict[float], new_line='<br>'):
        graph_str = f'<b>{title}</b>' + new_line
        for key in data.keys():
            value = data[key] if not np.isnan(data[key]) else 0
            fraction = round(10 * value)
            for idx in range(11):
                if idx <= fraction:
                    elem = '|'
                else:
                    elem = ''
                graph_str += elem
            graph_str += f' {value * 100:.1f}% {key}' + new_line
        return graph_str

    data_lists_separated_by_region = {region: [] for region in gdp_md.get_regions()}
    for idx, country_code in enumerate(plot_country_codes):
        # Determine contribution of each product
        fossil, nuclear, heat, elec, renew = [np.sum([energy_dict[var_nam][idx] for var_nam in pl]) for pl in
                                              [fossil_products, nuclear_products, heat_products, elec_products,
                                               renew_products]]

        # Total energy supply minus the net electricity supply
        # -> secondary source, does not contribute to overall supply
        total = energy_dict['Total'][idx] - elec

        info_dict = {'Fossil': fossil / total,
                     'Nuclear': nuclear / total,
                     'Renewable & waste': renew / total,
                     'Other (Heat, electricity import, etc.)': np.clip(
                         total - nuclear - renew - fossil, 0,
                         np.inf) / total}

        custom_data_dict = {'mix_string': create_graph_string('Energy mix', info_dict), 'renew_deployed': renew / 1e3}

        # Determine the region
        region = gdp_md.get_region(country_code)

        data_lists_separated_by_region[region].append({
            'name': colloquial_names[idx],
            'countryCode': country_code,
            'country': colloquial_names[idx],
            'region': region,
            'x': gdp_list[idx] / 1e3,
            'y': 100 * renew / total,
            'z': total / 1e3,
            'color': plots_tools.get_color_based_on_region(region),
            'custom': custom_data_dict,
        })

    # STYLING
    # ------------------------------------------------------------------------------------------------------------------

    # Default options for options dict initialization
    oad = get_options_as_dict()

    # Load data into options dict
    # West -> East
    custom_region_order = ['North America', 'Latin America & Caribbean', 'Europe & Central Asia',
                           'Middle East & North Africa', 'Sub-Saharan Africa',
                           'South Asia', 'East Asia & Pacific']

    oad['series'] = []
    for region in custom_region_order:
        oad['series'].append({
            'data': data_lists_separated_by_region[region],
            'name': region,
            'color': plots_tools.get_color_based_on_region(region),
            'minSize': minBubbleSize,
            'maxSize': maxBubbleSize})

    # STYLING
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------
    xlabel = 'GDP per capita (1000s of constant 2015 US$)'
    ylabel = 'Percentage of total energy supplied by renewable sources and waste-to-energy schemes'
    zlabel = 'total energy supply'

    x_tt, y_tt, z_tt = 'GDP per capita', 'Renewable & waste fraction', 'Total energy supply'

    # Figure title
    oad['title'] = {
        'text': f'Economic development does not necessarily drive renewable energy uptake',
        'align': 'left'}

    oad['subtitle'] = {
        'text': f'Percentage of total energy supply provided by renewable sources (solar, wind, hydro, biofuels, etc.) ' +
                ' and waste-to-energy schemes for select countries in {plot_year}' +
                ' [Source: <a href="https://www.iea.org/data-and-statistics/data-product/world-energy-balances-highlights">IEA</a> and ' +
                '<a href="https://databank.worldbank.org/reports.aspx?source=2&series=NY.GDP.MKTP.CD&country=#">World Bank</a>] <br>'
                'Supporting code on <a href="https://github.com/fivetenprojecter/econ_ener">GitHub</a>.',
        'align': 'left'}

    # Legend
    oad['legend'] = {
        'enabled': True,
        'title': {
            'text': f'Size indicates {zlabel} <br/><span style="font-size: 9px; color: #666; font-weight: normal">(Click on region to hide)</span>'},
        'align': 'right',
        'layout': 'vertical',
        'verticalAlign': 'top',
        'itemMarginTop': 10,
        'borderRadius': 1}

    oad['legend']['bubbleLegend'] = {
        'legendIndex': 0,
        'enabled': True,
        'connectorDistance': 40,
        'borderWidth': 3,
        'connectorWidth': 3,
        'labels': {
            'align': 'left',
            'format': '{value:,.0f} TJ'
        },
        'minSize': minBubbleSize,
        'maxSize': maxBubbleSize,
        'ranges': [{'value': val} for val in [1, 20, 150]]}

    # Data labels
    oad['plotOptions']['series']['dataLabels']['format'] = '{point.name}'

    # Axis-titles
    # X-axis
    oad['xAxis']['type'] = 'logarithmic'
    oad['xAxis']['minorTickInterval'] = 0.1
    oad['xAxis']['lineWidth'] = 2.5
    oad['xAxis']['gridLineWidth'] = 1.5

    oad['xAxis']['title']['text'] = xlabel
    oad['xAxis']['labels']['format'] = '{value:,.0f} '

    # Y-axis
    oad['yAxis']['title']['text'] = ylabel
    oad['yAxis']['labels']['format'] = '{value}%'

    # Tooltip
    oad['tooltip']['pointFormat'] = '<b>{point.name}</b><br>' + \
                                    x_tt + ': US${point.x:.0f}000<br>' + \
                                    z_tt + ': {point.z:.1f} TJ <br>' + \
                                    'Renewable & waste production: {point.custom.renew_deployed:.1f} TJ<br>' + \
                                    y_tt + ': {point.y:.1f}%<br>' + \
                                    '<br> {point.custom.mix_string}'

    oad['tooltip']['headerFormat'] = ''
    oad['tooltip']['footerFormat'] = ''

    # PLOTTING
    # ------------------------------------------------------------------------------------------------------------------
    options = HighchartsOptions.from_dict(oad)
    chart = Chart.from_options(options)

    return chart
