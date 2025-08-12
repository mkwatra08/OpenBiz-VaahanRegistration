# Vehicle Registration Analytics Dashboard

## Overview

This is a Streamlit-based analytics dashboard for vehicle registration data analysis in India. The application focuses on providing investment-grade insights through Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) growth metrics, market share analysis, and interactive visualizations. The dashboard simulates real-time vehicle registration trend analysis using synthetic data that mimics the structure and patterns of actual Vahan (Indian vehicle registration) data.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Wide layout with expandable sidebar for filters
- **Interactivity**: Real-time filtering and date range selection
- **Responsive Design**: Adaptive layout for different screen sizes

### Data Architecture
- **Data Collection**: `VahanDataCollector` class handles data acquisition from external sources
- **Data Processing**: `DataProcessor` class manages data transformation and metric calculations
- **Data Flow**: Raw data → Processing → Visualization pipeline
- **Caching**: Streamlit `@st.cache_resource` for component initialization optimization

### Visualization Architecture
- **Charting Library**: Plotly for interactive visualizations
- **Chart Types**: Timeline charts, growth rate bars, market share pies, scatter plots, heatmaps
- **Color Consistency**: Predefined color palette across all visualizations
- **Interactivity**: Configurable display modes and interactive controls

### Component Design Pattern
- **Modular Architecture**: Separate classes for data collection, processing, and visualization
- **Single Responsibility**: Each component handles one specific concern
- **Dependency Injection**: Components are initialized and passed between modules
- **Error Handling**: Comprehensive try-catch blocks with user-friendly error messages

### Data Processing Pipeline
- **Time Series Processing**: Automatic date parsing and time-based column generation
- **Growth Calculations**: YoY and QoQ growth rate computations
- **Rolling Averages**: Smoothed trend analysis
- **Market Share Analysis**: Relative performance calculations
- **Performance Indicators**: Investment-focused metrics

### Utility Functions
- **Number Formatting**: Automatic scaling with K/M/B suffixes
- **Growth Rate Calculations**: Percentage change computations
- **Data Validation**: Input sanitization and error handling

## External Dependencies

### Core Framework Dependencies
- **Streamlit**: Web application framework for interactive dashboards
- **Pandas**: Data manipulation and analysis library
- **NumPy**: Numerical computing support

### Visualization Dependencies
- **Plotly Express**: High-level plotting interface
- **Plotly Graph Objects**: Low-level plotting control for custom visualizations

### Data Collection Dependencies
- **Requests**: HTTP library for web scraping and API calls
- **Trafilatura**: Web content extraction library
- **JSON**: Data serialization for API responses

### Python Standard Library
- **DateTime**: Date and time manipulation
- **Time**: Sleep and timing functions
- **RE**: Regular expression processing
- **Typing**: Type hints for better code documentation

### Data Sources
- **Vahan Portal**: Indian vehicle registration data (simulated access)
- **Synthetic Data Generation**: Fallback realistic data generation for demonstration

### Potential Future Integrations
- **Database**: Could integrate with PostgreSQL or other databases for persistent storage
- **Authentication**: Could add user authentication for multi-user access
- **Export Capabilities**: Could add Excel/CSV export functionality
- **Real-time APIs**: Could integrate with actual government data APIs when available