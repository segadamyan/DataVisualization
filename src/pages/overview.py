from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html

dash.register_page(__name__, path="/")

df = pd.read_csv(Path(__file__).parents[1] / "car_sales_dataset.csv", parse_dates=["Sale Date"])
df["Sale Month"] = df["Sale Date"].dt.to_period("M").dt.to_timestamp()

sales_per_month = (
    df.groupby("Sale Month")
    .size()
    .reset_index(name="Sales")
    .sort_values("Sale Month")
)

fig_sales = px.line(
    sales_per_month, x="Sale Month", y="Sales",
    markers=True, title="Monthly car sales trend",
    template="plotly_white",
)

layout = dbc.Container(
    [
        html.H2("Key Highlights", className="mt-3"),
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    dbc.CardBody([
                        html.H4(f"{df.shape[0]:,}", className="card-title"),
                        html.P("Total cars sold", className="card-text"),
                    ]), color="success", inverse=True
                ), lg=3),
                dbc.Col(dbc.Card(
                    dbc.CardBody([
                        html.H4(f"${df['Price (USD)'].mean():,.0f}", className="card-title"),
                        html.P("Average selling price", className="card-text"),
                    ]), color="info", inverse=True
                ), lg=3),
                dbc.Col(dbc.Card(
                    dbc.CardBody([
                        html.H4(f"{df['Brand'].nunique()}", className="card-title"),
                        html.P("Brands represented", className="card-text"),
                    ]), color="primary", inverse=True
                ), lg=3),
                dbc.Col(dbc.Card(
                    dbc.CardBody([
                        html.H4(f"{df['Fuel Type'].nunique()}", className="card-title"),
                        html.P("Fuel types", className="card-text"),
                    ]), color="warning", inverse=True
                ), lg=3),
            ],
            className="g-3",
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=fig_sales, id="sales-line"), width=12),
            ]
        ),
        dbc.Row(
            dbc.Col(
                dcc.Markdown(
                    """
**Story so far**

Sales have shown seasonality and a gradual uptick in Q4 2024,
coinciding with dealership incentives and the launch of several
electric-drive models. Average prices remain stable despite discounting,
implying a move toward higher-trim vehicles.
                    """,
                    className="mt-4",
                ), width=12
            )
        ),
        html.Hr(),
        html.H5("Dataset preview (first 5 rows)", className="mt-4"),
        html.Div(
            dbc.Table.from_dataframe(df.head(), striped=True, bordered=True, hover=True, className="small"),
            className="table-responsive"
        )

    ],
    className="pt-4",
    fluid=True,
)
