# PyPSA Network Viewer - Example Usage Guide

## ✅ Test Results

All 5 updates have been successfully implemented and tested:

1. ✅ **Export button removed** - The export functionality has been completely removed
2. ✅ **Network Summary view** - Shows network properties, optimization results, and metadata
3. ✅ **Global Constraints view** - Displays global constraints with currency-formatted dual values
4. ✅ **Explore Map integration** - Interactive geographical visualization embedded as iframe
5. ✅ **Custom Plots support** - User-provided Plotly figures with full interactivity

## 📦 Installation

```bash
# Clone or navigate to the repository
cd pypsa_network_viewer

# Install required packages (if not already installed)
pip install pypsa plotly
```

## 🚀 Quick Start

### Option 1: Use the Python Module (Recommended)

```python
import pypsa
from pypsa_network_viewer import html_network

# Load and optimize your network
network = pypsa.examples.ac_dc_meshed()
network.optimize()

# Generate the HTML viewer
html_network(network, file_name='my_network.html')
```

### Option 2: Run the Example Notebook

Open `example.ipynb` in Jupyter:

```bash
jupyter notebook example.ipynb
```

The notebook demonstrates:
- Basic usage
- Custom currency symbols
- Network with explore map
- Creating custom Plotly plots
- Complete viewer with all features
- Organized output directories
- Quick network inspection

### Option 3: Run the Test Script

```bash
python test_example.py
```

This will generate 6 test HTML files demonstrating all features.

## 📖 Function Parameters

```python
html_network(
    network,              # pypsa.Network object (required)
    file_path=None,       # Output directory (default: current directory)
    file_name=None,       # HTML filename (default: 'network_analyzer.html')
    title="...",          # Page title
    currency='$',         # Currency symbol for costs
    explore=False,        # Enable explore map
    custom_plots=None     # List of Plotly figure objects
)
```

## 🎨 Features Overview

### 1. Network Summary
View comprehensive network information:
- Network name and PyPSA version
- Optimization objective and constants
- Network configuration settings
- Custom metadata

**Usage:** Select "Network Summary" from the Component Type dropdown

### 2. Global Constraints
Display global constraints with:
- Constraint type and attributes
- Dual values (mu) with currency formatting
- Constraint limits

**Usage:** Select "Global Constraints" from the Component Type dropdown

### 3. Explore Map
Interactive geographical visualization:
- Network topology on a map
- Bus locations and connections
- Line and link flows

**Usage:**
```python
html_network(network, file_name='map.html', explore=True)
```
Then select "Explore Map" from the dropdown

### 4. Custom Plots
Add your own Plotly visualizations:

```python
import plotly.graph_objects as go

# Create custom plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=..., y=..., name='...'))
fig.update_layout(title='My Custom Plot')

# Include in viewer
html_network(network, custom_plots=[fig])
```

Then select "Custom Plots" > "My Custom Plot" from the dropdowns

### 5. Component Data
Explore all network components:
- **Static Data**: View component properties in tables
- **Timeseries Data**: Interactive plots of time-varying data

Available components:
- Generators
- Links
- Loads
- Stores
- Storage Units
- Lines
- Transformers
- Buses

## 📁 Generated Test Files

The test script creates:

1. **test_basic.html** - Basic viewer with default settings
2. **test_currency.html** - Custom currency (Euro) example
3. **test_summary_constraints.html** - Network Summary and Global Constraints
4. **test_explore_map.html** - With interactive map
5. **test_custom_plots.html** - With 2 custom Plotly plots
6. **test_output/complete_test.html** - All features combined

Open any HTML file in your web browser to explore!

## 🎯 Example: Complete Setup

```python
import pypsa
import plotly.graph_objects as go
from pypsa_network_viewer import html_network

# 1. Load and optimize network
network = pypsa.examples.ac_dc_meshed()
network.optimize()

# 2. Create custom plots
fig1 = go.Figure()
for col in network.generators_t.p.columns:
    fig1.add_trace(go.Scatter(
        x=network.generators_t.p.index,
        y=network.generators_t.p[col],
        mode='lines',
        name=col
    ))
fig1.update_layout(title='Generator Power Output')

fig2 = go.Figure()
for col in network.buses_t.marginal_price.columns:
    fig2.add_trace(go.Scatter(
        x=network.buses_t.marginal_price.index,
        y=network.buses_t.marginal_price[col],
        mode='lines',
        name=col
    ))
fig2.update_layout(title='Bus Marginal Prices')

# 3. Generate complete viewer
html_network(
    network,
    file_path='output',
    file_name='complete_analysis.html',
    title='My Network Analysis',
    currency='€',
    explore=True,
    custom_plots=[fig1, fig2]
)

# 4. Open the file in your browser
# output/complete_analysis.html
```

## 🔍 Using the HTML Viewer

1. **Select Component Type**: Choose from dropdowns (Network Summary, components, etc.)
2. **Select Data Type**: Choose Static Data or Time Series
3. **Select Time Series**: If applicable, choose which timeseries to plot
4. **Load Data**: Click to display the selected information
5. **Clear Display**: Reset the view

All plots are interactive:
- Hover for details
- Zoom and pan
- Toggle series visibility
- Download as PNG

## 💡 Tips

- **Network Summary**: Shows optimization results after running `network.optimize()`
- **Global Constraints**: Only appears if your network has global constraints
- **Explore Map**: Requires network buses to have valid coordinates (x, y or lon, lat)
- **Custom Plots**: Plot titles are used as menu options - give them meaningful names!
- **Large Networks**: For very large networks, consider selecting specific time ranges or components

## 🐛 Troubleshooting

**Import Error:**
```python
# If you get "cannot import name 'html_network'"
# Make sure you're in the correct directory:
import sys
sys.path.insert(0, '/path/to/pypsa_network_viewer')
from pypsa_network_viewer import html_network
```

**Explore Map Not Showing:**
- Ensure `explore=True` is set
- Check that your network has valid bus coordinates
- The map is generated in a separate HTML file and embedded

**Custom Plots Not Appearing:**
- Verify plots have titles: `fig.update_layout(title='...')`
- Make sure `custom_plots` is a list: `custom_plots=[fig1, fig2]`

## 📞 Support

For issues or questions, please check:
1. The example notebook: `example.ipynb`
2. The test script: `test_example.py`
3. Generated test files for working examples

## 📄 License

See LICENSE file in the repository.
