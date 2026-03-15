# PyPSA Network Viewer

Interactive HTML viewer and Excel template generator for PyPSA networks (requires PyPSA >= 1.0).

## Features

- 📊 **Network Summary** — Properties, optimization results, and metadata
- 🔗 **Global Constraints** — Constraints with dual values (shadow prices)
- 📈 **Custom Plots** — Embed your own Plotly visualizations via a `.py` file or inline
- 📋 **Component Data** — Static and timeseries data for all components, discovered dynamically
- 📝 **Excel Template Generator** — Generate a pre-configured Excel workbook to define a new network

## Requirements

- Python 3.8+
- PyPSA >= 1.0
- Plotly 5.0+ (for custom plots)
- openpyxl (for Excel template generator)

## Installation

```bash
pip install git+https://github.com/PriyeshGosai/pypsa_network_viewer.git
```

## Quick Start

### HTML Viewer

```python
import pypsa
from pypsa_network_viewer import html_network

network = pypsa.examples.ac_dc_meshed()
network.optimize()

html_network(network, file_name='my_network.html')
```

### With Custom Plots (inline)

```python
import plotly.graph_objects as go

fig = go.Figure()
for gen, series in network.components['generators'].dynamic['p'].items():
    fig.add_trace(go.Scatter(x=series.index, y=series.values, mode='lines', name=gen))
fig.update_layout(title='Generator Dispatch')

html_network(network, file_name='analysis.html', currency='€', custom_plots=[fig])
```

### With Custom Plots (file)

Create a `my_plots.py` file with a `get_plots(network)` function (copy
`pypsa_network_viewer/custom_plots_template.py` as a starting point):

```python
# my_plots.py
import plotly.graph_objects as go

def get_plots(network):
    fig = go.Figure()
    # ... build plots using network data ...
    fig.update_layout(title='My Plot')
    return [fig]
```

Then pass the file path:

```python
html_network(network, file_name='analysis.html', custom_plots='my_plots.py')
```

### Excel Template Generator

```python
from pypsa_network_viewer import generate_template

# 1 year, hourly resolution
generate_template(
    output_name='network_template.xlsx',
    start_year=2025,
    start_month=1,
    years_duration=1,
    resolution_str='H',
)

# 3 months, 30-minute resolution, 2 link outputs
generate_template(
    output_name='network_template_3m.xlsx',
    start_year=2025,
    start_month=6,
    months_duration=3,
    resolution_str='30m',
    link_outputs=2,
)
```

## `html_network` Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `network` | `pypsa.Network` | required | Network to visualize |
| `file_path` | `str` | `None` | Output directory |
| `file_name` | `str` | `'network_analyzer.html'` | Output filename |
| `title` | `str` | `'PyPSA Network Analyzer'` | Page title |
| `currency` | `str` | `'$'` | Currency symbol for cost units |
| `custom_plots` | `str` or `list` | `None` | Path to a `.py` file or list of Plotly figures |

## `generate_template` Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `output_name` | `str` | required | Output `.xlsx` file path |
| `start_year` | `int` | `2024` | Start year (2024–2029) |
| `start_month` | `int` | `1` | Start month (1–12) |
| `years_duration` | `int\|None` | `1` | Duration in years (1–5) |
| `months_duration` | `int\|None` | `None` | Duration in months (1–12) |
| `days_duration` | `int\|None` | `None` | Duration in days (7–31) |
| `resolution_str` | `str` | `'H'` | Timestep: `'H'`, `'2H'`, `'4H'`, `'6H'`, `'8H'`, `'0.5H'`, `'15m'`, `'30m'` |
| `drop_leap_day` | `bool` | `True` | Skip Feb 29 timestamps |
| `link_outputs` | `int` | `1` | Number of link output buses |
| `process_outputs` | `int` | `2` | Number of process output buses |

Exactly one of `years_duration`, `months_duration`, or `days_duration` must be set.

## Custom Plots Template

A ready-to-use template is included in the package:

```
pypsa_network_viewer/custom_plots_template.py
```

Copy it, rename it, and edit the `get_plots(network)` function to return your list of figures.
The template includes three example plots: generator dispatch, installed capacity, and system costs.

## Available Views

| View | Description |
|---|---|
| **Network Summary** | Network name, PyPSA version, objective value, metadata |
| **Global Constraints** | Constraint attributes and shadow prices |
| **Custom Plots** | Your embedded Plotly figures |
| **Component / Static** | Per-component property tables |
| **Component / Time Series** | Interactive time-series plots for all dynamic attributes |

Components are discovered dynamically — any component present in the network will appear automatically.

## Example Notebook

See [example.ipynb](example.ipynb) for runnable examples covering all features.

## Contributing

Issues and pull requests are welcome.

## License

MIT License

## Author

Priyesh Gosai
