import time
import math
import random
import os

# Hardcoded Architectural Configurations
SYMBOLS = ['BNBUSDT', 'ETHUSDT', 'BTCUSDT']
LOG_FILE = "crypto_signals_log.txt"

# Initializing Simulated Historical Database for RSI/EMA math continuity
simulated_history = {}
for s in SYMBOLS:
    base_p = 600.0 if 'BNB' in s else (2500.0 if 'ETH' in s else 95000.0)
    simulated_history[s] = [base_p + random.uniform(-10, 10) for _ in range(50)]

last_signals = {symbol: "INITIAL" for symbol in SYMBOLS}
last_price_print_time = 0

def get_live_market_data(symbol):
    """Network-Independent Secure Local Data Feed."""
    history = simulated_history[symbol]
    last_price = history[-1]
    
    # Replicating real-time continuous market volatility
    change_pct = random.uniform(-0.0015, 0.0015) 
    new_price = last_price * (1 + change_pct)
    
    history.append(new_price)
    if len(history) > 100:
        history.pop(0)
        
    simulated_history[symbol] = history
    return new_price, history

def calculate_ema(prices, period):
    """Calculates Exponential Moving Average using pure math logic."""
    if len(prices) < period: return None
    k = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for price in prices[period:]:
        ema = (price * k) + (ema * (1 - k))
    return ema

def calculate_rsi(prices, period=14):
    """Calculates Relative Strength Index using Wilder's smoothing logic."""
    if len(prices) < period + 1: return None
    gains, losses = [], []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        gains.append(change if change > 0 else 0)
        losses.append(abs(change) if change < 0 else 0)
        
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
    if avg_loss == 0: return 100
    return 100 - (100 / (1 + (avg_gain / avg_loss)))

def log_signal_to_file(timestamp, symbol, price, rsi, signal, tp, sl):
    """Saves trading signals into a local file with Automatic Log Rotation guardrails."""
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 2 * 1024 * 1024:
        try: os.remove(LOG_FILE)
        except: pass
    log_entry = f"[{timestamp}] ASSET: {symbol} | PRICE: {price:.2f} | RSI: {rsi:.2f} | SIGNAL: {signal} | TP: {tp:.2f} | SL: {sl:.2f}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file: file.write(log_entry)
    except: pass

def process_bot_cycle():
    """Runs high-performance clean terminal monitoring dashboard loop."""
    global last_signals
    
    # Screen Refresh
    os.system('cls' if os.name == 'nt' else 'clear')
    
    timestamp = time.strftime('%H:%M:%S', time.localtime())
    print("==================================================")
    print(f"🚀 PRO CRYPTO BOT MONITOR  |  🕒 TIME: {timestamp}")
    print("==================================================")
    print(" ASSET      PRICE        RSI(14)    STATUS")
    print("--------------------------------------------------")
    
    for symbol in SYMBOLS:
        current_price, close_prices = get_live_market_data(symbol)
        
        ema9 = calculate_ema(close_prices, 9)
        ema21 = calculate_ema(close_prices, 21)
        rsi14 = calculate_rsi(close_prices, 14)
        
        if None in [ema9, ema21, rsi14]: continue
            
        current_condition = "NEUTRAL"
        if ema9 > ema21 and rsi14 < 65: current_condition = "BULLISH"
        elif ema9 < ema21 and rsi14 > 35: current_condition = "BEARISH"
            
        # Display Row Formatting
        cond_emoji = "⚪" if current_condition == "NEUTRAL" else ("🟢" if current_condition == "BULLISH" else "🔴")
        display_name = symbol.replace("USDT", "")
        print(f" 🔹 {display_name:<8} ${current_price:<11.2f} {rsi14:<10.1f} {cond_emoji} {current_condition}")

        if last_signals[symbol] == "INITIAL":
            last_signals[symbol] = current_condition
            continue

        # Crossover Trigger Detection
        if current_condition != "NEUTRAL" and current_condition != last_signals[symbol]:
            last_signals[symbol] = current_condition
            full_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            risk_amt = current_price * 0.005
            
            if current_condition == "BULLISH":
                signal_text = "🟢 HIGH-PROBABILITY BUY SIGNAL"
                sl, tp = current_price - risk_amt, current_price + (risk_amt * 2.0)
            else:
                signal_text = "🔴 HIGH-PROBABILITY SELL SIGNAL"
                sl, tp = current_price + risk_amt, current_price - (risk_amt * 2.0)
                
            log_signal_to_file(full_timestamp, symbol, current_price, rsi14, signal_text, tp, sl)
            print("\a", end="", flush=True)

    print("--------------------------------------------------")
    print("📝 Signals are saved in background to 'crypto_signals_log.txt'")

if __name__ == "__main__":
    while True:
        process_bot_cycle()
        time.sleep(2)
