# -*- coding: utf-8 -*-

# Import required libraries
import numpy as np
import plotly.graph_objs as go
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Initialize the Dash app with Bootstrap stylesheets
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Define the layout of the app
app.layout = dbc.Container([
    # Add header
    html.H1('Active, Reactive and Instantaneous Power'),
    html.P([html.Span("Link to supplementary article on "),
            html.A("active and reactive power", href='https://medium.com/@ogb.bassey/from-real-to-imaginary-understanding-active-and-reactive-power-with-interactive-plots-34d67be8386e', target="_blank"),
    ]),
    # Add a graph container
    dcc.Graph(id='power-plot-graph'),
    
    # Add sliders for input parameters within a row
    dbc.Row([
        # Frequency slider
        dbc.Col([
            html.Label('Frequency (Hertz)'),
            dcc.Slider(
                id='frequency-slider',
                min=1,
                max=10,
                step=0.1,
                value=1,
                marks={i: f'{i}' for i in range(0, 11)},
            ),
        ], style={'marginBottom': 20}, md=4),
        
        # Voltage phase slider
        dbc.Col([
            html.Label('Voltage Phase (Degs)'),
            dcc.Slider(
                id='phase-voltage',
                min=-180,
                max=180,
                step=5,
                value=0,
                marks={i: f'{i}' for i in range(-180, 185, 60)},
            ),
        ], style={'marginBottom': 20}, md=4),
        
        # Current phase slider
        dbc.Col([
            html.Label('Current Phase (Degs)'),
            dcc.Slider(
                id='phase-current',
                min=-180,
                max=180,
                step=5,
                value=0,
                marks={i: f'{i}' for i in range(-180, 185, 60)},
            ),
        ], style={'marginBottom': 20}, md=4),
    ]),
], fluid=True)

# Define the callback function to update the power plot
@app.callback(
    Output('power-plot-graph', 'figure'),
    [Input('frequency-slider', 'value'),
     Input('phase-voltage', 'value'),
     Input('phase-current', 'value')]
)
def update_power_plot(frequency, phase_v, phase_i):
    # Define constants and initialize arrays
    small_num = 1e-5
    Vm = 2  # voltage magnitude
    Im = 2  # current magnitude
    S = Vm * Im / 2  # Apparent power
    t = np.linspace(0, 2, 500)  # Time array
    
    # Calculate active and reactive power
    P = np.ones((t.shape)) * S * np.cos(np.radians(phase_v - phase_i))
    Q = np.ones((t.shape)) * S * np.sin(np.radians(phase_v - phase_i))
    
    # Calculate instantaneous power
    iP = P + Vm * Im / 2 * np.cos(2 * 2 * np.pi * frequency * t + np.pi * (phase_v - phase_i) / 180)
    
    # Initialize a plotly figure and add traces for power values
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=t, y=P, mode='lines', name='Active Power (P)', line=dict(color='blue', width=2, dash='dashdot')))
    figure.add_trace(go.Scatter(x=t, y=Q, mode='lines', name='Reactive Power (Q)', line=dict(color='firebrick', width=2, dash='dash')))
    figure.add_trace(go.Scatter(x=t, y=iP, mode='lines', name='Instantaneous Power(p)', line=dict(color='red', width=2)))
    
    # Add annotations to the figure for power values
    figure.add_annotation(x=1, y=4.5,
            text="Im = Vm = 2, P: {:.2f}, Q: {:.2f}, S: {:.2f}, P/S : {:.2f}, \u03B8v - \u03B8i:{} degs".format(P[0], Q[0], S, P[0]/S, phase_v-phase_i),
            showarrow=False,
            yshift=10)
    figure.add_annotation(x=1, y=-4.5,
            text="Slider Settings. Freq (Hz): {:.1f}, Voltage Phase (degs): {}, Current Phase (degs): {}".format(frequency, phase_v, phase_i),
            showarrow=False)
    if P[0] == S:
        figure.add_annotation(x=1, y=2,
                text="Maximum active power (absorbing): 2 Watts",
                showarrow=True,
                arrowhead=5,
                arrowsize=2)
    elif P[0] == -S:
        figure.add_annotation(x=1, y=-2,
                text="Maximum active power (generating): -2 Watts",
                showarrow=True,
                arrowhead=5,
                arrowsize=2)
    elif P[0] < small_num and P[0] > -small_num:
        figure.add_annotation(x=1, y=0,
                text="Zero active power",
                showarrow=True,
                arrowhead=5,
                arrowsize=2)
    figure.update_layout(xaxis_title='Time (sec)', yaxis_title='Power (volts.amps)', font=dict(size=18))
    figure.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    figure.update_layout(yaxis_range=[-5,5])

    return figure

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
    