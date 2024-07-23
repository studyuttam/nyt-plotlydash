import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
from dash import dash_table


df = pd.read_excel('Data/disabilitycensus2021_cleaned.xlsx')

#Summarized data
df_summ = pd.read_excel('Data/summarised_population.xlsx')
df_summ['Percentage'] = df_summ['Percentage'].round(2)

# Calculate the average percentage for each age group
average_percentage_by_age_group = df_summ.groupby('Age')['Percentage'].mean().reset_index()

# Initialize an empty list for conditional styles
style_data_conditional = []

# Generate conditional styles for each age group
for index, row in average_percentage_by_age_group.iterrows():
    style_data_conditional.append({
        'if': {
            'filter_query': '{{Age}} = "{}" && {{Percentage}} > {}'.format(row['Age'], row['Percentage']),
            'column_id': 'Percentage'
        },
        'backgroundColor': 'tomato',
        'color': 'white'
    }),

app = dash.Dash( external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div([
    html.Div("NYT Dashboard", style={'fontSize': 50, 'textAlign': 'center', 'color': 'white', 'backgroundColor': 'Green'}),
    dcc.Tabs([
        dcc.Tab(label='Census 2021', children=[
            html.Div([
                html.Div([
                    html.Label('Select Local Authority', style={'fontWeight': 'bold'}),
                    dcc.Dropdown([la for la in df['Local Authority'].unique()], id='la-choice',
                                 style={'width':'100%'}, multi=True, value=['Brent']),
                        ],
                        style={'width':'48%', 'display': 'inline-block'}
                        ),
                html.Div([
                    html.Label('Select Age', style={'fontWeight': 'bold'}),
                    dcc.Dropdown([ag for ag in df['Age'].unique()], id='ag-choice', multi=True, value=['15 to 19'],
                                     style={'width':'100%'}),
                    ],
                    style={'width':'48%', 'display': 'inline-block', 'marginLeft': '4%'}
                    ),
            ],
            style={'display': 'flex'}),
        
        # Card to display total population
        html.Div([
            # Card to display total population
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Population", className="card-title"),
                    # Placeholder for dynamic total population
                    html.P(id="total-population-placeholder", className="card-text"),
                    ]),
                ],
                style={"width": "18rem", "marginTop": "20px", "marginRight": "10px", "border": "5px solid #000 !important"},  # Adjust styling as needed
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H4("Disabled Population", className="card-title"),
                             # Placeholder for dynamic total population
                            html.P(id="disabled-population-placeholder", className="card-text"),
                        ]
                    ),
                ],
                style={"width": "18rem", "marginTop": "20px","border": "5px solid #000 !important"},  # Adjust styling as needed
            )], 
            style={"display":"flex"}
            ),
            # Inside your layout definition
html.Div([
    dbc.Row([  # This Row wraps all three charts
        dbc.Col([  # First column for the pie chart
            dcc.Graph(id='disability-by-sex-chart')
        ], width=4),  # Adjust 'width' as needed to size the pie chart column
        dbc.Col([  # Second column for another chart
            dcc.Graph(id='disability-by-category-chart')  # Placeholder ID, replace with actual
        ], width=4),  # Adjust 'width' as needed
        dbc.Col([  # Third column for another chart
            dcc.Graph(id='population-bar-chart')  # Placeholder ID, replace with actual
        ], width=4),  # Adjust 'width' as needed
    ], style={"display": "flex", "justify-content": "center"}),  # Adjust styling as needed
    # Other components can follow here
]),
html.Div([
    dbc.Row([  
        dbc.Col([  # First column for the pie chart
            dcc.Graph(id='agegroup-scatter-plot', style={'height': '500px'}),
            html.Div(style={'height': '50px'})
        ], width=6),  # Adjust 'width' as needed to size the pie chart column
        dbc.Col([  # Second column for Data Table
            html.H3('Data Table for Disabled Population by Age Group', style={'textAlign': 'center'}),
            dash_table.DataTable(
                id='datatable-agegroup',
    style_data_conditional=style_data_conditional,
    sort_action='native',
    filter_action="native",
    filter_options={"placeholder_text": "Filter column..."},
    style_data={
        'color': 'black',
        'whiteSpace': 'normal',
        'height': 'auto',
    },
    columns=[{"name": i, "id": i} for i in df_summ.columns],
    page_size=10)

        ], width=6),  # Adjust 'width' as needed
    ], style={"display": "flex", "justify-content": "center"}),  # Adjust styling as needed
    # Other components can follow here
]
),
# Empty Div added at the bottom with a height of 50px (adjust as needed)
    html.Div(style={'height': '50px'})

        ]),

        dcc.Tab(label='SEN', children=[
            html.H3('Work in Progress...'),
            # Add other components or figures for this tab
        ]),
            
    ])

])

@app.callback(
    Output('total-population-placeholder', 'children'),
    [
        Input('la-choice', 'value'),
        Input('ag-choice', 'value'),
    ]
)
def update_total_population(selected_la, selected_ag):
    if selected_la is None:
        # If no region is selected, calculate total population of all regions
        total_population = df['Population'].sum()
    else:
        # Calculate total population for selected regions
         filtered_df = df[(df['Local Authority'].isin(selected_la))
                          & (df['Age'].isin(selected_ag))
                          & (df['Sex'].isin(['Male','Female']))
                          & (df['Disability Status'].isin(['Disabled; limited a lot']))]
         total_population = filtered_df['Population'].sum()
        

    return  f'{total_population}'

@app.callback(
    
     Output('disabled-population-placeholder', 'children'),
    [
        Input('la-choice', 'value'),
        Input('ag-choice', 'value'),
    ]
)
def update_total_population(selected_la, selected_ag):
    
    disabled_population_df = df[(df['Local Authority'].isin(selected_la))
                          & (df['Age'].isin(selected_ag))
                          & (df['Category'] == 'Four category')
                          & (df['Sex'].isin(['Male','Female']))
                          & (df['Disability Status'].isin(['Disabled; limited a lot','Disabled; limited a little']))]
    disabled_population = disabled_population_df['Count'].sum()

    return  f'{disabled_population}'

@app.callback(
    Output('disability-by-sex-chart', 'figure'),
    [Input('la-choice', 'value'),
    Input('ag-choice', 'value'),]
)
def update_pie_chart(selected_la, selected_ag):
    # Example data update based on selected category
    
    disabled_population_df = df[(df['Local Authority'].isin(selected_la))
                          & (df['Age'].isin(selected_ag))
                          & (df['Category'] == 'Four category')
                          & (df['Sex'].isin(['Male','Female']))
                          & (df['Disability Status'].isin(['Disabled; limited a lot','Disabled; limited a little']))]
    
    # Group by 'Sex' and sum 'Count'
    grouped_data = disabled_population_df.groupby('Sex')['Count'].sum()
    
    
    labels = grouped_data.index.tolist()  # Convert index to list for labels
    values = grouped_data.values.tolist()  # Convert values to list
    
    # Update the pie chart
    new_figure = {
        'data': [
            go.Pie(labels=labels, 
                   values=values, 
                   hole=.3,
                   hoverinfo='label+percent+value')
        ],
        'layout': {
            'title': 'Disability by Sex for '
        }
    }
    return new_figure
@app.callback(
    Output('disability-by-category-chart', 'figure'),
    [Input('la-choice', 'value'),
    Input('ag-choice', 'value'),]
)
def update_pie_chart_by_category(selected_la, selected_ag):
    # Example data update based on selected category
    
    poulation_grpby_category = df[(df['Local Authority'].isin(selected_la))
                          & (df['Age'].isin(selected_ag))
                          & (df['Category'] == 'Four category')
                          & (df['Sex'].isin(['Male','Female']))
                          ]
    data = poulation_grpby_category.groupby('Disability Status')['Count'].sum().reset_index()
    
    
    labels = data['Disability Status'].tolist()  # Convert index to list for labels
    values = data['Count'].tolist()  # Convert values to list
    
    # Update the pie chart
    new_figure = {
        'data': [
            go.Pie(labels=labels, 
                   values=values, 
                   hole=.3,
                   hoverinfo='label+percent+value')
        ],
        'layout': {
            'title': {
                'text': 'Disability by Status',
                  'x': 0.3,  # Centers the title
                  'xanchor': 'Left'  # Ensures the center is the anchor point
                    },
            'width':650,
            'height':500
        }
    }
    return new_figure
@app.callback(
    Output('population-bar-chart', 'figure'),  # Assume there's an element with ID 'population-bar-chart' to display the bar chart
    [Input('la-choice', 'value'),  # Assuming these are the dropdowns or inputs that determine the selection
     Input('ag-choice', 'value')]
)
def update_population_bar_chart(selected_la, selected_ag):
    
    filtered_df = df[(df['Local Authority'].isin(selected_la))
                          & (df['Age'].isin(selected_ag))
                          & (df['Sex'].isin(['Male','Female']))
                          & (df['Disability Status'].isin(['Disabled; limited a lot']))]
    total_population = filtered_df['Population'].sum()

    disabled_population_df = df[(df['Local Authority'].isin(selected_la))
                          & (df['Age'].isin(selected_ag))
                          & (df['Category'] == 'Four category')
                          & (df['Sex'].isin(['Male','Female']))
                          & (df['Disability Status'].isin(['Disabled; limited a lot','Disabled; limited a little']))]
    disabled_population = disabled_population_df['Count'].sum()
    
    # Data for the bar plot
    categories = ['Total Population', 'Disabled Population']
    values = [total_population, disabled_population]
    
    # Create the bar plot
    figure = {
        'data': [
            {'type': 'bar',
             'x': categories,
             'y': values,
             'marker': {'color': ['blue', 'orange']}}  # Optional: Use different colors for the bars
        ],
        'layout': {
            'title': 'Total vs Disabled Population',
            'xaxis': {'title': 'Category'},
            'yaxis': {'title': 'Population Count'}
        }
    }
    
    return figure

@app.callback(
    [Output('agegroup-scatter-plot', 'figure'),
     Output('datatable-agegroup', 'data')],
    [Input('la-choice', 'value'),
        Input('ag-choice', 'value')]
)
def update_scatter_and_datatable(selected_la, selected_ag):
    # Filter the DataFrame for the selected age group
    filtered_df = df[(df['Age'].isin(selected_ag))
                     & (df['Sex'].isin(['Male', 'Female']))
                     & (df['Disability Status'].isin(['Disabled; limited a lot']))]
    
    selected_borough = selected_la
    # Group by 'Local Authority' and sum the populations and the disabled count
    grouped_df = filtered_df.groupby('Local Authority', as_index=False).agg({'Population': 'sum', 'Count': 'sum'})
    
    # Create the scatter plot figure with marker size based on the disabled population count
    fig = {
        'data': [{
            'x': grouped_df['Local Authority'],
            'y': grouped_df['Population'],
            'type': 'scatter',
            'mode': 'markers',
            # Adjust marker size based on the 'Count' column, possibly scaled for better visualization
            'marker': {'size': grouped_df['Count'] / grouped_df['Count'].max() * 50,
                       'color': ['red' if la in selected_la else 'blue' for la in grouped_df['Local Authority']]
                       }  # Example scaling
            
        }],
        'layout': {
            'title': 'Population vs. Disabled Population Count by Local Authority',
            'margin': {'l': 60, 'r': 40, 't': 40, 'b': 170},  # Adjust 'b' (bottom) as needed
            'xaxis': {'title': 'Local Authority',
                     'title_standoff': 150,
                     },
            'yaxis': {'title': 'Total Population'},
            'plot_bgcolor': 'lightgrey'
        }
    }

    data = df_summ[df_summ['Age'].isin(selected_ag)].to_dict('records')
    
    return fig, data



if __name__ == '__main__':
    app.run_server(debug=True)
