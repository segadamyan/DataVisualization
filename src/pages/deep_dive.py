from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from dash import dcc, html, Input, Output

dash.register_page(__name__, path="/deep-dive", name="Deep-Dive")

df = pd.read_csv(Path(__file__).parents[1] / "car_sales_dataset.csv", parse_dates=["Sale Date"])
df["Sale Month"] = df["Sale Date"].dt.to_period("M").dt.to_timestamp()

brands = sorted(df["Brand"].unique())
fuels = sorted(df["Fuel Type"].unique())
locations = sorted(df["Location"].unique())
max_km = int(df["Mileage (km)"].max())
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
max_price = int(df["Price (USD)"].max())

brand_dd = dcc.Dropdown(
    brands,
    id="brand-dd",
    placeholder="Select brand (optional)",
    clearable=True,
    className="mb-2",
)

fuel_cl = dbc.Checklist(
    options=[{"label": f, "value": f} for f in fuels],
    value=fuels,
    id="fuel-cl",
    inline=True,
    switch=True,
)

km_sl = dcc.RangeSlider(
    0,
    max_km,
    step=5000,
    value=[0, max_km],
    id="km-sl",
    marks=None,
    tooltip={"placement": "bottom", "always_visible": False},
)

year_sl = dcc.RangeSlider(
    min_year,
    max_year,
    step=1,
    value=[min_year, max_year],
    id="year-sl",
    marks=None,
    tooltip={"placement": "bottom", "always_visible": False},
)

price_sl = dcc.RangeSlider(
    0,
    max_price,
    step=1000,
    value=[0, max_price],
    id="price-sl",
    marks=None,
    tooltip={"placement": "bottom", "always_visible": False},
)

location_dd = dcc.Dropdown(
    locations,
    id="location-dd",
    placeholder="Location (optional)",
    clearable=True,
    className="mb-2",
)

control_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Filters", className="card-title"),
            brand_dd,
            html.Small("Fuel type:", className="d-inline-block me-2"),
            fuel_cl,
            html.Hr(),
            html.Small("Mileage range (km):"),
            km_sl,
            html.Small("Year of manufacture:"),
            year_sl,
            html.Small("Price range (USD):"),
            price_sl,
            location_dd,
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
                                dcc.Tab(label="Engine size vs Price", value="tab-engine"),
                                dcc.Tab(label="Monthly sales trend", value="tab-timeseries"),
                                dcc.Tab(label="Price by Brand", value="tab-box"),
                                dcc.Tab(label="Correlation heatmap", value="tab-corr"),
                            ],
                        ),
                        dcc.Loading(dcc.Graph(id="main-graph"), type="circle"),
                    ],
                    lg=9,
                    md=8,
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
    Output("year-sl", "value"),
    Output("price-sl", "value"),
    Output("location-dd", "value"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    """Return default values for all controls when the Reset button is pressed."""
    return None, fuels, [0, max_km], [min_year, max_year], [0, max_price], None


def _apply_filters(df_: pd.DataFrame, brand, fuel_list, km_range, year_range, price_range, location):
    """Utility function to apply all filters to the dataframe."""
    if brand:
        df_ = df_[df_["Brand"] == brand]
    if fuel_list:
        df_ = df_[df_["Fuel Type"].isin(fuel_list)]
    if location:
        df_ = df_[df_["Location"] == location]

    df_ = df_[
        (df_["Mileage (km)"] >= km_range[0]) & (df_["Mileage (km)"] <= km_range[1]) &
        (df_["Year"] >= year_range[0]) & (df_["Year"] <= year_range[1]) &
        (df_["Price (USD)"] >= price_range[0]) & (df_["Price (USD)"] <= price_range[1])
        ]
    return df_


@dash.callback(
    Output("main-graph", "figure"),
    Input("graph-tabs", "value"),
    Input("brand-dd", "value"),
    Input("fuel-cl", "value"),
    Input("km-sl", "value"),
    Input("year-sl", "value"),
    Input("price-sl", "value"),
    Input("location-dd", "value"),
)
def update_graph(active_tab, brand, fuel_list, km_range, year_range, price_range, location):
    """Return the appropriate Plotly figure based on the active tab and current filters."""

    dff = _apply_filters(df.copy(), brand, fuel_list, km_range, year_range, price_range, location)

    if active_tab == "tab-price":
        hist_data = [dff["Price (USD)"]]
        fig = ff.create_distplot(hist_data, group_labels=["Price (USD)"], bin_size=2000, show_rug=False)
        fig.update_layout(title_text="Price distribution (histogram + KDE)",
                          xaxis_title="Price (USD)", yaxis_title="Density")
        return fig

    if active_tab == "tab-scatter":
        fig = px.scatter(
            dff,
            x="Mileage (km)",
            y="Price (USD)",
            color="Fuel Type",
            hover_data=["Brand", "Model", "Year"],
            title="Mileage vs Price",
            template="plotly_white",
            opacity=0.7,
        )
        return fig

    if active_tab == "tab-engine":
        fig = px.scatter(
            dff,
            x="Engine Size (L)",
            y="Price (USD)",
            color="Fuel Type",
            hover_data=["Brand", "Model", "Year"],
            title="Engine size vs Price (L)",
            template="plotly_white",
            opacity=0.7,
        )
        return fig

    if active_tab == "tab-timeseries":
        ts = (
            dff.groupby("Sale Month", observed=True)["Price (USD)"].mean().reset_index(name="Average Price")
        )
        fig = px.line(ts, x="Sale Month", y="Average Price", title="Average sale price over time")
        fig.update_traces(mode="lines+markers")
        return fig

    if active_tab == "tab-box":
        fig = px.box(
            dff,
            x="Brand",
            y="Price (USD)",
            color="Brand",
            points="outliers",
            title="Price distribution by brand",
            template="plotly_white",
        )
        fig.update_layout(showlegend=False)
        return fig

    if active_tab == "tab-corr":
        num_cols = [
            "Price (USD)",
            "Discount (USD)",
            "Tax (USD)",
            "Mileage (km)",
            "Engine Size (L)",
            "Safety Rating",
            "Year",
        ]
        corr = dff[num_cols].corr().round(2)
        fig = go.Figure(
            data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                zmin=-1,
                zmax=1,
                colorbar_title="Correlation",
            )
        )
        fig.update_layout(title="Correlation heatmap of numeric variables")
        return fig

    return px.scatter()
