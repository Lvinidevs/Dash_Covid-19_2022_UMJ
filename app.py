#  Projeto baseado no painel construido pelo Aismov Academy
#  python app.py runserver
import dash
import dash_html_components as html 
import dash_core_components as dcc 
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
CENTER_LAT, CENTER_LON = -14.272572694355336, -51.25567404158474
#Base
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
import pandas as pd
df = pd.read_csv("HIST_PAINEL_COVIDBR_27dez2022.csv", sep=";")
df_states = df[(~df["estado"].isna() & (df["codmun"].isna()))]
df_states_ = df_states[df_states["data"] == "2022-05-23"]
df_brasil = df[df["regiao"] == "Brasil"]
brazil_states = json.load(open("geojson/brazil_geo.json", "r")) 
df_data = df_states[df_states["estado"]=="AL"] 
select_columns = {"casosAcumulado": "Casos Acumulados",
                    "casosNovos": "Novos Casos",
                    "obitosAcumulado": "Óbitos totais",
                    "obitosNovos": "Óbitos por dia"
}
#Figura
fig = px.choropleth_mapbox(df_states, locations="estado", color="casosNovos", 
                            center={"lat": -16.95, "lon": -47.78}, opacity=0.4,
                            geojson=brazil_states, color_continuous_scale="Redor",
                            hover_data={"casosAcumulado": True, "casosNovos": True, "estado": True})
fig.update_layout(
    paper_bgcolor="#000000",
    autosize=True,
    showlegend=False,
    margin=go.Margin(l=0, r=0, t=0, b=0),
    mapbox_style="carto-darkmatter"
)
fig2 = go.Figure(layout={"template":"plotly_dark"})
fig2.add_trace(go.Scatter(x=df_data["data"], y=df_data["casosAcumulado"]))
fig2.update_layout(
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10)
)
#Layout
app.layout = html.Div([
        dbc.Row(dbc.Col(html.Div("UMJ🔹EAD| PAINEL COVID-19 BRASIL"),
        style={"padding":"15px", "background-color":"black", "color":"white","text-align": "center"}),
        ),
        dbc.Col([html.Div([
                    dbc.Button("BRASIL", color="primary", id="location-button", size="lg"),
                    html.P("Selecione o tipo de dado que deseja visualizar:", style={"margin-top": "20px"}),
                    dcc.Dropdown(id="location-dropdown", options=[{"label": j, "value": i} for i, j in select_columns.items()],
                    value= "casosNovos",
                    style={"margin-top": "10px"}
                    ),
                ])]),
        dbc.Row(
            dbc.Col([
                dcc.Loading(id="loading-1", type="default", children=[dcc.Graph(id="choropleth-map", figure=fig, style={"height": "50vh"})])
                
                ],
            ),
        ),
        dbc.Row(
            [
                dbc.Col([
                    dbc.Card([dbc.CardBody([html.Span("Casos recuperados"),html.H3(style={"color": "green"}, id="casos-recuperados-text"),html.Span("Em acompanhamentos"),html.H5(style={"color": "green"}, id="em-acompanhamento-text"),
                    ])],color="light", outline=True, style={"margin-top":"10px", "box-shadow":"0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.15)", "color":"#ffffff"})
                ],md=4),
                dbc.Col([
                    dbc.Card([dbc.CardBody([html.Span("Casos confirmados totais"),html.H3(style={"color": "blue"}, id="casos-confirmados-text"),html.Span("Novos casos na data"),html.H5(style={"color": "blue"}, id="novos-casos-text"),
                    ])],color="light", outline=True, style={"margin-top":"10px", "box-shadow":"0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.15)", "color":"#ffffff"})
                ],md=4),
                dbc.Col([
                    dbc.Card([dbc.CardBody([html.Span("Óbitos confirmados"),html.H3(style={"color": "red"}, id="obitos-text"),html.Span("Óbitos na data"),html.H5(style={"color": "red"}, id="obitos-na-data-text"),
                    ])],color="light", outline=True, style={"margin-top":"10px", "box-shadow":"0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.15)", "color":"#ffffff"})
                ],md=4),
                dbc.Col([
                    html.P("Selecione a data na qual deseja obter informações:", style={"margin-top": "20px"}),
                    html.Div(id="div-test", children=[
                    dcc.DatePickerSingle(
                    id="date-picker",
                    min_date_allowed=df_brasil["data"].min(),
                    max_date_allowed=df_brasil["data"].max(),
                    initial_visible_month=df_brasil["data"].min(),
                    date=df_brasil["data"].max(),
                    display_format="MMMM D, YYYY",
                    style={"border": "0px solid black", "width": "100%"}
                    ),
                    ]),
                    dcc.Graph(id="line-graph", figure=fig2, style={"height":"400px", "width":"100%"})
                    ]),
            ]
        ),
    ]
)
#Functions
@app.callback(
    [
        Output("casos-recuperados-text", "children"),
        Output("em-acompanhamento-text", "children"),
        Output("casos-confirmados-text", "children"),
        Output("novos-casos-text", "children"),
        Output("obitos-text", "children"),
        Output("obitos-na-data-text", "children"),
    ], [Input("date-picker", "date"), Input("location-button", "children")]
)
def display_status(date, location):
    # print(location, date)
    if location == "BRASIL":
        df_data_on_date = df_brasil[df_brasil["data"] == date]
    else:
        df_data_on_date = df_states[(df_states["estado"] == location) & (df_states["data"] == date)]

    recuperados_novos = "-" if df_data_on_date["Recuperadosnovos"].isna().values[0] else f'{int(df_data_on_date["Recuperadosnovos"].values[0]):,}'.replace(",", ".") 
    acompanhamentos_novos = "-" if df_data_on_date["emAcompanhamentoNovos"].isna().values[0]  else f'{int(df_data_on_date["emAcompanhamentoNovos"].values[0]):,}'.replace(",", ".") 
    casos_acumulados = "-" if df_data_on_date["casosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["casosAcumulado"].values[0]):,}'.replace(",", ".") 
    casos_novos = "-" if df_data_on_date["casosNovos"].isna().values[0]  else f'{int(df_data_on_date["casosNovos"].values[0]):,}'.replace(",", ".") 
    obitos_acumulado = "-" if df_data_on_date["obitosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["obitosAcumulado"].values[0]):,}'.replace(",", ".") 
    obitos_novos = "-" if df_data_on_date["obitosNovos"].isna().values[0]  else f'{int(df_data_on_date["obitosNovos"].values[0]):,}'.replace(",", ".") 
    return (
            recuperados_novos, 
            acompanhamentos_novos, 
            casos_acumulados, 
            casos_novos, 
            obitos_acumulado, 
            obitos_novos,
            )
@app.callback(
        Output("line-graph", "figure"),
        [Input("location-dropdown", "value"), Input("location-button", "children")]
)
def plot_line_graph(plot_type, location):
    if location == "BRASIL":
        df_data_on_location = df_brasil.copy()
    else:
        df_data_on_location = df_states[(df_states["estado"] == location)]
    fig2 = go.Figure(layout={"template":"plotly_dark"})
    bar_plots = ["casosNovos", "obitosNovos"]

    if plot_type in bar_plots:
        fig2.add_trace(go.Bar(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))
    else:
        fig2.add_trace(go.Scatter(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))
    
    fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, b=10, t=10),
        )
    return fig2


@app.callback(
    Output("choropleth-map", "figure"), 
    [Input("date-picker", "date")]
)
def update_map(date):
    df_data_on_states = df_states[df_states["data"] == date]

    fig = px.choropleth_mapbox(df_data_on_states, locations="estado", geojson=brazil_states, 
        center={"lat": CENTER_LAT, "lon": CENTER_LON},  # https://www.google.com/maps/ -> right click -> get lat/lon
        zoom=4, color="casosAcumulado", color_continuous_scale="Redor", opacity=0.55,
        hover_data={"casosAcumulado": True, "casosNovos": True, "obitosNovos": True, "estado": False}
        )

    fig.update_layout(paper_bgcolor="#242424", mapbox_style="carto-darkmatter", autosize=True,
                    margin=go.layout.Margin(l=0, r=0, t=0, b=0), showlegend=False)
    return fig


@app.callback(
    Output("location-button", "children"),
    [Input("choropleth-map", "clickData"), Input("location-button", "n_clicks")]
)
def update_location(click_data, n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if click_data is not None and changed_id != "location-button.n_clicks":
        state = click_data["points"][0]["location"]
        return "{}".format(state)
    
    else:
        return "BRASIL"


if __name__ == '__main__':
    app.run_server(debug=True)




