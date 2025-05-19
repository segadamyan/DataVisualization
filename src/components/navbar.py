import dash_bootstrap_components as dbc
from dash import html, dcc

def make_navbar():
    return dbc.NavbarSimple(
        brand="Car-Sales Dashboard",
        brand_href="/",
        color="primary", dark=True, fluid=True,
        children=[
            dbc.NavItem(dcc.Link("Overview", href="/", className="nav-link")),
            dbc.NavItem(dcc.Link("Deep-dive", href="/deep-dive", className="nav-link")),
        ],
    )
