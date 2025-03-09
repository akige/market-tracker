from flask import Flask, render_template, Response
import os
from datetime import datetime
import json
import requests
import ccxt
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)

# 要追踪的股票列表
STOCKS = ['MSTR', '^IXIC', 'NVDA', 'TSLA']

# 要追踪的加密货币列表
CRYPTO = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT', 'XRP/USDT', 'BNB/USDT', 'ADA/USDT', 'XLM/USDT']

# 配置请求会话
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

def get_stock_data(symbol):
    """从Yahoo Finance获取股票数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d'
        response = session.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result['meta']
            
            market_state = meta.get('marketState', 'CLOSED')
            current_price = meta.get('regularMarketPrice', 0)
            previous_close = meta.get('previousClose', current_price)
            
            regular_change = ((current_price - previous_close) / previous_close * 100) if previous_close > 0 else 0
            
            extended_price = 0
            extended_change = 0
            
            if market_state in ['PRE', 'PREPRE', 'POST', 'POSTPOST']:
                extended_price = meta.get('postMarketPrice' if 'POST' in market_state else 'preMarketPrice', 0)
                if extended_price > 0:
                    extended_change = ((extended_price - current_price) / current_price * 100)

            return {
                'symbol': symbol,
                'price': current_price,
                'change_percent': regular_change,
                'extended_hours_change': extended_change,
                'market_state': market_state,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'stock'
            }
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {str(e)}")
    return None

def get_crypto_data():
    """使用币安公共API获取加密货币数据"""
    all_data = []
    try:
        # 使用币安公共API
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 获取24小时价格统计
        response = session.get('https://api.binance.com/api/v3/ticker/24hr', headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error fetching crypto data: Status code {response.status_code}")
            return all_data

        all_tickers = response.json()
        ticker_dict = {item['symbol']: item for item in all_tickers}
        
        for pair in CRYPTO:
            symbol = pair.replace('/', '')  # 转换 BTC/USDT 为 BTCUSDT
            if symbol in ticker_dict:
                ticker = ticker_dict[symbol]
                try:
                    price = float(ticker['lastPrice'])
                    change = float(ticker['priceChangePercent'])
                    
                    all_data.append({
                        'symbol': pair.split('/')[0],
                        'price': price,
                        'change_percent': change,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'type': 'crypto'
                    })
                except (ValueError, KeyError) as e:
                    print(f"Error processing {symbol} data: {str(e)}")
                    continue
            else:
                print(f"Symbol {symbol} not found in Binance response")
    except Exception as e:
        print(f"Error in get_crypto_data: {str(e)}")
    return all_data

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """处理所有路由"""
    try:
        if path == '' or path == 'index.html':
            return render_template('index.html', stocks=STOCKS, crypto=[c.split('/')[0] for c in CRYPTO])
        elif path == 'api/market-data':
            all_data = []
            
            # 获取股票数据
            for symbol in STOCKS:
                stock_data = get_stock_data(symbol)
                if stock_data:
                    all_data.append(stock_data)
            
            # 获取加密货币数据
            crypto_data = get_crypto_data()
            if crypto_data:
                all_data.extend(crypto_data)
            
            return Response(
                json.dumps(all_data),
                mimetype='application/json'
            )
        else:
            return '', 404
    except Exception as e:
        print(f"Error in catch_all route: {str(e)}")
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000) 