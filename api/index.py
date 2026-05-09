from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import os
from datetime import datetime, timedelta
import secrets
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../static', static_url_path='/')
CORS(app)


# ========== TIMEZONE UTC+6 (Bangladesh Time) WITHOUT PYTZ ==========
def get_current_time():
    """Get current time in UTC+6 (Bangladesh Time)"""
    # Get UTC time and add 6 hours
    utc_now = datetime.utcnow()
    bangladesh_time = utc_now + timedelta(hours=6)
    return bangladesh_time


def format_time(dt):
    """Format datetime object to HH:MM string"""
    return dt.strftime('%H:%M')


# ========== ENVIRONMENT VARIABLES (HIDDEN FROM FRONTEND) ==========
API_BASE_URL = os.environ.get('API_BASE_URL')
VIP_PASSWORD = os.environ.get('VIP_PASSWORD')
SECRET_KEY = os.environ.get('SECRET_KEY')

active_sessions = {}

# ========== COMPLETE TRADING PAIRS (200+ assets) ==========
TRADING_PAIRS = [
    {"value": "EURUSD", "label": "EUR/USD", "group": "Forex (Real Market)"},
    {"value": "GBPUSD", "label": "GBP/USD", "group": "Forex (Real Market)"},
    {"value": "USDJPY", "label": "USD/JPY", "group": "Forex (Real Market)"},
    {"value": "USDCHF", "label": "USD/CHF", "group": "Forex (Real Market)"},
    {"value": "AUDUSD", "label": "AUD/USD", "group": "Forex (Real Market)"},
    {"value": "USDCAD", "label": "USD/CAD", "group": "Forex (Real Market)"},
    {"value": "EURGBP", "label": "EUR/GBP", "group": "Forex (Real Market)"},
    {"value": "EURJPY", "label": "EUR/JPY", "group": "Forex (Real Market)"},
    {"value": "GBPJPY", "label": "GBP/JPY", "group": "Forex (Real Market)"},
    {"value": "AUDJPY", "label": "AUD/JPY", "group": "Forex (Real Market)"},
    {"value": "EURCHF", "label": "EUR/CHF", "group": "Forex (Real Market)"},
    {"value": "GBPCHF", "label": "GBP/CHF", "group": "Forex (Real Market)"},
    {"value": "AUDCAD", "label": "AUD/CAD", "group": "Forex (Real Market)"},
    {"value": "AUDNZD", "label": "AUD/NZD", "group": "Forex (Real Market)"},
    {"value": "CADJPY", "label": "CAD/JPY", "group": "Forex (Real Market)"},
    {"value": "CHFJPY", "label": "CHF/JPY", "group": "Forex (Real Market)"},
    {"value": "EURAUD", "label": "EUR/AUD", "group": "Forex (Real Market)"},
    {"value": "EURCAD", "label": "EUR/CAD", "group": "Forex (Real Market)"},
    {"value": "GBPAUD", "label": "GBP/AUD", "group": "Forex (Real Market)"},
    {"value": "GBPCAD", "label": "GBP/CAD", "group": "Forex (Real Market)"},
    {"value": "EURUSD_otc", "label": "EUR/USD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "GBPUSD_otc", "label": "GBP/USD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDJPY_otc", "label": "USD/JPY (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDCHF_otc", "label": "USD/CHF (OTC)", "group": "Forex OTC Pairs"},
    {"value": "AUDUSD_otc", "label": "AUD/USD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDCAD_otc", "label": "USD/CAD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "EURGBP_otc", "label": "EUR/GBP (OTC)", "group": "Forex OTC Pairs"},
    {"value": "EURNZD_otc", "label": "EUR/NZD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "EURJPY_otc", "label": "EUR/JPY (OTC)", "group": "Forex OTC Pairs"},
    {"value": "GBPJPY_otc", "label": "GBP/JPY (OTC)", "group": "Forex OTC Pairs"},
    {"value": "CADCHF_otc", "label": "CAD/CHF (OTC)", "group": "Forex OTC Pairs"},
    {"value": "AUDJPY_otc", "label": "AUD/JPY (OTC)", "group": "Forex OTC Pairs"},
    {"value": "EURCHF_otc", "label": "EUR/CHF (OTC)", "group": "Forex OTC Pairs"},
    {"value": "EURSGD_otc", "label": "EUR/SGD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "GBPCHF_otc", "label": "GBP/CHF (OTC)", "group": "Forex OTC Pairs"},
    {"value": "NZDUSD_otc", "label": "NZD/USD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "NZDCHF_otc", "label": "NZD/CHF (OTC)", "group": "Forex OTC Pairs"},
    {"value": "NZDCAD_otc", "label": "NZD/CAD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "NZDJPY_otc", "label": "NZD/JPY (OTC)", "group": "Forex OTC Pairs"},
    {"value": "AUDCAD_otc", "label": "AUD/CAD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "AUDNZD_otc", "label": "AUD/NZD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "CADJPY_otc", "label": "CAD/JPY (OTC)", "group": "Forex OTC Pairs"},
    {"value": "CHFJPY_otc", "label": "CHF/JPY (OTC)", "group": "Forex OTC Pairs"},
    {"value": "EURAUD_otc", "label": "EUR/AUD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "EURCAD_otc", "label": "EUR/CAD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "GBPAUD_otc", "label": "GBP/AUD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "GBPNZD_otc", "label": "GBP/NZD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "GBPCAD_otc", "label": "GBP/CAD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDBDT_otc", "label": "USD/BDT (OTC)", "group": "Forex OTC Pairs"},
    {"value": "BRLUSD_otc", "label": "BRL/USD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDINR_otc", "label": "USD/INR (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDARS_otc", "label": "USD/ARS (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDPHP_otc", "label": "USD/PHP (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDPKR_otc", "label": "USD/PKR (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDMXN_otc", "label": "USD/MXN (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDCOP_otc", "label": "USD/COP (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDEGP_otc", "label": "USD/EGP (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDTRY_otc", "label": "USD/TRY (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDDZD_otc", "label": "USD/DZD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDNZD_otc", "label": "USD/NZD (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDIDR_otc", "label": "USD/IDR (OTC)", "group": "Forex OTC Pairs"},
    {"value": "USDZAR_otc", "label": "USD/ZAR (OTC)", "group": "Forex OTC Pairs"},
    {"value": "XAUUSD", "label": "Gold", "group": "Commodities (Real Market)"},
    {"value": "XAGUSD", "label": "Silver", "group": "Commodities (Real Market)"},
    {"value": "XBRUSD", "label": "Brent Oil", "group": "Commodities (Real Market)"},
    {"value": "XTIUSD", "label": "WTI Oil", "group": "Commodities (Real Market)"},
    {"value": "NATGAS", "label": "Natural Gas", "group": "Commodities (Real Market)"},
    {"value": "UKBrent_otc", "label": "UK Brent Oil (OTC)", "group": "Commodities OTC"},
    {"value": "USCrude_otc", "label": "US Crude Oil (OTC)", "group": "Commodities OTC"},
    {"value": "XAUUSD_otc", "label": "Gold (OTC)", "group": "Commodities OTC"},
    {"value": "XAGUSD_otc", "label": "Silver (OTC)", "group": "Commodities OTC"},
    {"value": "BTCUSD_otc", "label": "Bitcoin (OTC)", "group": "Cryptocurrencies"},
    {"value": "ARBUSD_otc", "label": "Arbitrum (OTC)", "group": "Cryptocurrencies"},
    {"value": "AXIUSD_otc", "label": "Axie Infinity (OTC)", "group": "Cryptocurrencies"},
    {"value": "HAMUSD_otc", "label": "Hamster (OTC)", "group": "Cryptocurrencies"},
    {"value": "SHIUSD_otc", "label": "Shiba Inu (OTC)", "group": "Cryptocurrencies"},
    {"value": "ETHUSD_otc", "label": "Ethereum (OTC)", "group": "Cryptocurrencies"},
    {"value": "CRLUSD_otc", "label": "Cardano (OTC)", "group": "Cryptocurrencies"},
    {"value": "BNBUSD_otc", "label": "Binance Coin (OTC)", "group": "Cryptocurrencies"},
    {"value": "XRPUSD_otc", "label": "Ripple (OTC)", "group": "Cryptocurrencies"},
    {"value": "LTCUSD_otc", "label": "Litecoin (OTC)", "group": "Cryptocurrencies"},
    {"value": "DOGUSD_otc", "label": "Dogecoin (OTC)", "group": "Cryptocurrencies"},
    {"value": "TRXUSD_otc", "label": "TRON (OTC)", "group": "Cryptocurrencies"},
    {"value": "PEPUSD_otc", "label": "Pepe (OTC)", "group": "Cryptocurrencies"},
    {"value": "GALUSD_otc", "label": "Gala (OTC)", "group": "Cryptocurrencies"},
    {"value": "TRUUSD_otc", "label": "Trump (OTC)", "group": "Cryptocurrencies"},
    {"value": "BONUSD_otc", "label": "Bonk (OTC)", "group": "Cryptocurrencies"},
    {"value": "MANUSD_otc", "label": "Decentraland (OTC)", "group": "Cryptocurrencies"},
    {"value": "MELUSD_otc", "label": "Melania Meme (OTC)", "group": "Cryptocurrencies"},
    {"value": "APTUSD_otc", "label": "Aptos (OTC)", "group": "Cryptocurrencies"},
    {"value": "AVAUSD_otc", "label": "Avalanche (OTC)", "group": "Cryptocurrencies"},
    {"value": "BCHUSD_otc", "label": "Bitcoin Cash (OTC)", "group": "Cryptocurrencies"},
    {"value": "DOTUSD_otc", "label": "Polkadot (OTC)", "group": "Cryptocurrencies"},
    {"value": "LINUSD_otc", "label": "Chainlink (OTC)", "group": "Cryptocurrencies"},
    {"value": "ATOUSD_otc", "label": "Cosmos (OTC)", "group": "Cryptocurrencies"},
    {"value": "SOLUSD_otc", "label": "Solana (OTC)", "group": "Cryptocurrencies"},
    {"value": "ADAUSD_otc", "label": "Cardano (OTC)", "group": "Cryptocurrencies"},
    {"value": "TONUSD_otc", "label": "Toncoin (OTC)", "group": "Cryptocurrencies"},
    {"value": "FLOUSD_otc", "label": "Floki (OTC)", "group": "Cryptocurrencies"},
    {"value": "DASUSD_otc", "label": "Dash (OTC)", "group": "Cryptocurrencies"},
    {"value": "BEAUSD_otc", "label": "Beam (OTC)", "group": "Cryptocurrencies"},
    {"value": "MSFT_otc", "label": "Microsoft (OTC)", "group": "Stocks"},
    {"value": "PFE_otc", "label": "Pfizer (OTC)", "group": "Stocks"},
    {"value": "BA_otc", "label": "Boeing (OTC)", "group": "Stocks"},
    {"value": "JNJ_otc", "label": "Johnson & Johnson (OTC)", "group": "Stocks"},
    {"value": "INTC_otc", "label": "Intel (OTC)", "group": "Stocks"},
    {"value": "MCD_otc", "label": "McDonald's (OTC)", "group": "Stocks"},
    {"value": "AXP_otc", "label": "American Express (OTC)", "group": "Stocks"},
    {"value": "FB_otc", "label": "FACEBOOK INC (OTC)", "group": "Stocks"}
]


# ========== HIDDEN SIGNAL ALGORITHM ==========
def analyze_market_data(candle_array):
    """Professional signal analysis - runs entirely on backend"""
    if not isinstance(candle_array, list) or len(candle_array) < 2:
        raise ValueError('Insufficient candle data')

    latest = candle_array[-1]
    prev = candle_array[-2]

    open_price = float(latest.get('open', 0))
    close_price = float(latest.get('close', 0))
    high_price = float(latest.get('high', close_price))
    low_price = float(latest.get('low', close_price))
    prev_close = float(prev.get('close', open_price))

    momentum = close_price - prev_close
    momentum_percent = (momentum / prev_close) * 100 if prev_close != 0 else 0

    if momentum > 0:
        direction = 'CALL'
    elif momentum < 0:
        direction = 'PUT'
    else:
        direction = 'CALL' if close_price > open_price else 'PUT'

    confidence = 60
    if abs(momentum_percent) > 0.05:
        confidence += 15
    elif abs(momentum_percent) > 0.02:
        confidence += 8

    if len(candle_array) >= 3:
        older = candle_array[-3]
        older_close = float(older.get('close', prev_close))
        if direction == 'CALL' and close_price > older_close:
            confidence += 8
        elif direction == 'PUT' and close_price < older_close:
            confidence += 8

    price_range = (high_price - low_price) / close_price if close_price != 0 else 0
    if price_range > 0.002:
        confidence += 5

    confidence = max(55, min(96, confidence))

    return {
        'direction': direction,
        'price': round(close_price, 5),
        'open': round(open_price, 5),
        'close': round(close_price, 5),
        'bull': close_price >= open_price,
        'confidence': confidence
    }


def fetch_candles_from_api(asset):
    try:
        url = f"{API_BASE_URL}?asset={urllib.parse.quote(asset)}"
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) >= 2:
                if 'open' in data[0] and 'close' in data[0]:
                    return data, None
        return None, f"API returned {response.status_code}"
    except Exception as e:
        return None, str(e)


@app.route('/')
def serve_frontend():
    return send_from_directory('../static', 'index.html')


@app.route('/api/verify', methods=['POST'])
def verify_password():
    try:
        data = request.get_json()
        user_password = data.get('password', '')

        if user_password == VIP_PASSWORD:
            session_token = secrets.token_hex(32)
            active_sessions[session_token] = get_current_time().isoformat()
            return jsonify({
                'success': True,
                'message': 'Access granted',
                'token': session_token
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/pairs', methods=['GET'])
def get_pairs():
    return jsonify({'success': True, 'pairs': TRADING_PAIRS})


@app.route('/api/signal', methods=['POST'])
def generate_signal():
    try:
        data = request.get_json()
        password = data.get('password', '')
        token = data.get('token', '')

        is_authorized = False
        if password and password == VIP_PASSWORD:
            is_authorized = True
        elif token and token in active_sessions:
            is_authorized = True

        if not is_authorized:
            return jsonify({'success': False, 'message': 'VIP access required'}), 401

        asset = data.get('asset', 'EURUSD')
        duration = data.get('duration', '1 Minute')

        candles, error = fetch_candles_from_api(asset)

        if error or not candles or len(candles) < 2:
            return jsonify({'success': False, 'message': 'market is off now'}), 503

        analysis = analyze_market_data(candles)

        # Calculate trade time in UTC+6 (Bangladesh Time)
        now = get_current_time()
        minutes = 1 if duration == '1 Minute' else 5
        trade_time_dt = now + timedelta(minutes=minutes)
        trade_time = format_time(trade_time_dt)
        current_time = format_time(now)

        return jsonify({
            'success': True,
            'signal': {
                'pair': asset,
                'direction': analysis['direction'],
                'confidence': analysis['confidence'],
                'price': analysis['price'],
                'open': analysis['open'],
                'close': analysis['close'],
                'bull': analysis['bull'],
                'expiry': duration,
                'tradeTime': trade_time,
                'currentTime': current_time
            }
        })

    except Exception as e:
        print(f"Signal error: {str(e)}")
        return jsonify({'success': False, 'message': 'market is off now'}), 500


app_handler = app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
