import pandas as pd
import numpy as np
from typing import Union, List, Optional

def format_number(num: Union[int, float], precision: int = 1) -> str:
    """
    Format numbers for display with appropriate suffixes (K, M, B)
    
    Args:
        num: Number to format
        precision: Decimal places for formatting
        
    Returns:
        str: Formatted number string
    """
    if pd.isna(num):
        return "N/A"
    
    num = float(num)
    
    if abs(num) >= 1_000_000_000:
        return f"{num / 1_000_000_000:.{precision}f}B"
    elif abs(num) >= 1_000_000:
        return f"{num / 1_000_000:.{precision}f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:.{precision}f}K"
    else:
        return f"{num:.{precision}f}"

def calculate_growth_rate(current: float, previous: float) -> float:
    """
    Calculate percentage growth rate between two values
    
    Args:
        current: Current period value
        previous: Previous period value
        
    Returns:
        float: Growth rate as percentage
    """
    if previous == 0 or pd.isna(previous) or pd.isna(current):
        return 0.0
    
    return ((current - previous) / previous) * 100

def calculate_compound_annual_growth_rate(end_value: float, start_value: float, periods: int) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR)
    
    Args:
        end_value: Final value
        start_value: Initial value
        periods: Number of periods (years)
        
    Returns:
        float: CAGR as percentage
    """
    if start_value <= 0 or periods <= 0:
        return 0.0
    
    return (((end_value / start_value) ** (1 / periods)) - 1) * 100

def detect_outliers(data: pd.Series, method: str = 'iqr') -> pd.Series:
    """
    Detect outliers in a data series
    
    Args:
        data: Pandas series of numerical data
        method: Method to use ('iqr' or 'zscore')
        
    Returns:
        pd.Series: Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((data - data.mean()) / data.std())
        return z_scores > 3
    
    else:
        raise ValueError("Method must be 'iqr' or 'zscore'")

def smooth_time_series(data: pd.Series, window: int = 7, method: str = 'rolling') -> pd.Series:
    """
    Smooth time series data to reduce noise
    
    Args:
        data: Time series data
        window: Window size for smoothing
        method: Smoothing method ('rolling', 'ewm')
        
    Returns:
        pd.Series: Smoothed data
    """
    if method == 'rolling':
        return data.rolling(window=window, center=True).mean()
    elif method == 'ewm':
        return data.ewm(span=window).mean()
    else:
        raise ValueError("Method must be 'rolling' or 'ewm'")

def calculate_market_concentration(market_shares: List[float]) -> float:
    """
    Calculate Herfindahl-Hirschman Index for market concentration
    
    Args:
        market_shares: List of market shares (as percentages)
        
    Returns:
        float: HHI value (0-10000)
    """
    # Convert percentages to proportions and calculate HHI
    proportions = [share / 100 for share in market_shares]
    hhi = sum(proportion ** 2 for proportion in proportions) * 10000
    return hhi

def categorize_growth_rate(growth_rate: float) -> str:
    """
    Categorize growth rates into descriptive labels
    
    Args:
        growth_rate: Growth rate as percentage
        
    Returns:
        str: Growth category description
    """
    if pd.isna(growth_rate):
        return "Unknown"
    elif growth_rate > 20:
        return "Very High Growth"
    elif growth_rate > 10:
        return "High Growth"
    elif growth_rate > 5:
        return "Moderate Growth"
    elif growth_rate > 0:
        return "Low Growth"
    elif growth_rate > -5:
        return "Slight Decline"
    elif growth_rate > -15:
        return "Moderate Decline"
    else:
        return "Steep Decline"

def validate_data_quality(data: pd.DataFrame) -> dict:
    """
    Validate data quality and return quality metrics
    
    Args:
        data: DataFrame to validate
        
    Returns:
        dict: Data quality metrics
    """
    quality_metrics = {
        'total_rows': len(data),
        'missing_values': data.isnull().sum().to_dict(),
        'duplicate_rows': data.duplicated().sum(),
        'data_types': data.dtypes.to_dict(),
        'memory_usage': data.memory_usage(deep=True).sum(),
    }
    
    # Check for negative values in registration columns
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if 'registration' in col.lower():
            negative_count = (data[col] < 0).sum()
            quality_metrics[f'negative_values_{col}'] = negative_count
    
    # Calculate completeness percentage
    total_cells = len(data) * len(data.columns)
    missing_cells = data.isnull().sum().sum()
    quality_metrics['completeness_percentage'] = ((total_cells - missing_cells) / total_cells) * 100
    
    return quality_metrics

def create_date_features(data: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Create additional date-based features from a date column
    
    Args:
        data: DataFrame containing date column
        date_column: Name of the date column
        
    Returns:
        pd.DataFrame: DataFrame with additional date features
    """
    data = data.copy()
    data[date_column] = pd.to_datetime(data[date_column])
    
    # Basic date features
    data['year'] = data[date_column].dt.year
    data['month'] = data[date_column].dt.month
    data['day'] = data[date_column].dt.day
    data['day_of_week'] = data[date_column].dt.dayofweek
    data['day_of_year'] = data[date_column].dt.dayofyear
    data['week_of_year'] = data[date_column].dt.isocalendar().week
    data['quarter'] = data[date_column].dt.quarter
    
    # Additional features
    data['is_weekend'] = data['day_of_week'].isin([5, 6])
    data['is_month_start'] = data[date_column].dt.is_month_start
    data['is_month_end'] = data[date_column].dt.is_month_end
    data['is_quarter_start'] = data[date_column].dt.is_quarter_start
    data['is_quarter_end'] = data[date_column].dt.is_quarter_end
    
    # Cyclical encoding for better ML performance
    data['month_sin'] = np.sin(2 * np.pi * data['month'] / 12)
    data['month_cos'] = np.cos(2 * np.pi * data['month'] / 12)
    data['day_of_week_sin'] = np.sin(2 * np.pi * data['day_of_week'] / 7)
    data['day_of_week_cos'] = np.cos(2 * np.pi * data['day_of_week'] / 7)
    
    return data

def export_to_excel(data: pd.DataFrame, filename: str, sheet_name: str = 'Data') -> None:
    """
    Export DataFrame to Excel with formatting
    
    Args:
        data: DataFrame to export
        filename: Output filename
        sheet_name: Excel sheet name
    """
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
    except ImportError:
        # Fallback to CSV if openpyxl is not available
        csv_filename = filename.replace('.xlsx', '.csv')
        data.to_csv(csv_filename, index=False)
        print(f"Excel export not available, saved as CSV: {csv_filename}")

def get_investment_insights(data: pd.DataFrame) -> dict:
    """
    Generate investment-focused insights from the data
    
    Args:
        data: Processed vehicle registration data
        
    Returns:
        dict: Investment insights and recommendations
    """
    insights = {}
    
    # Growth momentum analysis
    recent_growth = data.groupby('category')['yoy_growth'].tail(30).mean()
    insights['growth_momentum'] = recent_growth.to_dict()
    
    # Market leader identification
    market_leaders = data.groupby('category')['registrations'].sum().sort_values(ascending=False)
    insights['market_leaders'] = market_leaders.head(3).to_dict()
    
    # Volatility assessment
    volatility = data.groupby('category')['registrations'].std() / data.groupby('category')['registrations'].mean()
    insights['volatility_scores'] = volatility.to_dict()
    
    # Trend classification
    trend_analysis = {}
    for category in data['category'].unique():
        cat_data = data[data['category'] == category]['yoy_growth'].dropna()
        if len(cat_data) > 0:
            recent_trend = cat_data.tail(10).mean()
            if recent_trend > 15:
                trend_analysis[category] = "Strong Growth"
            elif recent_trend > 5:
                trend_analysis[category] = "Moderate Growth"
            elif recent_trend > -5:
                trend_analysis[category] = "Stable"
            else:
                trend_analysis[category] = "Declining"
        else:
            trend_analysis[category] = "Insufficient Data"
    
    insights['trend_classification'] = trend_analysis
    
    return insights
