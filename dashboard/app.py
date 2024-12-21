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
    page_icon="🛍️",
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
            hover_data=['product_category_name']
        )
        st.plotly_chart(fig, use_container_width=True)

def create_rfm_analysis(df):
    """Create RFM analysis visualizations."""
    rfm = calculate_rfm(df)
    
    col1, col2, col3 = st.columns(3)
    
    metrics = {
        'recency': ('Top 5 Most Recent Customers', 'ascending'),
        'frequency': ('Top 5 Most Frequent Customers', 'descending'),
        'monetary': ('Top 5 Highest Value Customers', 'descending')
    }
    
    for (metric, (title, order)), col in zip(metrics.items(), [col1, col2, col3]):
        with col:
            top_5 = rfm.nlargest(5, metric) if order == 'descending' else rfm.nsmallest(5, metric)
            fig = px.bar(
                top_5,
                y=metric,
                color=metric,
                color_continuous_scale=COLOR_PALETTE,
                title=title
            )
            st.plotly_chart(fig, use_container_width=True)

def create_payment_analysis(df):
    """Create payment method analysis."""
    col1, col2 = st.columns(2)
    
    with col1:
        payment_stats = df.groupby('payment_type').agg({
            'total_value': 'sum',
            'review_score': 'mean'
        })
        
        fig = px.pie(
            payment_stats,
            values='total_value',
            names=payment_stats.index,
            title='Transaction Value by Payment Method',
            color_discrete_sequence=COLOR_PALETTE
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        installment_stats = df.groupby('payment_installments').agg({
            'total_value': 'mean',
            'review_score': 'mean'
        }).reset_index()
        
        fig = px.scatter(
            installment_stats,
            x='payment_installments',
            y='review_score',
            size='total_value',
            color='total_value',
            color_continuous_scale=COLOR_PALETTE,
            title='Review Scores by Payment Installments'
        )
        st.plotly_chart(fig, use_container_width=True)
def create_price_distribution(df):
    """Visualize product price distribution."""
    st.subheader("Distribusi Harga Produk")
    plt.figure(figsize=(10, 6))
    sns.histplot(df['price'], bins=50, kde=True, color="#FF7F50")
    plt.title('Distribusi Harga Produk', fontsize=16)
    plt.xlabel('Harga (BRL)')
    plt.ylabel('Frekuensi')
    st.pyplot(plt)

def create_payment_distribution(df):
    """Visualize payment method distribution."""
    st.subheader("Distribusi Metode Pembayaran")
    plt.figure(figsize=(8, 5))
    sns.countplot(data=df, y='payment_type', order=df['payment_type'].value_counts().index, palette="Oranges")
    plt.title('Distribusi Metode Pembayaran', fontsize=16)
    plt.xlabel('Jumlah')
    plt.ylabel('Metode Pembayaran')
    st.pyplot(plt)

def create_avg_delivery_time(df):
    """Visualize average delivery time by product category."""
    st.subheader("Rata-rata Waktu Pengiriman per Kategori Produk (Top 10)")
    df_last_year = df[df['order_purchase_timestamp'] >= df['order_purchase_timestamp'].max() - pd.DateOffset(years=1)]
    avg_delivery_time = df_last_year.groupby('product_category_name')['delivery_time'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=avg_delivery_time.values, y=avg_delivery_time.index, palette="Oranges_r")
    plt.title('Rata-rata Waktu Pengiriman per Kategori Produk (Top 10)', fontsize=16)
    plt.xlabel('Rata-rata Waktu Pengiriman (Hari)')
    plt.ylabel('Kategori Produk')
    st.pyplot(plt)

def create_payment_total(df):
    """Visualize total transactions by payment method."""
    st.subheader("Total Transaksi per Metode Pembayaran (6 Bulan Terakhir)")
    df_last_six_months = df[df['order_purchase_timestamp'] >= df['order_purchase_timestamp'].max() - pd.DateOffset(months=6)]
    payment_total = df_last_six_months.groupby('payment_type')['payment_value'].sum().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=payment_total.values, y=payment_total.index, palette="Oranges_r")
    plt.title('Total Transaksi per Metode Pembayaran (6 Bulan Terakhir)', fontsize=16)
    plt.xlabel('Total Transaksi (BRL)')
    plt.ylabel('Metode Pembayaran')
    st.pyplot(plt)

def create_payment_review(df):
    """Visualize average review scores by payment method."""
    st.subheader("Rata-rata Skor Ulasan per Metode Pembayaran (6 Bulan Terakhir)")
    df_last_six_months = df[df['order_purchase_timestamp'] >= df['order_purchase_timestamp'].max() - pd.DateOffset(months=6)]
    payment_review = df_last_six_months.groupby('payment_type')['review_score'].mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=payment_review.values, y=payment_review.index, palette="Oranges")
    plt.title('Rata-rata Skor Ulasan per Metode Pembayaran (6 Bulan Terakhir)', fontsize=16)
    plt.xlabel('Rata-rata Skor Ulasan')
    plt.ylabel('Metode Pembayaran')
    st.pyplot(plt)

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
    
    st.subheader("Visualisasi Pendahuluan")
    create_price_distribution(filtered_df)
    create_payment_distribution(filtered_df)
    
    st.subheader('Jawaban Pertanyaan Bisnis')
    create_avg_delivery_time(filtered_df)
    create_payment_total(filtered_df)
    create_payment_review(filtered_df)
    
    st.subheader('Time Series Analysis')
    create_time_series(filtered_df)
    
    st.subheader('Customer Demographics')
    create_customer_demographics(filtered_df)
    
    st.subheader('Product Insights')
    create_product_insights(filtered_df)
    
    st.subheader('RFM Analysis')
    create_rfm_analysis(filtered_df)
    
    st.subheader('Payment Method Analysis')
    create_payment_analysis(filtered_df)

if __name__ == "__main__":
    main()
