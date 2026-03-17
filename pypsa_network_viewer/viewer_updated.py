"""
PyPSA Network Viewer
Interactive HTML visualization for PyPSA networks

Author: Priyesh Gosai
"""

import importlib.util
import json
import os
import sys

import pandas as pd
import pypsa

_PYPSA_MAJOR = int(pypsa.__version__.split('.')[0])
if _PYPSA_MAJOR < 1:
    raise ImportError(
        f"pypsa_network_viewer requires PyPSA >= 1.0.0, but {pypsa.__version__} is installed"
    )

pypsa.options.api.new_components_api = True


def html_network(network, file_path=None, file_name=None, title="PyPSA Network Analyzer",
                 currency='$', custom_plots=None):
    """
    Generate interactive HTML interface for exploring PyPSA network components and timeseries data.

    Parameters:
    -----------
    network : pypsa.Network
        The PyPSA network object to analyze
    file_path : str, optional
        Directory path where the HTML file should be saved (default: None, saves in current directory)
    file_name : str, optional
        Name of the HTML file (default: None, creates "network_analyzer.html")
    title : str, optional
        Title for the HTML page (default: "PyPSA Network Analyzer")
    currency : str, optional
        Currency symbol for cost displays (default: '$')
    custom_plots : str or list, optional
        Either a path to a Python file containing a ``get_plots(network)`` function that
        returns a list of Plotly figure objects, OR a list of Plotly figure objects directly.
        See ``custom_plots_template.py`` for the expected file format.

    Returns:
    --------
    str : Path to generated HTML file

    Examples:
    ---------
    Basic usage:
    >>> import pypsa
    >>> network = pypsa.examples.ac_dc_meshed()
    >>> network.optimize()
    >>> html_network(network, file_name='my_network.html')

    With a custom plots file:
    >>> html_network(network, file_name='full_network.html',
    ...              currency='€', custom_plots='my_custom_plots.py')

    With inline custom plots:
    >>> import plotly.graph_objects as go
    >>> fig = go.Figure()
    >>> html_network(network, custom_plots=[fig])
    """

    if file_name is None:
        file_name = "network_analyzer.html"

    if file_path is None:
        output_file = file_name
    else:
        output_file = os.path.join(file_path, file_name)

    component_info = _extract_component_info(network, currency=currency, custom_plots=custom_plots)

    data_json = json.dumps(component_info, indent=2, default=str)

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.26.0/plotly.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #2c3e50 0%, #4a6741 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        .controls-section {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #2c3e50;
        }}
        .control-group {{
            display: flex;
            flex-direction: column;
        }}
        .control-label {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        select, button {{
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.2s;
        }}
        select:focus, button:hover {{
            outline: none;
            border-color: #2c3e50;
        }}
        button {{
            background: linear-gradient(135deg, #2c3e50 0%, #4a6741 100%);
            color: white;
            border: none;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(44, 62, 80, 0.3);
        }}
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(44, 62, 80, 0.4);
        }}
        .content-area {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            min-height: 600px;
        }}
        .loading {{
            display: none;
            text-align: center;
            color: #2c3e50;
            font-size: 1.2em;
            padding: 50px;
        }}
        .data-table {{
            overflow-x: auto;
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #2c3e50;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .plot-container {{
            margin-top: 20px;
        }}
        .info-panel {{
            background: #e8f4f8;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .info-panel h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        .error-panel {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            color: #721c24;
        }}
        .network-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 1.8em;
        }}
        .summary-card p {{
            margin: 0;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .network-details {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .network-details-item {{
            display: grid;
            grid-template-columns: 250px 1fr;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .network-details-label {{
            font-weight: 600;
            color: #2c3e50;
        }}
        .network-details-value {{
            color: #555;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>Interactive exploration of PyPSA network components and timeseries data</p>
        </div>

        <div id="networkSummary" class="network-summary">
            <!-- Will be populated by JavaScript -->
        </div>

        <div class="controls-section">
            <div class="control-group">
                <label class="control-label">Component Type</label>
                <select id="componentTypeSelect">
                    <option value="">Select component type...</option>
                </select>
            </div>
            <div class="control-group">
                <label class="control-label">Data Type</label>
                <select id="dataTypeSelect" disabled>
                    <option value="">Select data type...</option>
                    <option value="static">Static Data</option>
                    <option value="timeseries">Time Series</option>
                </select>
            </div>
            <div class="control-group">
                <label class="control-label">Time Series / Plot</label>
                <select id="timeseriesSelect" disabled>
                    <option value="">Select timeseries...</option>
                </select>
            </div>
        </div>

        <div class="controls-section">
            <div class="control-group" id="yearGroup" style="display:none;">
                <label class="control-label">Investment Period</label>
                <select id="yearSelect">
                    <option value="">All Periods</option>
                </select>
            </div>
            <div class="control-group">
                <button onclick="loadData()" id="loadButton" disabled>Load Data</button>
            </div>
            <div class="control-group">
                <button onclick="clearDisplay()" id="clearButton">Clear Display</button>
            </div>
        </div>

        <div class="content-area">
            <div class="loading" id="loading">Loading data...</div>
            <div id="contentDisplay">
                <div class="info-panel">
                    <h3>Welcome to PyPSA Network Analyzer</h3>
                    <p>Select a component type and data type above to begin exploring your network data.</p>
                    <p><strong>Instructions:</strong></p>
                    <ul>
                        <li>Choose a component type from the dropdown</li>
                        <li>Select whether you want to view static properties or timeseries data</li>
                        <li>For timeseries, choose which specific attribute to plot</li>
                        <li>Click "Load Data" to display the information</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        const networkData = {data_json};

        let currentData = null;

        document.addEventListener('DOMContentLoaded', function() {{
            populateNetworkSummary();
            populateComponentTypes();
            setupEventListeners();
            if (networkData.summary.is_multi_index) {{
                const yearGroup = document.getElementById('yearGroup');
                yearGroup.style.display = 'flex';
                const yearSelect = document.getElementById('yearSelect');
                networkData.summary.periods.forEach(p => {{
                    const opt = document.createElement('option');
                    opt.value = p;
                    opt.textContent = p;
                    yearSelect.appendChild(opt);
                }});
                if (networkData.summary.periods.length > 0) {{
                    yearSelect.value = networkData.summary.periods[0];
                }}
            }}
        }});

        function populateNetworkSummary() {{
            const summaryDiv = document.getElementById('networkSummary');
            const summary = networkData.summary;
            const skip = new Set(['network_info', 'global_constraints', 'custom_plots', 'is_multi_index', 'periods', 'period_index']);

            let html = '';
            Object.entries(summary).forEach(([key, value]) => {{
                if (!skip.has(key)) {{
                    html += `<div class="summary-card"><h3>${{value}}</h3><p>${{key.replace(/_/g, ' ').toUpperCase()}}</p></div>`;
                }}
            }});
            summaryDiv.innerHTML = html;
        }}

        function populateComponentTypes() {{
            const select = document.getElementById('componentTypeSelect');

            if (networkData.summary.network_info) {{
                const opt = document.createElement('option');
                opt.value = 'network_summary';
                opt.textContent = 'Network Summary';
                select.appendChild(opt);
            }}

            if (networkData.summary.global_constraints) {{
                const opt = document.createElement('option');
                opt.value = 'global_constraints';
                opt.textContent = 'Global Constraints';
                select.appendChild(opt);
            }}

            if (networkData.summary.custom_plots && networkData.summary.custom_plots.length > 0) {{
                const opt = document.createElement('option');
                opt.value = 'custom_plots';
                opt.textContent = 'Custom Plots';
                select.appendChild(opt);
            }}

            Object.keys(networkData.components).forEach(comp => {{
                const opt = document.createElement('option');
                opt.value = comp;
                opt.textContent = comp.charAt(0).toUpperCase() + comp.slice(1);
                select.appendChild(opt);
            }});
        }}

        function setupEventListeners() {{
            document.getElementById('componentTypeSelect').addEventListener('change', onComponentTypeChange);
            document.getElementById('dataTypeSelect').addEventListener('change', onDataTypeChange);
            document.getElementById('yearSelect').addEventListener('change', function() {{
                if (currentData && currentData.type === 'timeseries') {{
                    displayTimeseriesData(currentData.componentType, currentData.timeseriesName);
                }}
            }});
        }}

        function onComponentTypeChange() {{
            const componentType = document.getElementById('componentTypeSelect').value;
            const dataTypeSelect = document.getElementById('dataTypeSelect');
            const timeseriesSelect = document.getElementById('timeseriesSelect');

            timeseriesSelect.innerHTML = '<option value="">Select timeseries...</option>';
            timeseriesSelect.disabled = true;

            if (componentType === 'network_summary' || componentType === 'global_constraints') {{
                dataTypeSelect.disabled = true;
                dataTypeSelect.value = '';
                document.getElementById('loadButton').disabled = false;
            }} else if (componentType === 'custom_plots') {{
                dataTypeSelect.disabled = false;
                dataTypeSelect.innerHTML = '<option value="">Select plot...</option>';
                networkData.summary.custom_plots.forEach(name => {{
                    const opt = document.createElement('option');
                    opt.value = name;
                    opt.textContent = name;
                    dataTypeSelect.appendChild(opt);
                }});
                document.getElementById('loadButton').disabled = true;
            }} else if (componentType) {{
                dataTypeSelect.disabled = false;
                dataTypeSelect.innerHTML = '<option value="">Select data type...</option><option value="static">Static Data</option><option value="timeseries">Time Series</option>';
                dataTypeSelect.value = '';
                document.getElementById('loadButton').disabled = true;
            }} else {{
                dataTypeSelect.disabled = true;
                dataTypeSelect.innerHTML = '<option value="">Select data type...</option><option value="static">Static Data</option><option value="timeseries">Time Series</option>';
                document.getElementById('loadButton').disabled = true;
            }}
        }}

        function onDataTypeChange() {{
            const componentType = document.getElementById('componentTypeSelect').value;
            const dataType = document.getElementById('dataTypeSelect').value;
            const timeseriesSelect = document.getElementById('timeseriesSelect');

            if (componentType === 'custom_plots' && dataType) {{
                timeseriesSelect.disabled = true;
                document.getElementById('loadButton').disabled = false;
            }} else if (dataType === 'static') {{
                timeseriesSelect.disabled = true;
                timeseriesSelect.innerHTML = '<option value="">Select timeseries...</option>';
                document.getElementById('loadButton').disabled = false;
            }} else if (dataType === 'timeseries') {{
                const timeseries = networkData.components[componentType].timeseries;
                timeseriesSelect.innerHTML = '<option value="">Select timeseries...</option>';
                Object.keys(timeseries).forEach(ts => {{
                    const opt = document.createElement('option');
                    opt.value = ts;
                    opt.textContent = ts;
                    timeseriesSelect.appendChild(opt);
                }});
                timeseriesSelect.disabled = false;
                timeseriesSelect.onchange = function() {{
                    document.getElementById('loadButton').disabled = !this.value;
                }};
            }}
        }}

        function loadData() {{
            const componentType = document.getElementById('componentTypeSelect').value;
            const dataType = document.getElementById('dataTypeSelect').value;
            const timeseries = document.getElementById('timeseriesSelect').value;

            if (!componentType) return;

            showLoading(true);
            setTimeout(() => {{
                try {{
                    if (componentType === 'network_summary') {{
                        displayNetworkSummary();
                    }} else if (componentType === 'global_constraints') {{
                        displayGlobalConstraints();
                    }} else if (componentType === 'custom_plots' && dataType) {{
                        displayCustomPlot(dataType);
                    }} else if (dataType === 'static') {{
                        displayStaticData(componentType);
                    }} else if (dataType === 'timeseries' && timeseries) {{
                        displayTimeseriesData(componentType, timeseries);
                    }}
                }} catch (error) {{
                    showError('Error loading data: ' + error.message);
                }}
                showLoading(false);
            }}, 300);
        }}

        function displayNetworkSummary() {{
            const data = networkData.summary.network_info;
            const contentDiv = document.getElementById('contentDisplay');
            let html = '<div class="info-panel"><h3>Network Summary</h3></div><div class="network-details">';
            Object.entries(data).forEach(([key, value]) => {{
                html += `<div class="network-details-item"><div class="network-details-label">${{key}}</div><div class="network-details-value">${{value}}</div></div>`;
            }});
            html += '</div>';
            contentDiv.innerHTML = html;
            currentData = {{ type: 'network_summary', data }};
        }}

        function displayGlobalConstraints() {{
            const data = networkData.summary.global_constraints;
            const contentDiv = document.getElementById('contentDisplay');

            if (!data || data.length === 0) {{
                contentDiv.innerHTML = '<div class="error-panel"><strong>No global constraints available</strong></div>';
                return;
            }}

            const columns = Object.keys(data[0]);
            let html = `<div class="info-panel"><h3>Global Constraints</h3><p>Showing ${{data.length}} constraint(s)</p></div>
                <div class="data-table"><table><thead><tr>${{columns.map(c => `<th>${{c}}</th>`).join('')}}</tr></thead><tbody>`;
            data.forEach(row => {{
                html += '<tr>' + columns.map(c => `<td>${{row[c] ?? 'N/A'}}</td>`).join('') + '</tr>';
            }});
            html += '</tbody></table></div>';
            contentDiv.innerHTML = html;
            currentData = {{ type: 'global_constraints', data }};
        }}

        function displayCustomPlot(plotName) {{
            const plotData = networkData.custom_plots[plotName];
            const contentDiv = document.getElementById('contentDisplay');

            if (!plotData) {{
                contentDiv.innerHTML = '<div class="error-panel"><strong>Custom plot data not found</strong></div>';
                return;
            }}

            contentDiv.innerHTML = `
                <div class="info-panel"><h3>Custom Plot: ${{plotName}}</h3></div>
                <div class="plot-container"><div id="customPlot" style="width:100%;height:600px;"></div></div>`;

            Plotly.newPlot('customPlot', plotData.data, plotData.layout, {{
                responsive: true, displayModeBar: true, displaylogo: false
            }});
            currentData = {{ type: 'custom_plot', plotName, data: plotData }};
        }}

        function displayStaticData(componentType) {{
            const data = networkData.components[componentType].static;
            const contentDiv = document.getElementById('contentDisplay');

            if (!data || Object.keys(data).length === 0) {{
                contentDiv.innerHTML = `<div class="error-panel"><strong>No static data available for ${{componentType}}</strong></div>`;
                return;
            }}

            const columns = Object.keys(data);
            const indices = Object.keys(data[columns[0]] || {{}});

            let html = `<div class="info-panel"><h3>${{componentType.charAt(0).toUpperCase() + componentType.slice(1)}} - Static Data</h3>
                <p>Showing ${{indices.length}} components with ${{columns.length}} properties</p></div>
                <div class="data-table"><table><thead><tr><th>Component</th>
                ${{columns.map(c => `<th>${{c}}</th>`).join('')}}</tr></thead><tbody>`;

            indices.forEach(idx => {{
                html += `<tr><td><strong>${{idx}}</strong></td>` +
                    columns.map(c => `<td>${{data[c][idx] ?? 'N/A'}}</td>`).join('') + '</tr>';
            }});

            html += '</tbody></table></div>';
            contentDiv.innerHTML = html;
            currentData = {{ type: 'static', componentType, data }};
        }}

        function displayTimeseriesData(componentType, timeseriesName) {{
            const data = networkData.components[componentType].timeseries[timeseriesName];
            const contentDiv = document.getElementById('contentDisplay');

            if (!data || Object.keys(data.data).length === 0) {{
                contentDiv.innerHTML = `<div class="error-panel"><strong>No timeseries data for ${{componentType}} - ${{timeseriesName}}</strong></div>`;
                return;
            }}

            // Multi-index: filter by selected investment period
            let timeIndex = data.time_index.map(t => new Date(t));
            let seriesData = data.data;
            let periodLabel = '';

            if (networkData.summary.is_multi_index) {{
                const selectedPeriod = document.getElementById('yearSelect').value;
                if (selectedPeriod) {{
                    const periodIdx = networkData.summary.period_index;
                    const mask = periodIdx.map(p => p === selectedPeriod);
                    timeIndex = timeIndex.filter((_, i) => mask[i]);
                    seriesData = {{}};
                    Object.entries(data.data).forEach(([name, values]) => {{
                        seriesData[name] = values.filter((_, i) => mask[i]);
                    }});
                    periodLabel = ` — Period: ${{selectedPeriod}}`;
                }}
            }}

            contentDiv.innerHTML = `
                <div class="info-panel">
                    <h3>${{componentType.charAt(0).toUpperCase() + componentType.slice(1)}} - ${{timeseriesName}}${{periodLabel}}</h3>
                    <p><strong>Time Range:</strong> ${{data.time_range.start}} to ${{data.time_range.end}}</p>
                    <p><strong>Series:</strong> ${{Object.keys(data.data).length}} with ${{timeIndex.length}} time steps shown</p>
                </div>
                <div class="plot-container"><div id="timeseriesPlot" style="width:100%;height:600px;"></div></div>`;

            const traces = Object.entries(seriesData).map(([name, values]) => ({{
                x: timeIndex, y: values, type: 'scatter', mode: 'lines', name, line: {{ width: 2 }}
            }}));

            Plotly.newPlot('timeseriesPlot', traces, {{
                title: `${{componentType}} - ${{timeseriesName}}${{periodLabel}}`,
                xaxis: {{ title: 'Time', type: 'date' }},
                yaxis: {{ title: data.unit || 'Value' }},
                hovermode: 'x unified',
                legend: {{ orientation: 'h', x: 0.5, xanchor: 'center', y: -0.2 }},
                margin: {{ l: 80, r: 80, t: 80, b: 120 }}
            }}, {{ responsive: true, displayModeBar: true, displaylogo: false }});

            currentData = {{ type: 'timeseries', componentType, timeseriesName, data }};
        }}

        function clearDisplay() {{
            document.getElementById('contentDisplay').innerHTML =
                '<div class="info-panel"><h3>Display Cleared</h3><p>Select component and data type to load new data.</p></div>';
            currentData = null;
        }}

        function showLoading(show) {{
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }}

        function showError(message) {{
            document.getElementById('contentDisplay').innerHTML =
                `<div class="error-panel"><strong>Error:</strong> ${{message}}</div>`;
        }}
    </script>
</body>
</html>'''

    if file_path is not None:
        os.makedirs(file_path, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Network analyzer generated: {output_file}")
    print(f"Components found: {list(component_info['components'].keys())}")

    return output_file


def _load_custom_plots_from_file(file_path, network):
    """
    Dynamically import a custom plots Python file and call its ``get_plots(network)`` function.

    The file must define a function ``get_plots(network)`` that returns a list of
    Plotly figure objects.
    """
    file_path = os.path.abspath(file_path)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Custom plots file not found: {file_path}")

    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if not hasattr(module, 'get_plots'):
        raise AttributeError(
            f"Custom plots file '{file_path}' must define a function: get_plots(network)"
        )

    return module.get_plots(network)


def _extract_component_info(network, currency='$', custom_plots=None):
    """
    Extract component information from a PyPSA network using the new components API.

    All components are discovered dynamically from ``network.components`` — no
    hard-coded component lists. Timeseries attributes are read directly from
    each component's ``.dynamic`` mapping.
    """

    component_info = {
        'summary': {},
        'components': {},
        'custom_plots': {}
    }

    # --- Snapshot / multi-index detection ----------------------------------
    is_multi_index = isinstance(network.snapshots, pd.MultiIndex)
    if is_multi_index:
        ts_level = network.snapshots.get_level_values(1)
        try:
            snapshot_time_index = ts_level.strftime('%Y-%m-%d %H:%M:%S').tolist()
        except AttributeError:
            snapshot_time_index = [str(t) for t in ts_level]
        period_values = network.snapshots.get_level_values(0)
        snapshot_period_index = [str(p) for p in period_values]
        periods = [str(p) for p in period_values.unique()]
        snapshot_time_range = {
            'start': str(ts_level[0]),
            'end': str(ts_level[-1]),
            'periods': len(network.snapshots)
        }
    else:
        snapshot_time_index = network.snapshots.strftime('%Y-%m-%d %H:%M:%S').tolist()
        snapshot_period_index = None
        periods = None
        snapshot_time_range = {
            'start': str(network.snapshots[0]),
            'end': str(network.snapshots[-1]),
            'periods': len(network.snapshots)
        }

    # --- Dynamic component discovery via new PyPSA API ---------------------
    for comp_name, comp in network.components.items():
        static_df = comp.static

        if static_df.empty:
            continue

        component_info['summary'][comp_name] = len(static_df)
        component_info['components'][comp_name] = {
            'static': {},
            'timeseries': {}
        }

        # Static columns
        for col in static_df.columns:
            data_dict = static_df[col].to_dict()
            component_info['components'][comp_name]['static'][col] = {
                str(k): str(v) for k, v in data_dict.items()
            }

        # Timeseries: iterate over comp.dynamic (dict of DataFrames)
        for attr_name, ts_df in comp.dynamic.items():
            if ts_df.empty:
                continue

            unit = _get_unit_for_attribute(attr_name, currency=currency)
            ts_data = {str(col): ts_df[col].tolist() for col in ts_df.columns}

            component_info['components'][comp_name]['timeseries'][attr_name] = {
                'data': ts_data,
                'time_index': snapshot_time_index,
                'time_range': snapshot_time_range,
                'unit': unit
            }

    component_info['summary']['snapshots'] = len(network.snapshots)
    component_info['summary']['is_multi_index'] = is_multi_index
    if is_multi_index:
        component_info['summary']['periods'] = periods
        component_info['summary']['period_index'] = snapshot_period_index

    # --- Network metadata --------------------------------------------------
    network_info = {
        'Network Name': network.name or '(unnamed)',
        'PyPSA Version': network.pypsa_version,
        'Objective': str(network.objective),
        'Objective Constant': str(network._objective_constant),
        'Linearised Unit Commitment': str(network._linearized_uc),
        'Multi Invest': str(network._multi_invest),
        'SRID': str(network.srid),
    }
    if hasattr(network, 'meta') and network.meta:
        for key, value in network.meta.items():
            network_info[f'Metadata - {key}'] = str(value)
    component_info['summary']['network_info'] = network_info

    # --- Global constraints ------------------------------------------------
    gc = network.components.get('global_constraints')
    if gc is not None:
        gc_df = gc.static
        if not gc_df.empty:
            gc_list = []
            for idx, row in gc_df.iterrows():
                entry = {'name': idx}
                for col in gc_df.columns:
                    entry[col] = (
                        f"{row[col]:.2f}" if col == 'mu' and row[col] is not None
                        else str(row[col]) if row[col] is not None
                        else 'N/A'
                    )
                gc_list.append(entry)
            component_info['summary']['global_constraints'] = gc_list

    # --- Custom plots ------------------------------------------------------
    if custom_plots is not None:
        if isinstance(custom_plots, str):
            plots = _load_custom_plots_from_file(custom_plots, network)
        else:
            plots = custom_plots

        import plotly.io as pio
        import json as _json

        plot_names = []
        for i, fig in enumerate(plots):
            title_text = (
                fig.layout.title.text
                if fig.layout.title and fig.layout.title.text
                else f"Plot {i + 1}"
            )
            plot_names.append(title_text)
            fig_dict = _json.loads(pio.to_json(fig))
            component_info['custom_plots'][title_text] = {
                'data': fig_dict['data'],
                'layout': fig_dict['layout']
            }

        component_info['summary']['custom_plots'] = plot_names

    return component_info


def _get_unit_for_attribute(attr, currency='$'):
    """Return a human-readable unit string for a known timeseries attribute."""
    unit_map = {
        'p': 'MW', 'q': 'MVAr',
        'p0': 'MW', 'p1': 'MW', 'p2': 'MW', 'p3': 'MW', 'p4': 'MW',
        'q0': 'MVAr', 'q1': 'MVAr',
        'p_set': 'MW', 'q_set': 'MVAr',
        'e': 'MWh', 'e_set': 'MWh',
        'state_of_charge': 'MWh',
        'v_mag_pu': 'p.u.', 'v_ang': 'rad',
        'p_max_pu': 'p.u.', 'p_min_pu': 'p.u.',
        'e_max_pu': 'p.u.', 'e_min_pu': 'p.u.',
        's_max_pu': 'p.u.',
        'efficiency': 'p.u.', 'efficiency2': 'p.u.', 'efficiency3': 'p.u.',
        'marginal_cost': f'{currency}/MWh',
        'marginal_price': f'{currency}/MWh',
        'standing_loss': 'p.u.',
    }
    return unit_map.get(attr, 'Value')
