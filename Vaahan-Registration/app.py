import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from data_collector import VahanDataCollector
from data_processor import DataProcessor
from visualizations import VehicleRegistrationVisualizer
from utils import format_number, calculate_growth_rate

# Configure page
st.set_page_config(
    page_title="Vehicle Registration Analytics Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def initialize_components():
    """Initialize data collector, processor, and visualizer"""
    collector = VahanDataCollector()
    processor = DataProcessor()
    visualizer = VehicleRegistrationVisualizer()
    return collector, processor, visualizer

def main():
    # Header
    st.title("🚗 Vehicle Registration Analytics Dashboard")
    st.markdown("**Investment-focused analysis of Indian vehicle registration trends**")
    
    # Initialize components
    try:
        collector, processor, visualizer = initialize_components()
    except Exception as e:
        st.error(f"Failed to initialize dashboard components: {str(e)}")
        return
    
    # Sidebar filters
    st.sidebar.header("📊 Dashboard Filters")
    
    # Date range selection
    st.sidebar.subheader("Date Range")
    end_date = st.sidebar.date_input(
        "End Date",
        value=datetime.now().date(),
        max_value=datetime.now().date()
    )
    start_date = st.sidebar.date_input(
        "Start Date",
        value=end_date - timedelta(days=365),
        max_value=end_date
    )
    
    # Vehicle category filter
    st.sidebar.subheader("Vehicle Category")
    vehicle_categories = st.sidebar.multiselect(
        "Select Categories",
        options=["2W", "3W", "4W", "Commercial", "Others"],
        default=["2W", "3W", "4W"]
    )
    
    # State filter
    st.sidebar.subheader("Geographic Filter")
    selected_states = st.sidebar.multiselect(
        "Select States (leave empty for all)",
        options=[
            "Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", 
            "Uttar Pradesh", "Rajasthan", "West Bengal", "Telangana",
            "Haryana", "Delhi", "Punjab", "Madhya Pradesh"
        ],
        default=[]
    )
    
    # Manufacturer filter
    st.sidebar.subheader("Manufacturer Filter")
    top_manufacturers = [
        "Hero MotoCorp", "Honda", "TVS", "Bajaj", "Royal Enfield",
        "Maruti Suzuki", "Hyundai", "Tata Motors", "Mahindra", "Kia"
    ]
    selected_manufacturers = st.sidebar.multiselect(
        "Select Manufacturers (leave empty for all)",
        options=top_manufacturers,
        default=[]
    )
    
    # Data refresh button
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Main content area
    if st.button("📥 Load Vehicle Registration Data"):
        with st.spinner("Collecting and processing vehicle registration data..."):
            try:
                # Collect data
                raw_data = collector.collect_vahan_data(
                    start_date=start_date,
                    end_date=end_date,
                    states=selected_states if selected_states else None,
                    vehicle_categories=vehicle_categories
                )
                
                if raw_data.empty:
                    st.warning("No data found for the selected criteria. Please adjust your filters and try again.")
                    return
                
                # Process data
                processed_data = processor.process_registration_data(raw_data)
                
                # Calculate growth metrics
                growth_metrics = processor.calculate_growth_metrics(processed_data)
                
                # Store in session state
                st.session_state['processed_data'] = processed_data
                st.session_state['growth_metrics'] = growth_metrics
                st.session_state['raw_data'] = raw_data
                
                st.success(f"Successfully loaded {len(processed_data):,} records")
                
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                st.info("Please check your internet connection and try again.")
                return
    
    # Display dashboard if data is available
    if 'processed_data' in st.session_state:
        processed_data = st.session_state['processed_data']
        growth_metrics = st.session_state['growth_metrics']
        
        # Apply manufacturer filter if selected
        if selected_manufacturers:
            processed_data = processed_data[
                processed_data['manufacturer'].isin(selected_manufacturers)
            ]
        
        # Key metrics row
        st.header("📈 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_registrations = processed_data['registrations'].sum()
            st.metric(
                "Total Registrations",
                format_number(total_registrations),
                delta=f"{growth_metrics.get('total_yoy_growth', 0):.1f}% YoY"
            )
        
        with col2:
            avg_monthly = processed_data.groupby('month')['registrations'].sum().mean()
            st.metric(
                "Avg Monthly Registrations",
                format_number(avg_monthly),
                delta=f"{growth_metrics.get('monthly_growth', 0):.1f}% vs prev period"
            )
        
        with col3:
            top_category = processed_data.groupby('category')['registrations'].sum().idxmax()
            top_category_share = (
                processed_data[processed_data['category'] == top_category]['registrations'].sum() 
                / total_registrations * 100
            )
            st.metric(
                "Leading Category",
                top_category,
                delta=f"{top_category_share:.1f}% market share"
            )
        
        with col4:
            if len(processed_data['state'].unique()) > 1:
                top_state = processed_data.groupby('state')['registrations'].sum().idxmax()
                st.metric(
                    "Top Performing State",
                    top_state,
                    delta="By volume"
                )
            else:
                st.metric("Data Coverage", f"{len(processed_data)} records", "Current dataset")
        
        # Main visualizations
        st.header("📊 Registration Trends Analysis")
        
        # Time series chart
        fig_timeline = visualizer.create_timeline_chart(processed_data)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Growth analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("YoY Growth by Category")
            fig_yoy = visualizer.create_growth_chart(processed_data, 'yoy')
            st.plotly_chart(fig_yoy, use_container_width=True)
        
        with col2:
            st.subheader("QoQ Growth by Category")
            fig_qoq = visualizer.create_growth_chart(processed_data, 'qoq')
            st.plotly_chart(fig_qoq, use_container_width=True)
        
        # Market share analysis
        st.subheader("Market Share Distribution")
        fig_market_share = visualizer.create_market_share_chart(processed_data)
        st.plotly_chart(fig_market_share, use_container_width=True)
        
        # Geographic analysis (if multiple states)
        if len(processed_data['state'].unique()) > 1:
            st.subheader("State-wise Performance")
            fig_geo = visualizer.create_geographic_chart(processed_data)
            st.plotly_chart(fig_geo, use_container_width=True)
        
        # Manufacturer analysis (if manufacturer data available)
        if 'manufacturer' in processed_data.columns and not processed_data['manufacturer'].isna().all():
            st.subheader("Top Manufacturers Performance")
            fig_manu = visualizer.create_manufacturer_chart(processed_data)
            st.plotly_chart(fig_manu, use_container_width=True)
        
        # Data export section
        st.header("📥 Data Export")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download Processed Data"):
                csv_data = processed_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"vehicle_registration_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📈 Download Growth Metrics"):
                metrics_df = pd.DataFrame([growth_metrics])
                metrics_csv = metrics_df.to_csv(index=False)
                st.download_button(
                    label="Download Metrics CSV",
                    data=metrics_csv,
                    file_name=f"growth_metrics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Raw data preview
        with st.expander("🔍 View Raw Data Sample"):
            st.dataframe(processed_data.head(100), use_container_width=True)
    
    else:
        # Welcome message
        st.info("👆 Click 'Load Vehicle Registration Data' to begin analysis")
        
        # Sample insights
        st.subheader("📋 Dashboard Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📊 Analytics Capabilities:**
            - Year-over-Year (YoY) growth analysis
            - Quarter-over-Quarter (QoQ) trends
            - Vehicle category performance
            - Geographic distribution insights
            - Manufacturer market share
            """)
        
        with col2:
            st.markdown("""
            **🎯 Investor Focus:**
            - Growth rate calculations
            - Market trend identification
            - Performance benchmarking
            - Data export capabilities
            - Professional visualizations
            """)

if __name__ == "__main__":
    main()
