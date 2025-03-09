from flask import Flask, render_template, Response
import os
from datetime import datetime
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import logging
import ccxt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 要追踪的股票列表
STOCKS = ['MSTR', '^IXIC', 'NVDA', 'TSLA']

# 要追踪的加密货币列表
CRYPTO = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOGE/USDT', 'XRP/USDT', 'BNB/USDT', 'ADA/USDT', 'XLM/USDT']

# 初始化 CCXT 交易所实例
def init_exchange():
    try:
        exchange = ccxt.kucoin({
            'enableRateLimit': True,
            'timeout': 10000,
        })
        return exchange
    except Exception as e:
        logger.error(f"Error initializing exchange: {str(e)}")
        return None

# 配置请求会话
def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def get_stock_data(symbol, session):
    """从Yahoo Finance获取股票数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d'
        response = session.get(url, headers=headers, timeout=5)
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
        logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
    return None

def get_crypto_data():
    """使用CCXT获取加密货币数据"""
    all_data = []
    exchange = init_exchange()
    
    if not exchange:
        logger.error("Failed to initialize exchange")
        return all_data
        
    try:
        # 获取所有市场数据
        markets = {}
        try:
            markets = exchange.fetch_tickers()
            logger.info(f"Successfully fetched {len(markets)} markets from exchange")
        except Exception as e:
            logger.error(f"Error fetching markets: {str(e)}")
            return all_data

        # 处理每个加密货币
        for pair in CRYPTO:
            try:
                if pair in markets:
                    ticker = markets[pair]
                    price = ticker['last']
                    change = ticker['percentage']
                    
                    if price and change is not None:
                        all_data.append({
                            'symbol': pair.split('/')[0],
                            'price': price,
                            'change_percent': change,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'type': 'crypto'
                        })
                        logger.info(f"Successfully added {pair} data: price={price}, change={change}")
                    else:
                        logger.warning(f"Invalid price or change data for {pair}")
                else:
                    logger.warning(f"Symbol {pair} not found in exchange response")
            except Exception as e:
                logger.error(f"Error processing {pair}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error in get_crypto_data: {str(e)}")
    
    logger.info(f"Returning {len(all_data)} crypto entries")
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
            session = create_session()
            for symbol in STOCKS:
                stock_data = get_stock_data(symbol, session)
                if stock_data:
                    all_data.append(stock_data)
                time.sleep(0.1)  # 添加小延迟以避免触发频率限制
            
            # 获取加密货币数据
            crypto_data = get_crypto_data()
            if crypto_data:
                all_data.extend(crypto_data)
            
            logger.info(f"Returning total {len(all_data)} entries")
            return Response(
                json.dumps(all_data),
                mimetype='application/json'
            )
        else:
            return '', 404
    except Exception as e:
        logger.error(f"Error in catch_all route: {str(e)}")
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000) 