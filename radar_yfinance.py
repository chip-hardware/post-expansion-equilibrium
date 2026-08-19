import pandas as pd
import os
import yfinance as yf
from datetime import timedelta

# ============================================================
# 1. DIRECTORY & ASSET CONFIGURATION
# ============================================================
data_folder = 'yf_data'

if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    print(f"Created directory: '{data_folder}'")

# Map your MT4 assets to Yahoo Finance tickers
# Format: 'YOUR_NAME': 'YAHOO_TICKER'
asset_map = {
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    'USDCHF': 'USDCHF=X',
    'USDCAD': 'USDCAD=X',
    'USDJPY': 'USDJPY=X',
    'AUDUSD': 'AUDUSD=X',
    'GBPJPY': 'GBPJPY=X',
    'GOLD': 'GC=F',       # Gold Futures
    'SILVER': 'SI=F'      # Silver Futures
}

print(f"Starting automatic sync with Yahoo Finance for {len(asset_map)} assets...")

# ============================================================
# 2. AUTOMATIC DATA DOWNLOAD & H4 RESAMPLING
# ============================================================
for asset_name, ticker in asset_map.items():
    print(f"Fetching 1h data for {asset_name} ({ticker})...")
    
    # Download 1-hour data for the last 3 months (Yahoo limitation: max 730 days for 1h)
    raw_data = yf.download(ticker, period="3mo", interval="1h", progress=False)
    
    if raw_data.empty:
        print(f"  ⚠️ Warning: No data received for {ticker}")
        continue
        
    # Reset index to bring Datetime out as a column
    raw_data = raw_data.reset_index()
    
    # Ensure standard column names
    raw_data.columns = [c[0] if isinstance(c, tuple) else c for c in raw_data.columns]
    raw_data = raw_data.rename(columns={'Datetime': 'Timestamp'})
    
    # Set Datetime as index for reshaping
    raw_data.set_index('Timestamp', inplace=True)
    
    # Aggregate 1h bars into clean 4h bars (Open, High, Low, Close, Volume)
    h4_data = raw_data.resample('4h').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    # Break Datetime back into MT4 style 'Date' and 'Time' columns
    h4_data = h4_data.reset_index()
    h4_data['Date'] = h4_data['Timestamp'].dt.strftime('%Y.%m.%d')
    h4_data['Time'] = h4_data['Timestamp'].dt.strftime('%H:%M')
    
    # Reorder columns to closely match your expected structure
    final_df = h4_data[['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    # Save directly to yf_data folder
    output_path = os.path.join(data_folder, f"{asset_name}240.csv")
    final_df.to_csv(output_path, index=False, header=False)
    print(f"  ✅ Saved and converted to H4: {output_path}")

# ============================================================
# 3. GLOBAL SCANNING LOOP (INTEGRATED RADAR)
# ============================================================
print("\n" + "="*60)
print("🚀 YF-RADAR SCANNING STARTED (LAST 3 MONTHS HISTORY)")
print("="*60)

global_anomalies_count = 0
csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

for file_name in csv_files:
    asset_name = file_name.replace('240.csv', '').upper()
    file_path = os.path.join(data_folder, file_name)
    
    columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df_fresh = pd.read_csv(file_path, names=columns, header=None)
    
    if len(df_fresh) < 25:
        continue

    # Dynamically adjust point/pip multipliers based on asset price scale
    sample_price = df_fresh.loc[0, 'Close']
    if sample_price > 1000:     # E.g., Gold (around 2000-4000)
        pip_multiplier = 100
        pip_label = "points/dollars"
    elif sample_price > 50:     # E.g., JPY Pairs
        pip_multiplier = 1000
        pip_label = "pips"
    else:                       # Standard FX Majors (EURUSD, USDCHF etc.)
        pip_multiplier = 100000
        pip_label = "pips"

    # Calculate individual candle bodies and dynamic rolling average
    df_fresh['Body_Points'] = abs(df_fresh['Open'] - df_fresh['Close']) * pip_multiplier
    df_fresh['Average_Body'] = df_fresh['Body_Points'].rolling(window=20, min_periods=1).mean()
    
    # Anomaly threshold: expansion candle must be 3.5x larger than local average
    anomaly_threshold_multiplier = 3.5
    asset_anomalies = 0

    # Scan dataframe for anomalies
    for i in range(len(df_fresh)):
        if i < 5: 
            continue
            
        current_body = df_fresh.loc[i, 'Body_Points']
        avg_body = df_fresh.loc[i-1, 'Average_Body']
        
        if current_body >= (avg_body * anomaly_threshold_multiplier):
            asset_anomalies += 1
            global_anomalies_count += 1
            
            open_p = df_fresh.loc[i, 'Open']
            close_p = df_fresh.loc[i, 'Close']
            
            is_buy = close_p > open_p
            direction = "🚀 BULLISH EXPANSION" if is_buy else "🩸 BEARISH EXPANSION"
            
            impulse_high = max(open_p, close_p)
            impulse_low = min(open_p, close_p)
            equilibrium_50 = (impulse_high + impulse_low) / 2.0
            
            # Format outputs for consistent console reporting
            display_size = current_body / 10 if pip_multiplier == 100000 else current_body
            display_avg = avg_body / 10 if pip_multiplier == 100000 else avg_body
            
            print(f"\n[{asset_name}] Anomaly #{asset_anomalies} found on {df_fresh.loc[i, 'Date']} at {df_fresh.loc[i, 'Time']}")
            print(f"  • Vector Type : {direction}")
            print(f"  • Size        : {display_size:.1f} {pip_label} (Local average: {display_avg:.1f})")
            print(f"  • Body Range  : {impulse_low:.5f} — {impulse_high:.5f}")
            print(f"  • 50% Pivot   : {equilibrium_50:.5f}")

print("\n" + "="*60)
print(f"🌐 GLOBAL SCAN COMPLETE. Total anomalies detected across Yahoo Finance data: {global_anomalies_count}")
print("="*60)
