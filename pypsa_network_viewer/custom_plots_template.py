"""
Custom Plots Template for PyPSA Network Viewer
===============================================

Copy this file, rename it (e.g. ``my_plots.py``), and pass the path to ``html_network``:

    from pypsa_network_viewer import html_network
    html_network(network, custom_plots='my_plots.py')

Requirements
------------
- Define a function called ``get_plots(network)`` that returns a **list** of
  Plotly ``go.Figure`` objects.
- Each figure's ``layout.title.text`` is used as the plot name in the viewer.
  If no title is set, the plot is labelled "Plot 1", "Plot 2", etc.
- You can use any Plotly chart type (scatter, bar, pie, heatmap, …).

The ``network`` argument is the live PyPSA Network object, so you have full
access to optimisation results, component data, and snapshots.
"""

import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# Required: define this function
# ---------------------------------------------------------------------------

def get_plots(network):
    """
    Build and return a list of Plotly figures for the network viewer.

    Parameters
    ----------
    network : pypsa.Network

    Returns
    -------
    list[plotly.graph_objects.Figure]
    """
    figures = []

    # -- Example 1: Generator dispatch (stacked bar) ------------------------
    gen_dispatch = _generator_dispatch(network)
    if gen_dispatch is not None:
        figures.append(gen_dispatch)

    # -- Example 2: Total installed capacity by carrier ---------------------
    capacity_fig = _installed_capacity(network)
    if capacity_fig is not None:
        figures.append(capacity_fig)

    # -- Example 3: System cost breakdown -----------------------------------
    cost_fig = _system_costs(network)
    if cost_fig is not None:
        figures.append(cost_fig)

    return figures


# ---------------------------------------------------------------------------
# Helper functions – adapt or replace these with your own plots
# ---------------------------------------------------------------------------

def _generator_dispatch(network):
    """Stacked bar chart of hourly generator dispatch grouped by carrier."""
    try:
        p = network.components['generators'].dynamic.get('p')
        if p is None or p.empty:
            return None

        carriers = network.components['generators'].static.get('carrier')
        if carriers is None:
            return None

        # Group by carrier
        carrier_dispatch = {}
        for gen, series in p.items():
            c = carriers.get(gen, 'Unknown')
            carrier_dispatch[c] = carrier_dispatch.get(c, series * 0) + series

        fig = go.Figure()
        for carrier, series in carrier_dispatch.items():
            fig.add_trace(go.Bar(
                x=network.snapshots.tolist(),
                y=series.tolist(),
                name=carrier,
            ))

        fig.update_layout(
            title=dict(text='Generator Dispatch by Carrier'),
            barmode='stack',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Power (MW)'),
            hovermode='x unified',
            legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.2),
        )
        return fig

    except Exception:
        return None


def _installed_capacity(network):
    """Bar chart of total installed capacity (p_nom_opt or p_nom) by carrier."""
    try:
        gen_static = network.components['generators'].static
        if gen_static.empty:
            return None

        cap_col = 'p_nom_opt' if 'p_nom_opt' in gen_static.columns else 'p_nom'
        if cap_col not in gen_static.columns:
            return None

        by_carrier = gen_static.groupby('carrier')[cap_col].sum()

        fig = go.Figure(go.Bar(
            x=by_carrier.index.tolist(),
            y=by_carrier.values.tolist(),
            marker_color='steelblue',
        ))
        fig.update_layout(
            title=dict(text='Installed Capacity by Carrier'),
            xaxis=dict(title='Carrier'),
            yaxis=dict(title='Capacity (MW)'),
        )
        return fig

    except Exception:
        return None


def _system_costs(network):
    """Pie chart of annualised system costs split by component type."""
    try:
        cost_items = {}

        gen_static = network.components['generators'].static
        if not gen_static.empty and 'marginal_cost' in gen_static.columns:
            p = network.components['generators'].dynamic.get('p')
            if p is not None and not p.empty:
                mc = gen_static['marginal_cost']
                total = float((p * mc).sum().sum())
                if total > 0:
                    cost_items['Generator marginal cost'] = total

        if not cost_items:
            return None

        fig = go.Figure(go.Pie(
            labels=list(cost_items.keys()),
            values=list(cost_items.values()),
            hole=0.3,
        ))
        fig.update_layout(title=dict(text='System Cost Breakdown'))
        return fig

    except Exception:
        return None
