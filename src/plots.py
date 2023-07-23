from . import data_preparation as data_prep
from .data_classes import GDPData, GDPMetadata, IEAData

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go


def create_figure_widget(figure: go.Figure) -> go.FigureWidget:
    return go.FigureWidget(figure)


def electricity_plot(plot_year: int, gdp: GDPData, gdp_md: GDPMetadata, nrg_data: IEAData):
    """ Plots fraction of renewables as a function of GDP per capita (2015 US$) for a given plot year """

    # DATA PREPARATION
    # ------------------------------------------------------------------------------------------------------------------
    # Get all plottable country codes
    plot_country_codes = nrg_data.available_country_codes
    plot_country_codes.remove('WLD')

    colloquial_names = data_prep.create_colloquial_name_list(plot_country_codes, nrg_data)
    gdp_variable = 'GDP per capita (constant 2015 US$)'
    gdp_list = data_prep.create_gdp_dict([gdp_variable], plot_country_codes, plot_year, gdp)[gdp_variable]
    electricity_lists = data_prep.create_electricity_dict(plot_country_codes, plot_year, nrg_data)

    # PLOTTING
    # ------------------------------------------------------------------------------------------------------------------
    def tooltip_function(nuclear, renewable, fossil):
        return f'Fossil / Nuclear / Renewable: {fossil:.1f} / {nuclear:.1f} / {renewable:.1f} %'

    elec_cutoff = 3e5

    include_list = ['Norway', 'Iceland']
    exclude_list = ['Germany']

    cols = {'Code': plot_country_codes,
            'Country': colloquial_names,
            'GDP per capita (2015 US$)': gdp_list,
            'Total electricity consumption (GWh)': electricity_lists['Total'],
            'Size': 80 * electricity_lists['Total'] / np.max(electricity_lists['Total']),
            'Region': [gdp_md.get_region(country_code) for country_code in plot_country_codes],
            'label_text': [name if (elec > elec_cutoff and name not in exclude_list) or name in include_list else '' for
                           name, elec in zip(colloquial_names, electricity_lists['Total'])]}

    for key in ['Nuclear', 'Fossil fuels', 'Renewable sources']:
        cols |= {f'{key} fraction (%)': 100 * electricity_lists[key] / electricity_lists['Total']}

    cols['Energy mix'] = [tooltip_function(nuclear, renewable, fossil) for nuclear, renewable, fossil in
                          zip(cols['Nuclear fraction (%)'], cols['Renewable sources fraction (%)'],
                              cols['Fossil fuels fraction (%)'])]

    df = pd.DataFrame.from_dict(cols)

    hover_data = {}
    hover_data['GDP per capita (2015 US$)'] = ':.2f'
    hover_data['Total electricity consumption (GWh)'] = ':.2g'
    hover_data['Renewable sources fraction (%)'] = False
    hover_data['Size'] = False
    hover_data['Energy mix'] = True
    hover_data['Region'] = False

    scatter = px.scatter(df, x='GDP per capita (2015 US$)', y='Renewable sources fraction (%)',
                         size='Total electricity consumption (GWh)',
                         log_x=True, log_y=False, size_max=60,
                         color='Region', color_discrete_sequence=px.colors.qualitative.G10,
                         hover_name=colloquial_names,
                         hover_data=hover_data,
                         text='label_text',
                         title=f'Renewable fraction of electricity supply ({plot_year})'
                         )

    scatter.update_traces(textposition="middle center")

    scatter.update_layout(plot_bgcolor='white', font_family="Arial", font_color='black', font_size=14, title_font_size=20)

    scatter.update_xaxes(
        mirror=False,
        ticks='outside',
        zeroline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    scatter.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor=None,
        gridcolor='lightgrey'
    )

    scatter.add_annotation(dict(font=dict(color='black', size=11),
                                x=0,
                                y=0,
                                showarrow=False,
                                text="Based on World Bank and IEA data.<br>Creative Commons 4.0 License",
                                textangle=0,
                                xanchor='left',
                                align='left',
                                xref="x domain",
                                yref="y domain"))

    scatter.add_annotation(dict(font=dict(color='black', size=14),
                                x=0.02,
                                y=1.05,
                                showarrow=False,
                                text="Bubble size based on total electricity production.",
                                textangle=0,
                                xanchor='left',
                                align='left',
                                xref="x domain",
                                yref="y domain"))

    return scatter
