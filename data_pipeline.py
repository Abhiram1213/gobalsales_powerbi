"""
===============================================================================
Global Superstore - Dimensional Modeling & ETL Data Pipeline
===============================================================================
Author: Senior BI Data Engineer & Analytics Specialist
Description:
    Transforms raw 'Global Superstore - Orders.csv' transactional data into an
    optimized 5-table Star Schema:
      1. Dim_Date        - Complete date dimension with fiscal calendar & hierarchies
      2. Dim_Customer    - Customer dimension with RFM segmentation metrics
      3. Dim_Product     - Product catalog dimension with Category/Sub-Category tiers
      4. Dim_Geography   - Normalized geographical hierarchy (Country, State, City, Region, Market)
      5. Fact_Orders     - Core order line transactional facts with calculated metrics

    Also generates clean aggregations and JSON datasets for interactive visualization.
===============================================================================
"""

import os
import json
import pandas as pd
import numpy as np

def run_etl(source_csv_path='Global Superstore - Orders.csv', output_dir='data_model'):
    print(f"[*] Starting ETL Pipeline using source: {source_csv_path}")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load Raw Data
    df = pd.read_csv(source_csv_path, encoding='latin1')
    print(f"[+] Loaded {len(df):,} raw order lines across {df.shape[1]} columns.")
    
    # Clean column names & parse dates
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    
    # Fill Postal Code nulls with 'Unknown' (typical for international markets)
    df['Postal Code'] = df['Postal Code'].fillna('Unknown').astype(str)
    
    # Calculate order-level metrics
    df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days
    df['Unit Price'] = df['Sales'] / df['Quantity']
    df['Cost'] = df['Sales'] - df['Profit']
    df['Profit Margin %'] = (df['Profit'] / df['Sales']) * 100
    df['Is Loss Making'] = df['Profit'] < 0
    
    # -------------------------------------------------------------------------
    # 2. Build Dimension Tables (Star Schema)
    # -------------------------------------------------------------------------
    
    # A. Dim_Date
    print("[*] Generating Dim_Date...")
    min_date = df['Order Date'].min()
    max_date = max(df['Order Date'].max(), df['Ship Date'].max())
    date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    
    dim_date = pd.DataFrame({'Date': date_range})
    dim_date['DateKey'] = dim_date['Date'].dt.strftime('%Y%m%d').astype(int)
    dim_date['Year'] = dim_date['Date'].dt.year
    dim_date['Quarter'] = 'Q' + dim_date['Date'].dt.quarter.astype(str)
    dim_date['Year_Quarter'] = dim_date['Year'].astype(str) + '-' + dim_date['Quarter']
    dim_date['Month'] = dim_date['Date'].dt.month
    dim_date['Month_Name'] = dim_date['Date'].dt.strftime('%B')
    dim_date['Month_Short'] = dim_date['Date'].dt.strftime('%b')
    dim_date['Year_Month'] = dim_date['Date'].dt.strftime('%Y-%m')
    dim_date['Day'] = dim_date['Date'].dt.day
    dim_date['Day_Of_Week'] = dim_date['Date'].dt.day_name()
    dim_date['Is_Weekend'] = dim_date['Date'].dt.dayofweek.isin([5, 6]).astype(int)
    dim_date.to_csv(os.path.join(output_dir, 'Dim_Date.csv'), index=False)
    print(f"    -> Dim_Date created with {len(dim_date):,} date records.")
    
    # B. Dim_Customer
    print("[*] Generating Dim_Customer with RFM profiling...")
    snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)
    
    customer_agg = df.groupby('Customer ID').agg(
        Customer_Name=('Customer Name', 'first'),
        Segment=('Segment', 'first'),
        Total_Orders=('Order ID', 'nunique'),
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Profit', 'sum'),
        First_Order_Date=('Order Date', 'min'),
        Last_Order_Date=('Order Date', 'max')
    ).reset_index()
    
    customer_agg['Recency_Days'] = (snapshot_date - customer_agg['Last_Order_Date']).dt.days
    customer_agg['Profit_Margin_%'] = (customer_agg['Total_Profit'] / customer_agg['Total_Sales']) * 100
    
    # Customer Value Tier
    customer_agg['Customer_Tier'] = pd.qcut(
        customer_agg['Total_Sales'], 
        q=4, 
        labels=['Bronze', 'Silver', 'Gold', 'Platinum']
    )
    customer_agg.to_csv(os.path.join(output_dir, 'Dim_Customer.csv'), index=False)
    print(f"    -> Dim_Customer created with {len(customer_agg):,} unique customer profiles.")
    
    # C. Dim_Product
    print("[*] Generating Dim_Product...")
    dim_product = df.groupby('Product ID').agg(
        Product_Name=('Product Name', 'first'),
        Category=('Category', 'first'),
        Sub_Category=('Sub-Category', 'first'),
        Avg_Unit_Price=('Unit Price', 'mean'),
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Profit', 'sum')
    ).reset_index()
    dim_product['Profitability_Status'] = np.where(dim_product['Total_Profit'] >= 0, 'Profitable', 'Loss-Making')
    dim_product.to_csv(os.path.join(output_dir, 'Dim_Product.csv'), index=False)
    print(f"    -> Dim_Product created with {len(dim_product):,} unique products.")
    
    # D. Dim_Geography
    print("[*] Generating Dim_Geography...")
    dim_geo = df[['Country', 'State', 'City', 'Region', 'Market']].drop_duplicates().reset_index(drop=True)
    dim_geo['GeographyKey'] = dim_geo.index + 1
    dim_geo.to_csv(os.path.join(output_dir, 'Dim_Geography.csv'), index=False)
    print(f"    -> Dim_Geography created with {len(dim_geo):,} unique location hierarchies.")
    
    # E. Fact_Orders
    print("[*] Building Fact_Orders with surrogate keys...")
    df_merged = df.merge(dim_geo, on=['Country', 'State', 'City', 'Region', 'Market'], how='left')
    df_merged['OrderDateKey'] = df_merged['Order Date'].dt.strftime('%Y%m%d').astype(int)
    df_merged['ShipDateKey'] = df_merged['Ship Date'].dt.strftime('%Y%m%d').astype(int)
    
    fact_orders = df_merged[[
        'Row ID', 'Order ID', 'OrderDateKey', 'ShipDateKey', 'Ship Mode', 
        'Customer ID', 'GeographyKey', 'Product ID', 'Order Priority',
        'Sales', 'Quantity', 'Discount', 'Profit', 'Shipping Cost',
        'Shipping Days', 'Cost', 'Unit Price', 'Is Loss Making'
    ]]
    fact_orders.to_csv(os.path.join(output_dir, 'Fact_Orders.csv'), index=False)
    print(f"    -> Fact_Orders created with {len(fact_orders):,} facts.")
    
    # -------------------------------------------------------------------------
    # 3. Generate Analytical Summary JSON for Web App & Visualizations
    # -------------------------------------------------------------------------
    print("[*] Generating aggregated summary payload for interactive dashboard...")
    
    # Monthly Trends
    df['YearMonth'] = df['Order Date'].dt.strftime('%Y-%m')
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    
    monthly = df.groupby(['Year', 'Month', 'YearMonth']).agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Order ID', 'nunique'),
        Quantity=('Quantity', 'sum')
    ).reset_index().sort_values(by=['Year', 'Month'])
    
    # Market Summary
    market_summary = df.groupby('Market').agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Order ID', 'nunique'),
        Avg_Shipping_Cost=('Shipping Cost', 'mean')
    ).reset_index().sort_values(by='Sales', ascending=False)
    market_summary['Margin_Pct'] = (market_summary['Profit'] / market_summary['Sales']) * 100
    
    # Category & Sub-Category
    cat_summary = df.groupby(['Category', 'Sub-Category']).agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Avg_Discount=('Discount', 'mean'),
        Quantity=('Quantity', 'sum')
    ).reset_index().sort_values(by=['Category', 'Sales'], ascending=[True, False])
    cat_summary['Margin_Pct'] = (cat_summary['Profit'] / cat_summary['Sales']) * 100
    
    # Country Performance (Top 10 vs Bottom 10)
    country_summary = df.groupby('Country').agg(
        Market=('Market', 'first'),
        Region=('Region', 'first'),
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Order ID', 'nunique'),
        Avg_Discount=('Discount', 'mean')
    ).reset_index()
    country_summary['Margin_Pct'] = (country_summary['Profit'] / country_summary['Sales']) * 100
    
    top_10_countries = country_summary.sort_values(by='Profit', ascending=False).head(10).to_dict(orient='records')
    bottom_10_countries = country_summary.sort_values(by='Profit', ascending=True).head(10).to_dict(orient='records')
    
    # Ship Mode Performance
    ship_summary = df.groupby('Ship Mode').agg(
        Orders=('Order ID', 'nunique'),
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Avg_Cost=('Shipping Cost', 'mean'),
        Avg_Days=('Shipping Days', 'mean')
    ).reset_index().sort_values(by='Orders', ascending=False)
    
    # Segment Performance
    seg_summary = df.groupby('Segment').agg(
        Orders=('Order ID', 'nunique'),
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Avg_Discount=('Discount', 'mean')
    ).reset_index().sort_values(by='Sales', ascending=False)
    seg_summary['Margin_Pct'] = (seg_summary['Profit'] / seg_summary['Sales']) * 100
    
    # Detailed Order Records for in-browser multi-dimensional filtering
    cube = df.groupby(['Year', 'Market', 'Category', 'Sub-Category', 'Segment', 'Country']).agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Quantity=('Quantity', 'sum'),
        Shipping_Cost=('Shipping Cost', 'sum'),
        Orders=('Order ID', 'nunique'),
        Discount_Sum=('Discount', 'sum'),
        Row_Count=('Row ID', 'count')
    ).reset_index()
    
    dashboard_payload = {
        "kpis": {
            "total_sales": float(df['Sales'].sum()),
            "total_profit": float(df['Profit'].sum()),
            "profit_margin_pct": float((df['Profit'].sum() / df['Sales'].sum()) * 100),
            "total_orders": int(df['Order ID'].nunique()),
            "total_customers": int(df['Customer ID'].nunique()),
            "total_quantity": int(df['Quantity'].sum()),
            "avg_order_value": float(df['Sales'].sum() / df['Order ID'].nunique()),
            "total_shipping_cost": float(df['Shipping Cost'].sum()),
            "avg_shipping_days": float(df['Shipping Days'].mean()),
            "avg_discount_pct": float(df['Discount'].mean() * 100),
            "loss_making_orders": int((df['Profit'] < 0).sum()),
            "loss_amount": float(abs(df[df['Profit'] < 0]['Profit'].sum()))
        },
        "monthly_trends": monthly.to_dict(orient='records'),
        "market_summary": market_summary.to_dict(orient='records'),
        "category_summary": cat_summary.to_dict(orient='records'),
        "top_10_countries": top_10_countries,
        "bottom_10_countries": bottom_10_countries,
        "ship_mode_summary": ship_summary.to_dict(orient='records'),
        "segment_summary": seg_summary.to_dict(orient='records'),
        "cube": cube.to_dict(orient='records')
    }
    
    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_payload, f, indent=2)
    print("[+] Saved dashboard_data.json successfully.")
    
    print("\n=======================================================")
    print("ETL Pipeline completed successfully! Star schema created.")
    print("=======================================================")

if __name__ == '__main__':
    run_etl()
