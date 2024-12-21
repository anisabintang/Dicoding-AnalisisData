import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
import os

# Set page config
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Custom color palette for an appealing orange-copper tone
COLOR_PALETTE = ["#FF7F50", "#FF4500", "#CD853F", "#D2691E", "#8B4513"]
sns.set_palette(COLOR_PALETTE)  # Set default palette for seaborn


def load_data(file_path='data/cleaned_data.csv'):
    """
    Load and preprocess the dataset.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist. Please check the file path.")

    # Load the dataset
    df = pd.read_csv(file_path)
    
    # Convert date columns to datetime, ensuring the columns exist
    date_columns = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Calculate additional metrics
    if 'price' in df.columns and 'freight_value' in df.columns:
        df['total_value'] = df['price'] + df['freight_value']
    else:
        raise KeyError("The required columns 'price' and 'freight_value' are missing from the dataset.")

    # Add delivery time calculation
    if 'order_delivered_customer_date' in df.columns and 'order_purchase_timestamp' in df.columns:
        df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    
    return df


def calculate_rfm(df):
    """Calculate RFM metrics."""
    max_date = df['order_purchase_timestamp'].max()
    rfm = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (max_date - x.max()).days,  # Recency
        'order_id': 'count',  # Frequency
        'total_value': 'sum'  # Monetary
    }).rename(columns={
        'order_purchase_timestamp': 'recency',
        'order_id': 'frequency',
        'total_value': 'monetary'
    })
    return rfm


def create_overview_metrics(df):
    """Create overview metrics section."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Orders", f"{df['order_id'].nunique():,}")
    with col2:
        st.metric("Total Revenue", f"${df['total_value'].sum():,.2f}")
    with col3:
        st.metric("Avg Order Value", f"${df['total_value'].mean():,.2f}")
    with col4:
        st.metric("Avg Delivery Time", f"{df['delivery_time'].mean():.1f} days")


def create_time_series(df):
    """Create time series analysis."""
    daily_orders = df.groupby(df['order_purchase_timestamp'].dt.date).agg({
        'order_id': 'nunique',
        'total_value': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_orders['order_purchase_timestamp'],
        y=daily_orders['order_id'],
        name='Orders',
        line=dict(color=COLOR_PALETTE[0])
    ))
    fig.add_trace(go.Scatter(
        x=daily_orders['order_purchase_timestamp'],
        y=daily_orders['total_value'],
        name='Revenue',
        yaxis='y2',
        line=dict(color=COLOR_PALETTE[1])
    ))
    
    fig.update_layout(
        title='Daily Orders and Revenue Trends',
        yaxis=dict(title='Number of Orders'),
        yaxis2=dict(title='Revenue ($)', overlaying='y', side='right'),
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_customer_demographics(df):
    """Create customer demographics visualizations."""
    col1, col2 = st.columns(2)
    
    with col1:
        state_counts = df.groupby('customer_state')['customer_unique_id'].nunique().sort_values(ascending=True)
        fig = px.bar(
            state_counts,
            orientation='h',
            color=state_counts,
            color_continuous_scale=COLOR_PALETTE,
            title='Customer Distribution by State'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        city_counts = df.groupby('customer_city')['customer_unique_id'].nunique().nlargest(10)
        fig = px.bar(
            city_counts,
            color=city_counts,
            color_continuous_scale=COLOR_PALETTE,
            title='Top 10 Cities by Customer Count'
        )
        st.plotly_chart(fig, use_container_width=True)


def create_product_insights(df):
    """Create product category insights."""
    col1, col2 = st.columns(2)
    
    with col1:
        category_sales = df.groupby('product_category_name').agg({
            'total_value': 'sum',
            'delivery_time': 'mean',
            'review_score': 'mean'
        }).sort_values('total_value', ascending=False)
        
        fig = px.bar(
            category_sales,
            y='total_value',
            color='total_value',
            color_continuous_scale=COLOR_PALETTE,
            title='Sales by Product Category'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            category_sales,
            x='delivery_time',
            y='review_score',
            color='total_value',
            size='total_value',
            color_continuous_scale=COLOR_PALETTE,
            title='Delivery Time vs Review Score by Category',
            hover_data=['total_value']
        )
        st.plotly_chart(fig, use_container_width=True)


def main():
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.title('Filters')
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['order_purchase_timestamp'].min(), df['order_purchase_timestamp'].max()),
        min_value=df['order_purchase_timestamp'].min(),
        max_value=df['order_purchase_timestamp'].max()
    )
    
    # Product category filter
    categories = ['All'] + list(df['product_category_name'].unique())
    selected_category = st.sidebar.selectbox('Select Product Category', categories)
    
    # Payment type filter
    payment_types = ['All'] + list(df['payment_type'].unique())
    selected_payment = st.sidebar.selectbox('Select Payment Type', payment_types)
    
    # Apply filters
    mask = (df['order_purchase_timestamp'].dt.date >= date_range[0]) & \
           (df['order_purchase_timestamp'].dt.date <= date_range[1])
    
    if selected_category != 'All':
        mask = mask & (df['product_category_name'] == selected_category)
    if selected_payment != 'All':
        mask = mask & (df['payment_type'] == selected_payment)
    
    filtered_df = df[mask]
    
    # Main content
    st.title('E-commerce Analytics Dashboard')
    
    # Create sections
    st.subheader("Overview Metrics")
    create_overview_metrics(filtered_df)
    
    st.subheader('Customer Demographics')
    create_customer_demographics(filtered_df)
    
    st.subheader('Product Insights')
    create_product_insights(filtered_df)
    
    st.subheader('Time Series Analysis')
    create_time_series(filtered_df)


if __name__ == "__main__":
    main()
