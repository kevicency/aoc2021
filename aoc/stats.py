import sys

import dash
import yaml
from dash import html, dcc
import plotly.graph_objects as go
import numpy as np
from json import load
from plotly.subplots import make_subplots
from constants import ROOT_DIR, SUBMISSIONS_FILE, AOC_DIR

DAYS = [n for n in range(1, 25 + 1)]


def loc(day):
    nb = ROOT_DIR / f"day{str(day).rjust(2, '0')}.ipynb"
    if nb.exists():
        cells = load(nb.open())['cells']
        return sum(len(c['source']) for c in cells if c['cell_type'] == 'code')
    return 0


def get_locs():
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


def get_times():
    submissions = yaml.full_load(SUBMISSIONS_FILE.read_text())
    return [time(n, submissions) for n in DAYS]


def get_figure(locs=None, times=None):
    locs = locs or get_locs()
    times = times or get_times()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=DAYS, y=locs, name="Lines of code"),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=DAYS, y=times, name="Execution time"),
        secondary_y=True,
    )

    fig.update_layout(title_text=f"Total(avg) Lines of code / Execution time :: " +
                                 f"{sum(locs)}({float(np.mean(locs))}) / {round(sum(times))}({round(float(np.mean(times)))})ms")
    fig.update_xaxes(title_text="day")
    fig.update_yaxes(title_text="#loc", secondary_y=False)
    fig.update_yaxes(title_text="execution time in <b>ms</b>", secondary_y=True)

    return fig


def run_server():
    locs = get_locs()
    times = get_times()

    app = dash.Dash()
    app.layout = html.Div(id='parent', children=[
        html.H1(id='H1', children='AoC 2021 Stats',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
        dcc.Graph(id='line_plot', figure=get_figure(locs, times)),
        html.H2(id='H2', children='Totals',
                style={'textAlign': 'center', 'marginTop': 40}),
        html.Div(id="totals", children=f"Lines of code: {sum(locs)} <> Execution Time: {round(sum(times))}ms",
                 style={'textAlign': 'center', 'marginTop': 20, 'marginBottom': 40})
    ])
    app.run_server()


if __name__ == '__main__':
    print(*sys.argv)
    if len(sys.argv) > 1 and sys.argv[1] == 'serve':
        run_server()
    else:
        print('Generating stats chart...')
        get_figure().write_image(AOC_DIR / 'stats.png')
