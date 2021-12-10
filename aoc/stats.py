import dash
import yaml
from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
from json import load
from sys import argv

from plotly.subplots import make_subplots

from aoc import ROOT_DIR, SUBMISSIONS_FILE

DAYS = [n for n in range(1, 25 + 1)]

app = dash.Dash()  # initialising dash app
df = px.data.stocks()  # reading stock price dataset


def loc(day):
    nb = ROOT_DIR / f"day{str(day).rjust(2, '0')}.ipynb"
    if nb.exists():
        cells = load(nb.open())['cells']
        return sum(len(c['source']) for c in cells if c['cell_type'] == 'code')
    return 0


def locs():
    return [loc(n) for n in DAYS]


def time(day, submissions):
    index = str(day).rjust(2, '0')
    entry = submissions[index] if index in submissions else None
    if entry:
        try:
            return sum([entry[part][entry[part]['solution']]['time'] for part in ['1', '2']])
        except:
            pass
    return 0


def times():
    submissions = yaml.full_load(SUBMISSIONS_FILE.read_text())
    print(submissions)
    return [time(n, submissions) for n in DAYS]


def get_figure():
    # Function for creating line chart showing Google stock prices over time
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=DAYS, y=locs(), name="Lines of code"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=DAYS, y=times(), name="Execution time"),
        secondary_y=True,
    )

    # fig.update_layout(title_text="AoC 2021")
    fig.update_xaxes(title_text="day")
    fig.update_yaxes(title_text="#loc", secondary_y=False)
    fig.update_yaxes(title_text="execution time in <b>ms</b>", secondary_y=True)

    return fig


app.layout = html.Div(id='parent', children=[
    html.H1(id='H1', children='AoC 2021 Stats',
            style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
    dcc.Graph(id='line_plot', figure=get_figure()),
    html.H2(id='H2', children='Totals',
            style={'textAlign': 'center', 'marginTop': 40}),
    html.Div(id="totals", children=f"Lines of code: {sum(locs())} <> Execution Time: {sum(times())}ms",
             style={'textAlign': 'center', 'marginTop': 20, 'marginBottom': 40})
])

if __name__ == '__main__':
    app.run_server()
