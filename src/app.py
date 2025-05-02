import dash
import dash_bootstrap_components as dbc

from components.navbar import make_navbar

app = dash.Dash(
    __name__, use_pages=True,
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = dbc.Container(
    [
        make_navbar(),
        dash.page_container,
    ],
    fluid=True,
    className="px-0",
)

if __name__ == "__main__":
    app.run(debug=True)
