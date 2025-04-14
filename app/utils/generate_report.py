import matplotlib.pyplot as plt
import pandas as pd
import io
from datetime import datetime, timedelta

async def generate_user_growth_chart(user_growth_data):
    """Generate a chart showing user growth over time"""
    if not user_growth_data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(user_growth_data, columns=['date', 'count'])
    
    # Create figure
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['count'], marker='o', linestyle='-', color='blue')
    plt.title('User Growth Over Time')
    plt.xlabel('Date')
    plt.ylabel('New Users')
    plt.grid(True)
    plt.tight_layout()
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

async def generate_activity_heatmap(hour_activity_data):
    """Generate a heatmap showing activity by hour of day"""
    if not hour_activity_data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(hour_activity_data, columns=['hour', 'count'])
    
    # Create a 24-hour range
    all_hours = pd.DataFrame({'hour': range(24)})
    df = pd.merge(all_hours, df, on='hour', how='left').fillna(0)
    
    # Create figure
    plt.figure(figsize=(12, 6))
    plt.bar(df['hour'], df['count'], color='purple')
    plt.title('Activity by Hour of Day')
    plt.xlabel('Hour')
    plt.ylabel('Number of Commands')
    plt.xticks(range(24))
    plt.grid(True, axis='y')
    plt.tight_layout()
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf

async def generate_monthly_report(stats):
    """Generate a comprehensive monthly report with charts"""
    # This would create a more detailed report with multiple charts
    # For demonstration purposes, we'll just create a simple chart
    
    # Create a figure with multiple subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # User growth chart
    if stats['user_growth']:
        df_users = pd.DataFrame(stats['user_growth'], columns=['date', 'count'])
        ax1.plot(df_users['date'], df_users['count'], marker='o', linestyle='-', color='blue')
        ax1.set_title('User Growth Over Time')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('New Users')
        ax1.grid(True)
    
    # Activity by hour chart
    if stats['hour_activity']:
        df_hours = pd.DataFrame(stats['hour_activity'], columns=['hour', 'count'])
        all_hours = pd.DataFrame({'hour': range(24)})
        df_hours = pd.merge(all_hours, df_hours, on='hour', how='left').fillna(0)
        
        ax2.bar(df_hours['hour'], df_hours['count'], color='purple')
        ax2.set_title('Activity by Hour of Day')
        ax2.set_xlabel('Hour')
        ax2.set_ylabel('Number of Commands')
        ax2.set_xticks(range(24))
        ax2.grid(True, axis='y')
    
    plt.tight_layout()
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    return buf
