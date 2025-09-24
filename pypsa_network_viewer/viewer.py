"""
PyPSA Network Viewer - Main module containing the html_viewer function.
"""

import json
import os


def html_viewer(network, file_path=None, file_name=None, title="PyPSA Network Analyzer", currency='$'):
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
        Currency symbol for cost-related units (default: '$')

    Returns:
    --------
    str : Path to generated HTML file
    """

    # Extract component information
    component_info = _extract_component_info(network, currency=currency)

    # Convert data to JSON for JavaScript
    data_json = json.dumps(component_info, indent=2, default=str)

    # Generate HTML content
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
                <label class="control-label">Time Series</label>
                <select id="timeseriesSelect" disabled>
                    <option value="">Select timeseries...</option>
                </select>
            </div>
        </div>

        <div class="controls-section">
            <div class="control-group">
                <button onclick="loadData()" id="loadButton" disabled>Load Data</button>
            </div>
            <div class="control-group">
                <button onclick="exportData()" id="exportButton" disabled>Export Data</button>
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
                        <li>Choose a component type (generators, links, stores, etc.)</li>
                        <li>Select whether you want to view static properties or timeseries data</li>
                        <li>For timeseries, choose which specific timeseries to plot</li>
                        <li>Click "Load Data" to display the information</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Network data from Python
        const networkData = {data_json};

        let currentData = null;

        // Initialize the interface
        document.addEventListener('DOMContentLoaded', function() {{
            populateNetworkSummary();
            populateComponentTypes();
            setupEventListeners();
        }});

        function populateNetworkSummary() {{
            const summaryDiv = document.getElementById('networkSummary');
            const summary = networkData.summary;

            let summaryHTML = '';
            Object.entries(summary).forEach(([key, value]) => {{
                summaryHTML += `
                    <div class="summary-card">
                        <h3>${{value}}</h3>
                        <p>${{key.replace('_', ' ').toUpperCase()}}</p>
                    </div>
                `;
            }});

            summaryDiv.innerHTML = summaryHTML;
        }}

        function populateComponentTypes() {{
            const select = document.getElementById('componentTypeSelect');
            const components = networkData.components;

            Object.keys(components).forEach(componentType => {{
                const option = document.createElement('option');
                option.value = componentType;
                option.textContent = componentType.charAt(0).toUpperCase() + componentType.slice(1);
                select.appendChild(option);
            }});
        }}

        function setupEventListeners() {{
            document.getElementById('componentTypeSelect').addEventListener('change', onComponentTypeChange);
            document.getElementById('dataTypeSelect').addEventListener('change', onDataTypeChange);
        }}

        function onComponentTypeChange() {{
            const componentType = document.getElementById('componentTypeSelect').value;
            const dataTypeSelect = document.getElementById('dataTypeSelect');
            const timeseriesSelect = document.getElementById('timeseriesSelect');

            if (componentType) {{
                dataTypeSelect.disabled = false;
                dataTypeSelect.value = '';
                timeseriesSelect.disabled = true;
                timeseriesSelect.innerHTML = '<option value="">Select timeseries...</option>';
                document.getElementById('loadButton').disabled = true;
            }} else {{
                dataTypeSelect.disabled = true;
                timeseriesSelect.disabled = true;
                document.getElementById('loadButton').disabled = true;
            }}
        }}

        function onDataTypeChange() {{
            const componentType = document.getElementById('componentTypeSelect').value;
            const dataType = document.getElementById('dataTypeSelect').value;
            const timeseriesSelect = document.getElementById('timeseriesSelect');

            if (dataType === 'static') {{
                timeseriesSelect.disabled = true;
                document.getElementById('loadButton').disabled = false;
            }} else if (dataType === 'timeseries') {{
                const timeseries = networkData.components[componentType].timeseries;
                timeseriesSelect.innerHTML = '<option value="">Select timeseries...</option>';

                Object.keys(timeseries).forEach(ts => {{
                    const option = document.createElement('option');
                    option.value = ts;
                    option.textContent = ts;
                    timeseriesSelect.appendChild(option);
                }});

                timeseriesSelect.disabled = false;
                timeseriesSelect.addEventListener('change', function() {{
                    document.getElementById('loadButton').disabled = !this.value;
                }});
            }}
        }}

        function loadData() {{
            const componentType = document.getElementById('componentTypeSelect').value;
            const dataType = document.getElementById('dataTypeSelect').value;
            const timeseries = document.getElementById('timeseriesSelect').value;

            if (!componentType || !dataType) return;

            showLoading(true);

            setTimeout(() => {{
                try {{
                    if (dataType === 'static') {{
                        displayStaticData(componentType);
                    }} else if (dataType === 'timeseries' && timeseries) {{
                        displayTimeseriesData(componentType, timeseries);
                    }}
                    document.getElementById('exportButton').disabled = false;
                }} catch (error) {{
                    showError('Error loading data: ' + error.message);
                }}
                showLoading(false);
            }}, 500);
        }}

        function displayStaticData(componentType) {{
            const data = networkData.components[componentType].static;
            const contentDiv = document.getElementById('contentDisplay');

            if (!data || Object.keys(data).length === 0) {{
                contentDiv.innerHTML = `
                    <div class="error-panel">
                        <strong>No static data available for ${{componentType}}</strong>
                    </div>
                `;
                return;
            }}

            // Create table
            const columns = Object.keys(data);
            const indices = Object.keys(data[columns[0]] || {{}});

            let tableHTML = `
                <div class="info-panel">
                    <h3>${{componentType.charAt(0).toUpperCase() + componentType.slice(1)}} - Static Data</h3>
                    <p>Showing ${{indices.length}} components with ${{columns.length}} properties</p>
                </div>
                <div class="data-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Component</th>
                                ${{columns.map(col => `<th>${{col}}</th>`).join('')}}
                            </tr>
                        </thead>
                        <tbody>
            `;

            indices.forEach(index => {{
                tableHTML += `<tr><td><strong>${{index}}</strong></td>`;
                columns.forEach(col => {{
                    const value = data[col][index];
                    const displayValue = value !== null && value !== undefined ? value : 'N/A';
                    tableHTML += `<td>${{displayValue}}</td>`;
                }});
                tableHTML += `</tr>`;
            }});

            tableHTML += `
                        </tbody>
                    </table>
                </div>
            `;

            contentDiv.innerHTML = tableHTML;
            currentData = {{ type: 'static', componentType, data }};
        }}

        function displayTimeseriesData(componentType, timeseriesName) {{
            const data = networkData.components[componentType].timeseries[timeseriesName];
            const contentDiv = document.getElementById('contentDisplay');

            if (!data || Object.keys(data.data).length === 0) {{
                contentDiv.innerHTML = `
                    <div class="error-panel">
                        <strong>No timeseries data available for ${{componentType}} - ${{timeseriesName}}</strong>
                    </div>
                `;
                return;
            }}

            // Create info panel
            let infoHTML = `
                <div class="info-panel">
                    <h3>${{componentType.charAt(0).toUpperCase() + componentType.slice(1)}} - ${{timeseriesName}}</h3>
                    <p><strong>Time Range:</strong> ${{data.time_range.start}} to ${{data.time_range.end}}</p>
                    <p><strong>Components:</strong> ${{Object.keys(data.data).length}} series with ${{data.time_range.periods}} time periods</p>
                </div>
                <div class="plot-container">
                    <div id="timeseriesPlot" style="width: 100%; height: 600px;"></div>
                </div>
            `;

            contentDiv.innerHTML = infoHTML;

            // Create plotly traces
            const traces = [];
            const timeIndex = data.time_index.map(t => new Date(t));

            Object.entries(data.data).forEach(([component, values]) => {{
                traces.push({{
                    x: timeIndex,
                    y: values,
                    type: 'scatter',
                    mode: 'lines',
                    name: component,
                    line: {{ width: 2 }}
                }});
            }});

            const layout = {{
                title: `${{componentType}} - ${{timeseriesName}}`,
                xaxis: {{ title: 'Time', type: 'date' }},
                yaxis: {{ title: data.unit || 'Value' }},
                hovermode: 'x unified',
                legend: {{ orientation: 'h', x: 0.5, xanchor: 'center', y: -0.2 }},
                margin: {{ l: 80, r: 80, t: 80, b: 120 }}
            }};

            const config = {{
                responsive: true,
                displayModeBar: true,
                displaylogo: false
            }};

            Plotly.newPlot('timeseriesPlot', traces, layout, config);
            currentData = {{ type: 'timeseries', componentType, timeseriesName, data }};
        }}

        function exportData() {{
            if (!currentData) return;

            const filename = `${{currentData.componentType}}_${{currentData.type === 'timeseries' ? currentData.timeseriesName : 'static'}}_data.json`;
            const dataStr = JSON.stringify(currentData.data, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});

            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = filename;
            link.click();
        }}

        function clearDisplay() {{
            document.getElementById('contentDisplay').innerHTML = `
                <div class="info-panel">
                    <h3>Display Cleared</h3>
                    <p>Select component and data type to load new data.</p>
                </div>
            `;
            currentData = null;
            document.getElementById('exportButton').disabled = true;
        }}

        function showLoading(show) {{
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }}

        function showError(message) {{
            document.getElementById('contentDisplay').innerHTML = `
                <div class="error-panel">
                    <strong>Error:</strong> ${{message}}
                </div>
            `;
        }}
    </script>
</body>
</html>'''

    # Set default file name if not provided
    if file_name is None:
        file_name = "network_analyzer.html"

    # Set default file path if not provided
    if file_path is None:
        output_file = file_name
    else:
        output_file = os.path.join(file_path, file_name)

    # Create directory if it doesn't exist
    if file_path is not None:
        os.makedirs(file_path, exist_ok=True)

    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Network analyzer generated: {output_file}")
    print(f"Components found: {list(component_info['components'].keys())}")

    return output_file


def _extract_component_info(network, currency='$'):
    """
    Extract component information from PyPSA network.
    """

    component_info = {
        'summary': {},
        'components': {}
    }

    # Main component types to analyze
    component_types = {
        'generators': network.generators,
        'links': network.links,
        'loads': network.loads,
        'stores': network.stores,
        'storage_units': network.storage_units,
        'lines': network.lines,
        'transformers': network.transformers,
        'buses': network.buses
    }

    # Timeseries attributes for each component type
    timeseries_attrs = {
        'generators': ['p', 'q', 'p_max_pu', 'p_min_pu', 'p_set', 'q_set', 'marginal_cost', 'efficiency'],
        'links': ['p0', 'p1', 'p2', 'p_max_pu', 'p_min_pu', 'efficiency', 'p_set'],
        'loads': ['p', 'q', 'p_set', 'q_set'],
        'stores': ['p', 'e', 'e_max_pu', 'e_min_pu', 'e_set', 'standing_loss'],
        'storage_units': ['p', 'q', 'state_of_charge', 'p_max_pu', 'p_min_pu', 'p_set', 'q_set'],
        'lines': ['p0', 'p1', 'q0', 'q1', 's_max_pu'],
        'transformers': ['p0', 'p1', 'q0', 'q1', 's_max_pu'],
        'buses': ['v_mag_pu', 'v_ang', 'p', 'q', 'marginal_price']
    }

    # Extract summary information
    for comp_type, comp_df in component_types.items():
        if hasattr(network, comp_type) and not comp_df.empty:
            component_info['summary'][comp_type] = len(comp_df)

    component_info['summary']['snapshots'] = len(network.snapshots)

    # Extract component details
    for comp_type, comp_df in component_types.items():
        if not hasattr(network, comp_type) or comp_df.empty:
            continue

        component_info['components'][comp_type] = {
            'static': {},
            'timeseries': {}
        }

        # Static data
        if not comp_df.empty:
            for col in comp_df.columns:
                # Convert to string representation for JSON serialization
                data_dict = comp_df[col].to_dict()
                # Convert any non-serializable values to strings
                serializable_dict = {str(k): str(v) for k, v in data_dict.items()}
                component_info['components'][comp_type]['static'][col] = serializable_dict

        # Timeseries data
        ts_container = getattr(network, f"{comp_type}_t", None)
        if ts_container is not None:
            # Get all available timeseries attributes for this component type
            available_attrs = []

            # First check our predefined list
            predefined_attrs = timeseries_attrs.get(comp_type, [])
            available_attrs.extend(predefined_attrs)

            # Also dynamically check what actually exists in the container
            for attr_name in dir(ts_container):
                if not attr_name.startswith('_') and hasattr(ts_container, attr_name):
                    attr_obj = getattr(ts_container, attr_name)
                    # Check if it's a DataFrame with data
                    if hasattr(attr_obj, 'empty') and hasattr(attr_obj, 'columns') and not attr_obj.empty:
                        if attr_name not in available_attrs:
                            available_attrs.append(attr_name)

            # Remove duplicates while preserving order
            seen = set()
            unique_attrs = []
            for attr in available_attrs:
                if attr not in seen:
                    seen.add(attr)
                    unique_attrs.append(attr)

            for attr in unique_attrs:
                if hasattr(ts_container, attr):
                    ts_df = getattr(ts_container, attr)
                    # Check if it's a DataFrame and has data
                    if hasattr(ts_df, 'empty') and hasattr(ts_df, 'columns') and not ts_df.empty:
                        # Determine unit based on attribute
                        unit = _get_unit_for_attribute(attr, currency=currency)

                        # Convert timeseries data to serializable format
                        ts_data = {}
                        for col in ts_df.columns:
                            ts_data[str(col)] = ts_df[col].tolist()

                        component_info['components'][comp_type]['timeseries'][attr] = {
                            'data': ts_data,
                            'time_index': network.snapshots.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                            'time_range': {
                                'start': str(network.snapshots[0]),
                                'end': str(network.snapshots[-1]),
                                'periods': len(network.snapshots)
                            },
                            'unit': unit
                        }

    return component_info


def _get_unit_for_attribute(attr, currency='$'):
    """
    Get appropriate unit for timeseries attribute.
    """
    unit_map = {
        'p': 'MW',
        'q': 'MVAr',
        'p0': 'MW',
        'p1': 'MW',
        'p2': 'MW',
        'p_set': 'MW',
        'q_set': 'MVAr',
        'e': 'MWh',
        'e_set': 'MWh',
        'state_of_charge': 'MWh',
        'v_mag_pu': 'p.u.',
        'v_ang': 'rad',
        'p_max_pu': 'p.u.',
        'p_min_pu': 'p.u.',
        'e_max_pu': 'p.u.',
        'e_min_pu': 'p.u.',
        's_max_pu': 'p.u.',
        'efficiency': 'p.u.',
        'marginal_cost': f'{currency}/MWh',
        'marginal_price': f'{currency}/MWh',
        'standing_loss': 'p.u.'
    }

    return unit_map.get(attr, 'Value')