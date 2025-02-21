#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the dataset
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Convert Date column to datetime format
data['Date'] = pd.to_datetime(data['Date'])
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month

# Filter data between 1980 and 2013
data = data[(data['Year'] >= 1980) & (data['Year'] <= 2013)]

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "Automobile Statistics Dashboard"

# Dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'yearly'},
    {'label': 'Recession Period Statistics', 'value': 'recession'}
]

# List of years 
year_list = [{'label': str(i), 'value': i} for i in range(1980, 2014)]  # Stops at 2013

# Layout of the app
app.layout = html.Div([
    # TASK 2.1: Dashboard Title
    html.H1(
        "Automobile Sales Dashboard",
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'fontSize': '24px',
            'fontFamily': 'Roboto'
        }
    ),

    # TASK 2.2: Dropdown Menus
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='report_type',
            options=dropdown_options,
            value='yearly',
            placeholder='Select a report type',
            style={
                'width': '80%', 
                'padding': '3px', 
                'fontSize': '20px',
                'fontFamily': 'Roboto',
                'textAlignLast': 'center'
            }
        )
    ], style={'width': '50%', 'margin': 'auto'}),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=year_list,
            value=1980,
            style={
                'width': '80%', 
                'padding': '3px', 
                'fontSize': '20px',
                'fontFamily': 'Roboto',
                'textAlignLast': 'center'
            }
        )
    ], style={'width': '50%', 'margin': 'auto'}),

    # TASK 2.3: Output Container for Graphs
    html.Div(id='output-container', className='output-container', style={'padding': '20px'})
])

# TASK 2.4: Enable/disable year dropdown based on report selection
@app.callback(
    Output('select-year', 'disabled'),
    Input('report_type', 'value')
)
def update_input_container(selected_statistics):
    return selected_statistics == 'recession'  # Disable year dropdown if 'Recession' is selected

# TASK 2.5 & TASK 2.6: Callback for Plotting Graphs
@app.callback(
    Output('output-container', 'children'),
    [Input('report_type', 'value'), Input('select-year', 'value')]
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'recession':
        # Filter data for recession periods
        recession_data = data[data['Recession'] == 1]

        # Plot 1: Automobile sales fluctuation over Recession Period (year-wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, 
                x='Year',
                y='Automobile_Sales',
                title="Average Automobile Sales Fluctuation Over Recession Period"))

        # Plot 2: Average number of vehicles sold by vehicle type       
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title="Average Number of Vehicles Sold by Vehicle Type (Recession)"))

        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec,
                names='Vehicle_Type',
                values='Advertising_Expenditure',
                title="Total Expenditure Share by Vehicle Type During Recession"))

        # Plot 4: Bar chart for effect of unemployment rate on vehicle type and sales
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data,
                x='unemployment_rate',
                y='Automobile_Sales',
                color='Vehicle_Type',
                labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                title="Effect of Unemployment Rate on Vehicle Type and Sales"))

        return [
            html.Div(children=[R_chart1, R_chart2], style={'display': 'flex'}),
            html.Div(children=[R_chart3, R_chart4], style={'display': 'flex'})
        ]

    elif input_year and selected_statistics == 'yearly':
        yearly_data = data[data['Year'] == input_year]
                              
        # Plot 1: Yearly Automobile sales trend
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas,
                x='Year',
                y='Automobile_Sales',
                title="Yearly Automobile Sales Trend"))

        # Plot 2: Total Monthly Automobile sales
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(mas,
                x='Month',
                y='Automobile_Sales',
                title=f"Total Monthly Automobile Sales in {input_year}"))

        # Plot 3: Bar chart for average number of vehicles sold during the given year
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title=f"Average Vehicles Sold by Vehicle Type in {input_year}"))

        # Plot 4: Pie chart for total advertisement expenditure per vehicle type
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data,
                names='Vehicle_Type',
                values='Advertising_Expenditure',
                title=f"Total Advertisement Expenditure for Each Vehicle Type in {input_year}"))

        return [
            html.Div(children=[Y_chart1, Y_chart2], style={'display': 'flex'}),
            html.Div(children=[Y_chart3, Y_chart4], style={'display': 'flex'})
        ]
    
    else:
        return None

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
