# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'ALL', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}

                                    ],
                                    value='ALL',
                                    placeholder='Select site to see detailed statistics',
                                    searchable=True

                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        # Calculate number of successful launches for each launch site
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size()

        # Create pie chart showing distribution of successful launches across launch sites
        fig = px.pie(names=success_counts.index,
                     values=success_counts.values,
                     color = success_counts.index,
                     color_discrete_map={
                                'CCAFS LC-40':'lightcyan',
                                'VAFB SLC-4E':'cyan',
                                'CCAFS SLC-40':'royalblue',
                                'KSC LC-39A':'darkblue'},
                     title='Distribution of Successful Launches Across Launch Sites'
                     )

        return fig

    else:

        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        successes = site_df[site_df['class'] == 1]['class'].count()
        failures = site_df[site_df['class'] == 0]['class'].count()

        fig = px.pie(names=['Success', 'Failure'],
                     values=[successes, failures],
                     title='Total Success Launches on {}'.format(entered_site),
                     color=['Success', 'Failure'],
                     color_discrete_map={'Success': 'cyan', 'Failure': 'darkblue'})

        return fig
        # return the outcomes piechart for a selected site


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    if entered_site == 'ALL':
        minimum_payload = payload_range[0]
        maximum_payload = payload_range[1]
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= minimum_payload) &
                                (spacex_df['Payload Mass (kg)'] <= maximum_payload)]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between payload and success rate for all sites'
        )
    else:
        minimum_payload = payload_range[0]
        maximum_payload = payload_range[1]
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = site_df[(site_df['Payload Mass (kg)'] >= minimum_payload) &
                              (site_df['Payload Mass (kg)'] <= maximum_payload)]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between payload and success rate for site {} (Payload Range: {} - {})'.format(
                entered_site, minimum_payload, maximum_payload)
        )

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
