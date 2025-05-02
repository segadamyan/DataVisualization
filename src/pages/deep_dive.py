from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
from components.controls import brand_dropdown, fuel_checklist, km_slider
from dash import dcc, html, Input, Output

dash.register_page(__name__, path="/deep-dive", name="Deep-dive")

df = pd.read_csv(Path(__file__).parents[1] / "car_sales_dataset.csv", parse_dates=["Sale Date"])
df["Sale Month"] = df["Sale Date"].dt.to_period("M").dt.to_timestamp()

brands = df["Brand"].unique()
fuels = df["Fuel Type"].unique()
max_km = int(df["Mileage (km)"].max())

control_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Filters", className="card-title"),
            brand_dropdown(brands),
            html.Small("Fuel type:", className="d-inline-block me-2"),
            fuel_checklist(fuels),
            html.Hr(),
            html.Small("Mileage range (km):"),
            km_slider(max_km),
            dbc.Button("Reset", id="reset-btn", color="secondary", outline=True, className="mt-3"),
        ]
    ),
    className="mb-3 shadow-sm",
)

layout = dbc.Container(
    [
        html.H2("Interactive analytics", className="mt-3"),
        dbc.Row(
            [
                dbc.Col(control_card, lg=3, md=4),
                dbc.Col(
                    [
                        dcc.Tabs(
                            id="graph-tabs",
                            value="tab-price",
                            children=[
                                dcc.Tab(label="Price distribution", value="tab-price"),
                                dcc.Tab(label="Mileage vs Price", value="tab-scatter"),
                            ],
                        ),
                        dcc.Loading(dcc.Graph(id="main-graph"), type="circle"),
                    ],
                    lg=9, md=8,
                ),
            ],
            className="g-2",
        ),
    ],
    fluid=True,
)


@dash.callback(
    Output("brand-dd", "value"),
    Output("fuel-cl", "value"),
    Output("km-sl", "value"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return None, list(fuels), [0, max_km]


@dash.callback(
    Output("main-graph", "figure"),
    Input("graph-tabs", "value"),
    Input("brand-dd", "value"),
    Input("fuel-cl", "value"),
    Input("km-sl", "value"),
)
def update_graph(active_tab, brand, fuel_list, km_range):
    dff = df.copy()
    if brand:
        dff = dff[dff["Brand"] == brand]
    if fuel_list:
        dff = dff[dff["Fuel Type"].isin(fuel_list)]
    dff = dff[
        (dff["Mileage (km)"] >= km_range[0]) &
        (dff["Mileage (km)"] <= km_range[1])
        ]

    if active_tab == "tab-price":
        hist_data = [dff["Price (USD)"]]
        fig = ff.create_distplot(hist_data, group_labels=["Price (USD)"], bin_size=2000, show_rug=False)
        fig.update_layout(title_text="Price distribution (histogram + KDE)",
                          xaxis_title="Price (USD)", yaxis_title="Density")
        return fig

    if active_tab == "tab-scatter":
        fig = px.scatter(
            dff, x="Mileage (km)", y="Price (USD)", color="Fuel Type",
            hover_data=["Brand", "Model", "Year"],
            title="Mileage vs Price (color = fuel type)",
            template="plotly_white",
            opacity=0.7,
        )
        return fig

    return px.scatter()
