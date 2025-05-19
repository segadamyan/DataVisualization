import dash_bootstrap_components as dbc
from dash import dcc, html

def brand_dropdown(brands):
    return dbc.FormFloating(
        [
            dcc.Dropdown(
                id="brand-dd",
                options=[{"label": b, "value": b} for b in sorted(brands)],
                value=None, clearable=True, multi=False,
                placeholder="Select a brand …",
            ),
            dbc.Label("Filter by brand"),
        ],
        className="mb-3",
    )

def fuel_checklist(fuels):
    return dbc.Checklist(
        id="fuel-cl",
        options=[{"label": f, "value": f} for f in sorted(fuels)],
        value=sorted(fuels), inline=True, switch=True,
        label_checked_style={"fontWeight": "600"},
    )

def km_slider(max_km):
    return dcc.RangeSlider(
        id="km-sl",
        min=0, max=max_km, value=[0, max_km],
        marks=None, tooltip={"placement": "bottom"},
        allowCross=False,
    )
