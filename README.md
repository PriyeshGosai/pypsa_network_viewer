# PyPSA Network Viewer

Interactive HTML viewer for PyPSA networks that allows users to explore network components and timeseries data through a web-based interface.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/PriyeshGosai/pypsa_network_viewer.git
```

## Usage

```python
from pypsa_network_viewer import html_viewer
import pypsa

# Load your PyPSA network
network = pypsa.examples.ac_dc_meshed()

# Generate interactive HTML viewer
html_file = html_viewer(
    network,
    file_name='my_network.html',
    title='My Network Analysis'
)
```

## Features

- Interactive exploration of PyPSA network components
- Static data visualization in tables
- Dynamic timeseries plotting with Plotly
- Export functionality for data
- Clean, responsive web interface

## Function Parameters

- `network`: PyPSA network object
- `file_path`: Directory to save HTML file (optional)
- `file_name`: Name of HTML file (optional, defaults to "network_analyzer.html")
- `title`: Title for the HTML page (optional)
- `currency`: Currency symbol for cost units (optional, defaults to '$')

## Requirements

- Python 3.12+
- PyPSA
- Plotly (for JavaScript CDN)