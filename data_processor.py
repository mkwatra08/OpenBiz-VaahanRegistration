import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

class DataProcessor:
    """
    Processes raw vehicle registration data and calculates growth metrics
    """
    
    def __init__(self):
        pass
    
    def process_registration_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw registration data and add calculated fields
        
        Args:
            raw_data: Raw vehicle registration data
            
        Returns:
            pandas.DataFrame: Processed data with additional metrics
        """
        # Copy the dataframe to avoid modifying original
        data = raw_data.copy()
        
        # Ensure date column is datetime
        data['date'] = pd.to_datetime(data['date'])
        
        # Add time-based columns
        data['year'] = data['date'].dt.year
        data['month'] = data['date'].dt.to_period('M')
        data['quarter'] = data['date'].dt.to_period('Q')
        data['week'] = data['date'].dt.to_period('W')
        data['day_of_week'] = data['date'].dt.day_name()
        data['month_name'] = data['date'].dt.month_name()
        
        # Calculate rolling averages
        data = self._add_rolling_averages(data)
        
        # Calculate growth rates
        data = self._add_growth_rates(data)
        
        # Add market share calculations
        data = self._add_market_shares(data)
        
        # Add performance indicators
        data = self._add_performance_indicators(data)
        
        return data
    
    def _add_rolling_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add rolling average calculations"""
        
        # Sort by date for proper rolling calculations
        data = data.sort_values(['state', 'category', 'date'])
        
        # 7-day rolling average
        data['registrations_7d_avg'] = data.groupby(['state', 'category'])['registrations'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        
        # 30-day rolling average
        data['registrations_30d_avg'] = data.groupby(['state', 'category'])['registrations'].transform(
            lambda x: x.rolling(window=30, min_periods=1).mean()
        )
        
        return data
    
    def _add_growth_rates(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add year-over-year and quarter-over-quarter growth rates"""
        
        # Monthly aggregation for growth calculations
        monthly_data = data.groupby(['state', 'category', 'month'])['registrations'].sum().reset_index()
        
        # Year-over-year growth
        monthly_data['yoy_growth'] = monthly_data.groupby(['state', 'category'])['registrations'].pct_change(periods=12) * 100
        
        # Quarter-over-quarter growth (using 3-month periods)
        monthly_data['qoq_growth'] = monthly_data.groupby(['state', 'category'])['registrations'].pct_change(periods=3) * 100
        
        # Month-over-month growth
        monthly_data['mom_growth'] = monthly_data.groupby(['state', 'category'])['registrations'].pct_change() * 100
        
        # Merge growth rates back to main data
        data = data.merge(
            monthly_data[['state', 'category', 'month', 'yoy_growth', 'qoq_growth', 'mom_growth']],
            on=['state', 'category', 'month'],
            how='left'
        )
        
        return data
    
    def _add_market_shares(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add market share calculations"""
        
        # Calculate total registrations by date
        daily_totals = data.groupby('date')['registrations'].sum().reset_index()
        daily_totals.rename(columns={'registrations': 'total_daily_registrations'}, inplace=True)
        
        # Merge with main data
        data = data.merge(daily_totals, on='date')
        
        # Calculate market share by category
        data['category_market_share'] = (data['registrations'] / data['total_daily_registrations']) * 100
        
        # Calculate state market share
        data['state_market_share'] = data.groupby(['date', 'state'])['registrations'].transform('sum') / data['total_daily_registrations'] * 100
        
        return data
    
    def _add_performance_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add performance indicators and flags"""
        
        # Performance vs 30-day average
        data['performance_vs_30d'] = ((data['registrations'] - data['registrations_30d_avg']) / data['registrations_30d_avg']) * 100
        
        # Performance flags
        data['is_above_average'] = data['performance_vs_30d'] > 0
        data['is_high_growth'] = data['yoy_growth'] > 15  # Above 15% YoY growth
        data['is_declining'] = data['yoy_growth'] < -5   # Declining more than 5%
        
        # Volatility indicator (coefficient of variation for last 30 days)
        data['volatility_30d'] = data.groupby(['state', 'category'])['registrations'].transform(
            lambda x: x.rolling(window=30, min_periods=10).std() / x.rolling(window=30, min_periods=10).mean()
        )
        
        return data
    
    def calculate_growth_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate overall growth metrics for the dataset
        
        Args:
            data: Processed registration data
            
        Returns:
            Dict: Dictionary containing various growth metrics
        """
        metrics = {}
        
        # Overall growth rates
        current_year = data['year'].max()
        previous_year = current_year - 1
        
        current_year_data = data[data['year'] == current_year]
        previous_year_data = data[data['year'] == previous_year]
        
        if not previous_year_data.empty:
            current_total = current_year_data['registrations'].sum()
            previous_total = previous_year_data['registrations'].sum()
            
            metrics['total_yoy_growth'] = ((current_total - previous_total) / previous_total) * 100
        else:
            metrics['total_yoy_growth'] = 0
        
        # Category-wise growth
        category_growth = data.groupby('category')['yoy_growth'].mean().fillna(0).to_dict()
        metrics['category_yoy_growth'] = category_growth
        
        # State-wise growth
        state_growth = data.groupby('state')['yoy_growth'].mean().fillna(0).to_dict()
        metrics['state_yoy_growth'] = state_growth
        
        # Monthly trends
        monthly_totals = data.groupby('month')['registrations'].sum()
        if len(monthly_totals) > 1:
            monthly_growth = monthly_totals.pct_change().mean() * 100
            metrics['monthly_growth'] = monthly_growth
        else:
            metrics['monthly_growth'] = 0
        
        # Market concentration
        category_shares = data.groupby('category')['registrations'].sum()
        total_registrations = category_shares.sum()
        metrics['market_concentration'] = {
            cat: (share / total_registrations) * 100 
            for cat, share in category_shares.items()
        }
        
        # Growth consistency (coefficient of variation of monthly growth rates)
        monthly_growth_rates = monthly_totals.pct_change().dropna()
        if len(monthly_growth_rates) > 0:
            metrics['growth_consistency'] = monthly_growth_rates.std() / abs(monthly_growth_rates.mean()) if monthly_growth_rates.mean() != 0 else 0
        else:
            metrics['growth_consistency'] = 0
        
        # Top performing segments
        avg_growth_by_category = data.groupby('category')['yoy_growth'].mean().fillna(0)
        if len(avg_growth_by_category) > 0:
            metrics['top_growing_category'] = avg_growth_by_category.idxmax()
            metrics['top_growth_rate'] = avg_growth_by_category.max()
        else:
            metrics['top_growing_category'] = "N/A"
            metrics['top_growth_rate'] = 0
        
        # Volatility metrics
        avg_volatility = data['volatility_30d'].mean()
        metrics['average_volatility'] = avg_volatility if not pd.isna(avg_volatility) else 0
        
        return metrics
    
    def get_summary_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for the dataset
        
        Args:
            data: Processed registration data
            
        Returns:
            Dict: Dictionary containing summary statistics
        """
        summary = {}
        
        # Basic statistics
        summary['total_records'] = len(data)
        summary['date_range'] = {
            'start': data['date'].min().strftime('%Y-%m-%d'),
            'end': data['date'].max().strftime('%Y-%m-%d')
        }
        summary['total_registrations'] = data['registrations'].sum()
        summary['daily_average'] = data['registrations'].mean()
        summary['states_covered'] = data['state'].nunique()
        summary['categories_covered'] = data['category'].nunique()
        
        # Distribution statistics
        summary['registrations_distribution'] = {
            'mean': data['registrations'].mean(),
            'median': data['registrations'].median(),
            'std': data['registrations'].std(),
            'min': data['registrations'].min(),
            'max': data['registrations'].max()
        }
        
        return summary
