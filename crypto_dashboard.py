import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(page_title="Crypto Dashboard", layout="wide")

def get_crypto_data(crypto_id):
    """Fetch data from CoinGecko API"""
    try:
        # Get current price data
        price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true&include_market_cap=true"
        price_data = requests.get(price_url).json()
        
        # Get historical data (7 days)
        history_url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=7&interval=hourly"
        history_data = requests.get(history_url).json()
        
        return price_data, history_data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None, None

def main():
    st.title("📊 Crypto Trading Dashboard")
    
    # Sidebar
    st.sidebar.header("Settings")
    update_interval = st.sidebar.slider("Update interval (seconds)", 30, 300, 60)
    
    # Main content
    col1, col2 = st.columns(2)
    
    # Track these cryptocurrencies
    cryptos = {
        "bitcoin": "Bitcoin (BTC)",
        "hedera-hashgraph": "Hedera (HBAR)"
    }
    
    while True:
        for crypto_id, crypto_name in cryptos.items():
            price_data, history_data = get_crypto_data(crypto_id)
            
            if price_data and history_data:
                data = price_data[crypto_id]
                
                # Create metrics
                with col1:
                    st.subheader(f"{crypto_name} Metrics")
                    metrics_cols = st.columns(3)
                    
                    with metrics_cols[0]:
                        st.metric(
                            "Price (USD)",
                            f"${data['usd']:,.2f}",
                            f"{data['usd_24h_change']:.2f}%"
                        )
                    
                    with metrics_cols[1]:
                        st.metric(
                            "24h Volume (USD)",
                            f"${data['usd_24h_vol']:,.0f}"
                        )
                    
                    with metrics_cols[2]:
                        st.metric(
                            "Market Cap (USD)",
                            f"${data['usd_market_cap']:,.0f}"
                        )
                
                # Create price chart
                with col2:
                    st.subheader(f"{crypto_name} 7-Day Price Chart")
                    df = pd.DataFrame(history_data['prices'], columns=['timestamp', 'price'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df['timestamp'],
                        y=df['price'],
                        mode='lines',
                        name='Price'
                    ))
                    
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        height=400,
                        margin=dict(l=0, r=0, t=0, b=0)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        # Volatile Currencies Section
        st.subheader("🔥 High Volatility Opportunities")
        vol_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=100&sparkline=false"
        vol_data = requests.get(vol_url).json()
        
        # Filter for high volatility coins
        volatile_coins = [
            coin for coin in vol_data 
            if coin['price_change_percentage_24h'] is not None 
            and abs(coin['price_change_percentage_24h']) > 10
            and coin['total_volume'] > 10000000
        ]
        
        if volatile_coins:
            vol_df = pd.DataFrame(volatile_coins)
            vol_df = vol_df[['symbol', 'current_price', 'price_change_percentage_24h', 'total_volume', 'market_cap']]
            vol_df.columns = ['Symbol', 'Price (USD)', '24h Change %', 'Volume (USD)', 'Market Cap (USD)']
            st.dataframe(vol_df.head(5), use_container_width=True)
        
        # Update timestamp
        st.sidebar.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Wait for next update
        time.sleep(update_interval)
        st.experimental_rerun()

if __name__ == "__main__":
    main() 