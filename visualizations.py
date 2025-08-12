import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class VehicleRegistrationVisualizer:
    """
    Creates interactive visualizations for vehicle registration data
    """
    
    def __init__(self):
        # Define consistent color palette
        self.color_palette = {
            '2W': '#1f77b4',
            '3W': '#ff7f0e', 
            '4W': '#2ca02c',
            'Commercial': '#d62728',
            'Others': '#9467bd'
        }
        
        # Chart styling
        self.chart_config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        }
    
    def create_timeline_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        Create timeline chart showing registration trends over time
        
        Args:
            data: Processed registration data
            
        Returns:
            plotly.graph_objects.Figure: Interactive timeline chart
        """
        # Aggregate data by date and category
        timeline_data = data.groupby(['date', 'category'])['registrations'].sum().reset_index()
        
        fig = px.line(
            timeline_data,
            x='date',
            y='registrations',
            color='category',
            title='Vehicle Registration Trends Over Time',
            labels={
                'registrations': 'Daily Registrations',
                'date': 'Date',
                'category': 'Vehicle Category'
            },
            color_discrete_map=self.color_palette
        )
        
        # Update layout
        fig.update_layout(
            height=500,
            showlegend=True,
            hovermode='x unified',
            xaxis_title="Date",
            yaxis_title="Number of Registrations",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Add range selector
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=30, label="30d", step="day", stepmode="backward"),
                    dict(count=90, label="3m", step="day", stepmode="backward"),
                    dict(count=180, label="6m", step="day", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        # Update traces for better visibility
        fig.update_traces(
            line=dict(width=2),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Registrations: %{y:,.0f}<br>' +
                         '<extra></extra>'
        )
        
        return fig
    
    def create_growth_chart(self, data: pd.DataFrame, growth_type: str = 'yoy') -> go.Figure:
        """
        Create growth rate chart (YoY or QoQ)
        
        Args:
            data: Processed registration data
            growth_type: 'yoy' for year-over-year or 'qoq' for quarter-over-quarter
            
        Returns:
            plotly.graph_objects.Figure: Growth rate chart
        """
        growth_col = f'{growth_type}_growth'
        
        # Aggregate growth data by category
        if growth_type == 'yoy':
            time_col = 'month'
            title = 'Year-over-Year Growth Rate by Category'
        else:
            time_col = 'quarter'
            title = 'Quarter-over-Quarter Growth Rate by Category'
        
        growth_data = data.groupby([time_col, 'category'])[growth_col].mean().reset_index()
        growth_data[time_col] = growth_data[time_col].astype(str)
        
        fig = px.bar(
            growth_data,
            x=time_col,
            y=growth_col,
            color='category',
            title=title,
            labels={
                growth_col: 'Growth Rate (%)',
                time_col: 'Time Period',
                'category': 'Vehicle Category'
            },
            color_discrete_map=self.color_palette,
            barmode='group'
        )
        
        # Add horizontal line at 0%
        fig.add_hline(
            y=0, 
            line_dash="dash", 
            line_color="black", 
            opacity=0.5,
            annotation_text="No Growth"
        )
        
        # Update layout
        fig.update_layout(
            height=400,
            showlegend=True,
            yaxis_title="Growth Rate (%)",
            xaxis_title="Time Period"
        )
        
        # Color bars based on positive/negative growth
        fig.update_traces(
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Period: %{x}<br>' +
                         'Growth Rate: %{y:.1f}%<br>' +
                         '<extra></extra>'
        )
        
        return fig
    
    def create_market_share_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        Create market share pie chart
        
        Args:
            data: Processed registration data
            
        Returns:
            plotly.graph_objects.Figure: Market share pie chart
        """
        # Calculate total registrations by category
        market_share_data = data.groupby('category')['registrations'].sum().reset_index()
        
        fig = px.pie(
            market_share_data,
            values='registrations',
            names='category',
            title='Market Share by Vehicle Category',
            color='category',
            color_discrete_map=self.color_palette
        )
        
        # Update traces for better formatting
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>' +
                         'Registrations: %{value:,.0f}<br>' +
                         'Market Share: %{percent}<br>' +
                         '<extra></extra>'
        )
        
        # Update layout
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.01
            )
        )
        
        return fig
    
    def create_geographic_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        Create state-wise performance chart
        
        Args:
            data: Processed registration data
            
        Returns:
            plotly.graph_objects.Figure: Geographic performance chart
        """
        # Aggregate data by state
        geo_data = data.groupby('state').agg({
            'registrations': 'sum',
            'yoy_growth': 'mean'
        }).reset_index()
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            specs=[[{"secondary_y": True}]],
            subplot_titles=["State-wise Registration Volume and Growth Rate"]
        )
        
        # Add bar chart for registrations
        fig.add_trace(
            go.Bar(
                x=geo_data['state'],
                y=geo_data['registrations'],
                name='Total Registrations',
                marker_color='lightblue',
                yaxis='y'
            ),
            secondary_y=False
        )
        
        # Add line chart for growth rate
        fig.add_trace(
            go.Scatter(
                x=geo_data['state'],
                y=geo_data['yoy_growth'],
                mode='lines+markers',
                name='YoY Growth Rate (%)',
                line=dict(color='red', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ),
            secondary_y=True
        )
        
        # Update layout
        fig.update_xaxes(title_text="State", tickangle=45)
        fig.update_yaxes(title_text="Total Registrations", secondary_y=False)
        fig.update_yaxes(title_text="YoY Growth Rate (%)", secondary_y=True)
        
        fig.update_layout(
            height=500,
            title="State-wise Performance Analysis",
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def create_manufacturer_chart(self, data: pd.DataFrame) -> go.Figure:
        """
        Create top manufacturers performance chart
        
        Args:
            data: Processed registration data
            
        Returns:
            plotly.graph_objects.Figure: Manufacturer performance chart
        """
        # Get top 10 manufacturers by volume
        manu_data = data.groupby('manufacturer').agg({
            'registrations': 'sum',
            'yoy_growth': 'mean'
        }).reset_index()
        
        # Sort by registrations and take top 10
        manu_data = manu_data.sort_values('registrations', ascending=False).head(10)
        
        fig = px.scatter(
            manu_data,
            x='registrations',
            y='yoy_growth',
            size='registrations',
            color='yoy_growth',
            hover_name='manufacturer',
            title='Top Manufacturers: Volume vs Growth Rate',
            labels={
                'registrations': 'Total Registrations',
                'yoy_growth': 'YoY Growth Rate (%)',
                'manufacturer': 'Manufacturer'
            },
            color_continuous_scale='RdYlGn'
        )
        
        # Add quadrant lines
        avg_registrations = manu_data['registrations'].mean()
        avg_growth = manu_data['yoy_growth'].mean()
        
        fig.add_vline(
            x=avg_registrations, 
            line_dash="dash", 
            line_color="gray", 
            opacity=0.5
        )
        fig.add_hline(
            y=avg_growth, 
            line_dash="dash", 
            line_color="gray", 
            opacity=0.5
        )
        
        # Update layout
        fig.update_layout(
            height=500,
            showlegend=True,
            annotations=[
                dict(
                    x=avg_registrations * 1.2,
                    y=avg_growth * 1.2,
                    text="High Volume<br>High Growth",
                    showarrow=False,
                    font=dict(size=10, color="green")
                ),
                dict(
                    x=avg_registrations * 0.5,
                    y=avg_growth * 1.2,
                    text="Low Volume<br>High Growth",
                    showarrow=False,
                    font=dict(size=10, color="orange")
                ),
                dict(
                    x=avg_registrations * 1.2,
                    y=avg_growth * 0.5,
                    text="High Volume<br>Low Growth",
                    showarrow=False,
                    font=dict(size=10, color="blue")
                ),
                dict(
                    x=avg_registrations * 0.5,
                    y=avg_growth * 0.5,
                    text="Low Volume<br>Low Growth",
                    showarrow=False,
                    font=dict(size=10, color="red")
                )
            ]
        )
        
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' +
                         'Total Registrations: %{x:,.0f}<br>' +
                         'YoY Growth: %{y:.1f}%<br>' +
                         '<extra></extra>'
        )
        
        return fig
    
    def create_performance_heatmap(self, data: pd.DataFrame) -> go.Figure:
        """
        Create performance heatmap showing growth across categories and time
        
        Args:
            data: Processed registration data
            
        Returns:
            plotly.graph_objects.Figure: Performance heatmap
        """
        # Create monthly growth data
        heatmap_data = data.groupby(['month', 'category'])['yoy_growth'].mean().unstack(fill_value=0)
        
        fig = go.Figure(
            data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=[str(month) for month in heatmap_data.index],
                colorscale='RdYlGn',
                colorbar=dict(title="YoY Growth Rate (%)"),
                hovertemplate='Month: %{y}<br>' +
                             'Category: %{x}<br>' +
                             'Growth Rate: %{z:.1f}%<br>' +
                             '<extra></extra>'
            )
        )
        
        fig.update_layout(
            title='Growth Rate Heatmap: Category vs Time',
            xaxis_title='Vehicle Category',
            yaxis_title='Month',
            height=400
        )
        
        return fig
