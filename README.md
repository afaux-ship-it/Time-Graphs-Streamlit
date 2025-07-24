# Graph Anything Over Time 📈

A powerful and user-friendly Streamlit application for creating beautiful time-series visualizations from various data formats. Transform your temporal data into publication-ready charts in minutes!

## 🌟 Features

### 📁 Multi-Format Data Support
- **CSV, Excel, JSON, TSV**: Upload files in various formats
- **Intelligent Parsing**: Automatic encoding detection and error handling
- **Multiple Datasets**: Handle multiple files simultaneously
- **Large File Support**: Process files up to 200MB

### 🕐 Smart Date/Time Detection
- **Automatic Detection**: AI-powered identification of date/time columns
- **Format Flexibility**: Support for 20+ date formats including:
  - Standard formats (YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)
  - Natural language (February 23, 2023, 23 Feb 2023)
  - Unix timestamps (seconds/milliseconds)
  - ISO 8601 strings
  - Custom patterns with strptime

### 📊 Rich Visualization Options
- **Multiple Chart Types**: Line, scatter, area, bar, box plots, candlestick, heatmaps
- **Advanced Features**: Multi-axis plots, subplot grids, trendlines
- **Customization**: Colors, themes, markers, opacity, annotations
- **Interactive Elements**: Zoom, pan, hover information

### 💾 Export Capabilities
- **Multiple Formats**: PNG, JPEG, SVG, PDF, HTML
- **High Quality**: Publication-ready with customizable DPI
- **Interactive Export**: HTML files with full interactivity

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (recommended: 3.9-3.11)
- Virtual environment tool (venv or conda)

### Installation

1. **Clone or download this repository**
2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv graph-time-env
   graph-time-env\Scripts\activate
   
   # macOS/Linux
   python -m venv graph-time-env
   source graph-time-env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser to:** `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Upload Data 📁
- Drag and drop or select files to upload
- Supported formats: CSV, Excel (.xlsx, .xls), JSON, TSV
- View automatic data preview and statistics

### Step 2: Configure Time Column 🕐
- Let the app auto-detect your date/time columns
- Review confidence scores and format hints
- Manually specify custom formats if needed

### Step 3: Create Visualizations 📊
- Select variables to plot
- Choose from multiple chart types
- Customize colors, styling, and layout
- Apply date range filters

### Step 4: Export Results 💾
- Download charts in various formats
- Choose resolution and quality settings
- Export interactive HTML versions

## 🏗️ Project Structure

```
graph-anything-over-time/
├── app.py                   # Main Streamlit application
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── file_handler.py     # File upload and processing
│   ├── data_parser.py      # Date/time parsing utilities
│   └── plot_generator.py   # Chart generation functions
└── context/                # Project documentation
    ├── overview.md         # Project overview
    └── features.md         # Detailed feature specs
```

## 🎯 Use Cases

- **Data Analysts**: Rapid prototyping of time-series visualizations
- **Students & Researchers**: Academic data visualization across disciplines
- **Business Professionals**: KPI tracking and trend analysis
- **Anyone**: Quick insights from temporal data without coding

## 🔧 Technical Details

### Core Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive plotting library
- **NumPy**: Numerical computing
- **python-dateutil**: Advanced date parsing

### Performance Features
- **Intelligent Sampling**: Handle large datasets efficiently
- **Memory Management**: Optimized for large file processing
- **Caching**: Speed up repeated operations
- **Progress Indicators**: Visual feedback for long operations

## 📊 Supported Data Types

### File Formats
| Format | Extensions | Notes |
|--------|------------|-------|
| CSV | .csv | Various encodings supported |
| Excel | .xlsx, .xls | Modern and legacy formats |
| JSON | .json | Flexible nested structures |
| TSV | .tsv | Tab-separated values |

### Date/Time Formats
- **Standard**: MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD
- **Natural**: "February 23, 2023", "23 Feb 2023"
- **Timestamps**: Unix seconds/milliseconds
- **ISO 8601**: Standard datetime strings
- **Custom**: User-defined strptime patterns

## 🎨 Chart Types

1. **Line Charts**: Continuous time series data
2. **Scatter Plots**: Relationships with optional trendlines
3. **Area Charts**: Cumulative values visualization
4. **Bar Charts**: Discrete time period comparisons
5. **Box Plots**: Statistical summaries by time groups
6. **Candlestick Charts**: OHLC financial data
7. **Heatmaps**: Time vs category intensity
8. **Multi-Axis Plots**: Different scales on same chart
9. **Subplot Grids**: Multiple related visualizations

## 💡 Tips & Best Practices

### Data Preparation
- Ensure consistent date formats within columns
- Clean missing or invalid date entries
- Consider sampling very large datasets (>1M rows)

### Performance Optimization
- Use date range filters for large datasets
- Limit number of variables plotted simultaneously
- Enable caching for repeated operations

### Visualization Best Practices
- Choose appropriate chart types for your data
- Use color palettes suited to your audience
- Add meaningful titles and axis labels
- Consider accessibility in color choices

## 🐛 Troubleshooting

### Common Issues

**File Upload Problems:**
- Check file size limits (200MB max)
- Verify file format is supported
- Try different CSV encodings if parsing fails

**Date Parsing Issues:**
- Ensure consistent date formats in data
- Use manual format specification for unusual patterns
- Check for hidden characters or extra spaces

**Performance Issues:**
- Apply date range filters to reduce data size
- Reduce number of plotted variables
- Close unused browser tabs to free memory

## 🔄 Development

### Adding New Features
1. Create feature branch
2. Add utility functions in `/utils/`
3. Update main app interface
4. Test with various data formats
5. Update documentation

### Testing
- Test with various file formats and sizes
- Verify date parsing with different formats
- Check export functionality across formats
- Validate performance with large datasets

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Made with ❤️ for the data visualization community**
