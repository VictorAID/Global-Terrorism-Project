import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc


df = pd.read_csv("GTD_Dataset.csv")


df = df[['eventid', 'iyear', 'imonth', 'iday', 'country_txt', 'region_txt', 'nkill',
         'attacktype1_txt', 'targtype1_txt', 'gname', 'weaptype1_txt', 'success',
         'crit1', 'latitude', 'longitude']]

df = df.rename(columns={'iyear': 'year', 'imonth': 'month', 'iday': 'day'})
df['month'] = df['month'].replace(0, 1)
df['day'] = df['day'].replace(0, 1)
df['date'] = pd.to_datetime(df[['year', 'month', 'day']])


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
app.title = "Global Terrorism One-Page Dashboard"


app.layout = html.Div([
    html.H1("🌍 Global Terrorism Dashboard", className="text-center my-4 text-primary"),

    
    dbc.Row([
        dbc.Col([
            html.Label("Select Region"),
            dcc.Dropdown(
                id='region-filter',
                options=[{'label': r, 'value': r} for r in sorted(df['region_txt'].unique())],
                multi=True,
                value=[]
            )
        ], width=3),

        dbc.Col([
            html.Label("Select Country"),
            dcc.Dropdown(
                id='country-filter',
                options=[{'label': c, 'value': c} for c in sorted(df['country_txt'].unique())],
                multi=True,
                value=[]
            )
        ], width=3),

        dbc.Col([
            html.Label("Select Attack Type"),
            dcc.Dropdown(
                id='attack-filter',
                options=[{'label': a, 'value': a} for a in sorted(df['attacktype1_txt'].unique())],
                multi=True,
                value=[]
            )
        ], width=3),

        dbc.Col([
            html.Label("Select Year"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': y, 'value': y} for y in range(1970, 2025)],
                multi=True,
                value=[2017]
            )
        ], width=3),
    ], className="mb-4"),

    
    dbc.Row(id='kpis', className='mb-4'),

    
    dbc.Container(id='charts-container', fluid=True)

], style={'padding': '20px'})



@app.callback(
    [Output('kpis', 'children'),
     Output('charts-container', 'children')],
    [Input('region-filter', 'value'),
     Input('country-filter', 'value'),
     Input('attack-filter', 'value'),
     Input('year-dropdown', 'value')]
)
def update_dashboard(regions, countries, attacks, years):
    dff = df[df['year'].isin(years)]

    if regions:
        dff = dff[dff['region_txt'].isin(regions)]
    if countries:
        dff = dff[dff['country_txt'].isin(countries)]
    if attacks:
        dff = dff[dff['attacktype1_txt'].isin(attacks)]

    
    total_attacks = len(dff)
    total_kills = int(dff['nkill'].sum())
    success_rate = round(dff['success'].mean() * 100, 2)

    kpi_cards = [
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Total Attacks", className="card-title"),
                html.H2(f"{total_attacks:,}", className="text-danger")
            ])
        ], className="shadow-lg"), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Total Fatalities", className="card-title"),
                html.H2(f"{total_kills:,}", className="text-warning")
            ])
        ], className="shadow-lg"), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Success Rate", className="card-title"),
                html.H2(f"{success_rate}%", className="text-success")
            ])
        ], className="shadow-lg"), width=4),
    ]

    
    charts = []

    
    yearly = dff.groupby('year').size().reset_index(name='Attacks')
    fig1 = px.line(yearly, x='year', y='Attacks', title="Yearly Attacks")
    charts.append(fig1)

    
    top_countries = dff['country_txt'].value_counts().nlargest(10).reset_index()
    top_countries.columns = ['country_txt', 'count']
    fig2 = px.bar(top_countries, x='country_txt', y='count', title="Top 10 Countries by Attacks")
    charts.append(fig2)

    
    attack_pie = dff['attacktype1_txt'].value_counts().reset_index()
    attack_pie.columns = ['attacktype1_txt', 'count']
    fig3 = px.pie(attack_pie, names='attacktype1_txt', values='count', title="Attack Types Distribution")
    charts.append(fig3)

    
    map_df = dff.dropna(subset=['latitude', 'longitude'])
    fig4 = px.scatter_mapbox(
        map_df, lat="latitude", lon="longitude", hover_name="country_txt",
        color="region_txt", zoom=1, height=500, mapbox_style="carto-positron",
        title="Attack Locations"
    )
    charts.append(fig4)

    
    chart_rows = []
    for i in range(0, len(charts), 2):
        row = dbc.Row([
            dbc.Col(dcc.Graph(figure=charts[i]), width=6, className='mb-4 shadow'),
            dbc.Col(dcc.Graph(figure=charts[i+1]), width=6, className='mb-4 shadow') if i+1 < len(charts) else None
        ])
        chart_rows.append(row)

    return kpi_cards, chart_rows


if __name__ == '__main__':
    app.run(debug=False)
