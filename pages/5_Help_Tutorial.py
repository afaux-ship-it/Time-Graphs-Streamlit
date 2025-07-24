"""📚 Help & Tutorial page – static markdown pulled from original app."""
from __future__ import annotations

import streamlit as st
from utils.session_init import ensure_session_state

ensure_session_state()

st.markdown('<h2 class="subheader">📚 Help & Tutorial</h2>', unsafe_allow_html=True)

st.markdown(
    """
### 🚀 Quick Start Guide

1. **📁 Upload Data**: Start by uploading your CSV, Excel, JSON, or TSV files
2. **🕐 Set Time Column**: Let the app detect your date/time column or select manually
3. **📊 Create Charts**: Choose variables and chart types to visualize your data
4. **💾 Export**: Download your charts in various formats

### 📋 Supported File Formats

| Format | Extensions | Notes |
|--------|-----------|---------|
| CSV | .csv | Most common format, supports various encodings |
| Excel | .xlsx, .xls | Both modern and legacy Excel formats |
| JSON | .json | Flexible structure, nested objects supported |
| TSV | .tsv | Tab-separated values |

### 🕐 Date/Time Formats

The app automatically detects many date formats:
- **Standard**: 2023-12-25, 12/25/2023, 25/12/2023
- **Natural**: December 25, 2023, 25 Dec 2023
- **Timestamps**: Unix timestamps (seconds/milliseconds)
- **ISO**: 2023-12-25T14:30:00Z
- **Custom**: Use strptime patterns for unusual formats

### 📊 Chart Types

- **Line Charts**: Perfect for continuous time series data
- **Scatter Plots**: Show relationships with optional trendlines
- **Area Charts**: Emphasize cumulative values over time
- **Bar Charts**: Compare discrete time periods
- **Box Plots**: Statistical summaries grouped by time

### 💡 Tips & Best Practices

- **Large Files**: For files over 10MB, consider sampling or filtering
- **Date Issues**: If auto-detection fails, try manual format specification
- **Performance**: Use date range filters for large datasets
- **Colors**: Choose color palettes appropriate for your audience
- **Export**: SVG format is best for publications, PNG for presentations

### ❓ Troubleshooting

**File Upload Issues:**
- Check file size (max 200MB)
- Ensure file format is supported
- Try different encoding if CSV fails

**Date Parsing Issues:**
- Check for consistent date format in your data
- Use custom format strings for unusual formats
- Clean data in external tool if needed

**Performance Issues:**
- Filter data by date range
- Reduce number of variables plotted
- Use sampling for very large datasets

### 📞 Support

Having issues? Here are some resources:
- Check the troubleshooting section above
- Review your data format and structure
- Try with the sample data to test functionality
""",
    unsafe_allow_html=True,
)
