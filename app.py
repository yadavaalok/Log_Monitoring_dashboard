import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime


# Load data
def load_data():
    conn = sqlite3.connect('logs.db')
    df = pd.read_sql_query("SELECT * FROM api_logs", conn)
    conn.close()
    return df


# App
app = dash.Dash(__name__)
app.title = "API Log Monitoring Dashboard"

df = load_data()

# App Layout
app.layout = html.Div([
    html.H1("🚀 API Log Monitoring Dashboard", style={'textAlign': 'center'}),

    html.Div([
        dcc.Dropdown(
            id='endpoint-filter',
            options=[{'label': ep, 'value': ep} for ep in sorted(df['api_endpoint'].unique())],
            placeholder="Select API Endpoint",
            style={'width': '30%', 'display': 'inline-block', 'marginRight': '10px'}
        ),
        dcc.Dropdown(
            id='status-filter',
            options=[
                {'label': 'Success (2xx)', 'value': 'success'},
                {'label': 'Failure (4xx/5xx)', 'value': 'failure'}
            ],
            placeholder="Select Status",
            style={'width': '30%', 'display': 'inline-block', 'marginRight': '10px'}
        ),
        dcc.DatePickerRange(
            id='date-range',
            start_date=df['timestamp'].min(),
            end_date=df['timestamp'].max(),
            display_format='YYYY-MM-DD',
            style={'marginTop': '10px'}
        )
    ], style={'padding': '20px'}),

    html.Div(id='kpi-cards', style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}),

    dcc.Graph(id='requests-trend-graph', style={'marginTop': '20px'}),

    html.H2("📜 Logs", style={'paddingTop': '20px'}),

    dash_table.DataTable(
        id='logs-table',
        columns=[
            {"name": "Timestamp", "id": "timestamp"},
            {"name": "API Endpoint", "id": "api_endpoint"},
            {"name": "Status Code", "id": "status_code"}
        ],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        row_selectable='single'
    ),

    html.Div(id='log-detail', style={'padding': '20px', 'marginTop': '20px', 'border': '1px solid #ccc'})
])


# Callbacks
@app.callback(
    [Output('kpi-cards', 'children'),
     Output('requests-trend-graph', 'figure'),
     Output('logs-table', 'data')],
    [Input('endpoint-filter', 'value'),
     Input('status-filter', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_dashboard(endpoint, status_type, start_date, end_date):
    dff = load_data()

    # Apply filters
    if endpoint:
        dff = dff[dff['api_endpoint'] == endpoint]
    if status_type == 'success':
        dff = dff[dff['status_code'].between(200, 299)]
    elif status_type == 'failure':
        dff = dff[dff['status_code'] >= 400]

    if start_date and end_date:
        dff = dff[(dff['timestamp'] >= start_date) & (dff['timestamp'] <= end_date)]

    # KPIs
    total_requests = len(dff)
    successful_requests = len(dff[dff['status_code'].between(200, 299)])
    failed_requests = len(dff[dff['status_code'] >= 400])

    kpi_cards = [
        html.Div([
            html.H3("Total Requests"),
            html.P(total_requests)
        ], style={'padding': '10px', 'border': '1px solid gray', 'borderRadius': '5px', 'width': '20%',
                  'textAlign': 'center'}),

        html.Div([
            html.H3("Success Requests"),
            html.P(successful_requests)
        ], style={'padding': '10px', 'border': '1px solid green', 'borderRadius': '5px', 'width': '20%',
                  'textAlign': 'center'}),

        html.Div([
            html.H3("Failed Requests"),
            html.P(failed_requests)
        ], style={'padding': '10px', 'border': '1px solid red', 'borderRadius': '5px', 'width': '20%',
                  'textAlign': 'center'}),
    ]

    # Trend Graph
    fig = px.histogram(
        dff,
        x='timestamp',
        color='status_code',
        nbins=50,
        title="Request Trend Over Time"
    )
    fig.update_layout(bargap=0.2, xaxis_title="Timestamp", yaxis_title="Request Count")

    return kpi_cards, fig, dff.to_dict('records')


# Callback to show log details when a row is selected
@app.callback(
    Output('log-detail', 'children'),
    [Input('logs-table', 'selected_rows')],
    [State('logs-table', 'data')]
)
def display_log_detail(selected_rows, table_data):
    if selected_rows is None or len(selected_rows) == 0:
        return "Select a log row to see full details."

    row = table_data[selected_rows[0]]
    details = [
        html.H3("Log Details"),
        html.P(f"Timestamp: {row['timestamp']}"),
        html.P(f"API Endpoint: {row['api_endpoint']}"),
        html.P(f"Status Code: {row['status_code']}"),
        html.Pre(f"Request Payload: {row.get('request_payload', '{}')}"),
        html.Pre(f"Response Payload: {row.get('response_payload', '{}')}"),
        html.Pre(f"Error Message: {row.get('error_message', 'None')}")
    ]
    return details


# Run server
if __name__ == '__main__':
    app.run(debug=True)
