# Changelog

## Version 0.2.0 (2025-11-06)

### New Features
1. ✅ **Export Button Removed** - Cleaner interface without export functionality
2. ✅ **Network Summary View** - Display network properties, optimization results, and metadata
3. ✅ **Global Constraints View** - Show global constraints with currency-formatted dual values
4. ✅ **Explore Map Integration** - Interactive geographical network visualization
5. ✅ **Custom Plots Support** - Embed user-provided Plotly visualizations

### Bug Fixes
- **Custom Plots**: Fixed JavaScript error by properly serializing Plotly figures using `plotly.io.to_json()`
- **Explore Map**: Fixed map loading issue by generating map file in same directory as output HTML
- **Map API**: Added support for both old (`network.explore()`) and new (`network.plot.explore()`) PyPSA APIs

### Improvements
- Better error handling for map generation
- Unique map filenames using UUID to prevent conflicts
- Improved documentation with comprehensive examples
- Updated README with all features

### API Changes
- **Function name**: Changed from `html_viewer()` to `html_network()`
- **New parameters**:
  - `explore` (bool): Enable interactive map (default: False)
  - `custom_plots` (list): List of Plotly figure objects (default: None)
  - `output_dir` (internal): Output directory for proper file organization

### Files Updated
- `NetworkViewer.ipynb` - Main development notebook
- `pypsa_network_viewer.py` - Standalone module
- `pypsa_network_viewer/viewer_updated.py` - Package version
- `example.ipynb` - Comprehensive usage examples
- `README.md` - Updated documentation
- `EXAMPLE_USAGE.md` - Detailed usage guide

### Compatibility
- Python 3.8+
- PyPSA 0.25+ (tested with 0.35.1)
- Plotly 5.0+
- Works with both old and new PyPSA map APIs

## Version 0.1.0 (Initial Release)

### Features
- Basic HTML viewer for PyPSA networks
- Component data exploration
- Timeseries visualization
- Export functionality
