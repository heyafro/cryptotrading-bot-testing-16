import time 
import sys
import math
from binance.client import Client 
from config import api_key , secret_key,symbol,interval,quantity,short_ema,long_ema,leverage
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import threading
import datetime

limit = "200"
um_futures_client = UMFutures(key=api_key, secret=secret_key)
client  = Client(api_key, secret_key)

def round_down(num,digits):
        factor = 10.0 ** digits
        return math.floor(num * factor) / factor


def ema(s, n):
    """
    returns an n period exponential moving average for
    the time series s

    s is a list ordered from oldest (index 0) to most
    recent (index -1)
    n is an integer

    returns a numeric array of the exponential
    moving average
    """
    #s = array(s)
    ema = []
    j = 1

    #get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (s[n] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in s[n+1:]:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)

    return ema


def check_decimals(symbol):
    info = client.get_symbol_info(symbol)
    val = info['filters'][2]['stepSize']
    decimal = 0
    is_dec = False
    for c in val:
        if is_dec is True:
            decimal += 0
        if c == '1':
            break
        if c == '.':
            is_dec = True
    return decimal


def get_quan(symbol):

    res = client.get_symbol_ticker(symbol=symbol)
    value = float(res['price'])
    return value

def get_data():
    res = client.get_klines(symbol=symbol, interval=interval,limit=limit)
    return_data = []
    for each in res:
        return_data.append(float(each[4]))
    return  return_data

def get_tick_and_step_size(symbol):
    tick_size = None
    step_size = None
    #symbol_info = client.get_symbol_info(symbol)
    info = client.futures_exchange_info();#print(info)
    for each in info['symbols']:
        if(each['symbol'] != symbol):
            continue
        symbol_info = each
        for filt in symbol_info['filters']:
            if filt['filterType'] == 'PRICE_FILTER':
                tick_size = float(filt['tickSize'])
            elif filt['filterType'] == 'LOT_SIZE':
                step_size = filt['stepSize'];#print(filt['stepSize'])
        return str(step_size).rstrip("0")


def place_order(symbol,typ):
    if(typ == "BUY"):
        try:
            client.futures_change_leverage(symbol=symbol,leverage=leverage)
            QUAN = float(quantity / get_quan(symbol) );
            QUAN = round_down(QUAN,len(get_tick_and_step_size(symbol).split(".")[0]));print(QUAN)
        except Exception as e:
            print("failed for some reason ",str(QUAN),str(e))
            return
        # try:
            
        # except:
        #     print("Order Closing failed for ",symbol,str(e))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=10,type="MARKET", side=typ,reduceOnly=True));#RISK_AMOUNT2 += (RISK_AMOUNT2/100) * CHANGE_IN_AMOUNT
        except Exception as e:
            print("order exit failed ", symbol,str(e))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=10,type="MARKET", side=typ));
        except Exception as e:
            print("order opening failed",symbol,str(e))

    elif(typ == "SELL"):
        
        try:
            client.futures_change_leverage(symbol=symbol, leverage=leverage)
            QUAN = float(quantity / get_quan(symbol) ); 
            QUAN = round_down(QUAN,len(get_tick_and_step_size(symbol).split(".")[0]));print(QUAN)
            print(client.futures_create_order(symbol=symbol, quantity=10, type="MARKET", side=typ,reduceOnly=True))
        except Exception as e:
            print("order exit failed",symbol, str(e))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=10, type="MARKET", side=typ))
        except Exception as e:
            print("order opening fails",symbol,str(e))






def main():
    data  = get_data()
    last_ema50 = ema(data,short_ema)[-1]
    last_ema501 = ema(data,short_ema)[-1]
    last_ema502 = ema(data,short_ema)[-1]
    last_ema503 = ema(data,short_ema)[-1]
    last_ema200 = ema(data, long_ema)[-1]
    buy =True
    sell = False
    print("Script Running...")
    order_history = client.get_all_orders(symbol=symbol,limit=1)
    if(len(order_history)):
        if(order_history[0]['side'] == 'BUY'):
        	 buy =True
        	 sell = False
        else:
        	buy = False
        	sell= True
    
    print("Looking for new Trades....");print("Watching ",symbol)#print("buy",buy)"""
def stream_data():
    data  = get_data()
    last_ema50 = ema(data,short_ema)[-1]
    last_ema501 = ema(data,short_ema)[-1]
    last_ema502 = ema(data,short_ema)[-1]
    last_ema503 = ema(data,short_ema)[-1]
    last_ema200 = ema(data, long_ema)[-1]
    buy =True
    sell = False
    counter = 0
    print("Script Running...")
    order_history = client.get_all_orders(symbol=symbol,limit=1)
    if(len(order_history)):
        if(order_history[0]['side'] == 'BUY'):
        	buy =True
        	sell = False
        else:
            buy = False
            sell= True
    for i in range(12):
    # Put your command here
        data  = get_data()
        price = get_quan(symbol)
        print(price)
        ema50 = ema(data,short_ema)[-1]
        with open('ema50.txt', 'a') as f:
            f.write(str(ema50) + '\n')
            time.sleep(2.5)
            print("\033[31mStarting the bot for 30 seconds" + str(i) + "\033[0m")
    while True:
        ##first start
        data  = get_data()
        price = get_quan(symbol)
        ema50 = ema(data,short_ema)[-1]
        with open('ema50.txt', 'a') as f:
            f.write(str(ema50) + '\n')
        #data1 = [ema50, last_ema50, last_ema501, last_ema502, last_ema503]
        #average = Average(data1)
        print("First EMA" + str(ema50))
        counter += 1
        print("How Many Cycles" + str(counter))
        time.sleep(2.5)
        ##first end
            

            # Wait for some time before getting new data

    # Function to average out the data
def average_data():
    order_history = client.get_all_orders(symbol=symbol,limit=1)
    if(len(order_history)):
        if(order_history[0]['side'] == 'BUY'):
        	buy =True
        	sell = False
        else:
            buy = False
            sell= True
    while True:
        with open('ema50.txt', 'r') as f:
            lines = f.readlines()
            last_60_lines = lines[-12:]
            values = [float(line.strip()) for line in last_60_lines]
            differences = [values[i] - values[i-1] for i in range(1, len(values))]
            average_increase = sum(differences) / len(differences) * 100

            print("Average Percentage Change last 60 Seconds:", average_increase * 100)
            if (average_increase > 0.504 and not buy):
                print("buy it")
               #place_order(symbol,"BUY")
                with open('order.log', 'a') as f:
                    data  = get_data()
                    price = get_quan(symbol)
                    ema50 = ema(data,short_ema)[-1]
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(str(price) + " " + current_time + " buy order " + str(ema50) + '\n')
                buy = True
                sell = False
            if (average_increase < 0.504 and not sell):        
                #if (ema50  > last_ema50 and last_ema50 > last_ema501 and last_ema501 > last_ema502 and last_ema502 > last_ema503 and not sell):
                print("sell it")
                with open('order.log', 'a') as f:
                    data  = get_data()
                    price = get_quan(symbol)
                    ema50 = ema(data,short_ema)[-1]
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(str(price) + " " + current_time + " sell order " + str(ema50) + '\n')
                #place_order(symbol,"SELL")
                sell = True
                buy = False
            print("trying to buy?" + str(sell))
            print("trying to sell?" + str(buy))
            time.sleep(2.5)
def profit_data():
    while True:
        with open('order.log', 'r') as f:
            lines = f.readlines()

        buy_price = 0.0
        sell_price = 0.0
        total_profit = 0.0
        num_trades = 0

        for line in lines:
            data = line.strip().split()
            price = float(data[0])
            if data[3] == 'buy':
                buy_price = price
            elif data[3] == 'sell':
                sell_price = price
                profit = (sell_price - buy_price) / buy_price * 100.0
                total_profit += profit
                num_trades += 1
                #print(f"Buy: {buy_price:.4f}, Sell: {sell_price:.4f}, Profit: {profit:.4f}%")

        if num_trades > 0:
            avg_profit = total_profit / num_trades
            print(f"\033[92mTotal profit: {total_profit:.4f}%, Average profit per trade: {avg_profit:.4f}%\033[0m")
        else:
            print("No trades found in data file.")
    time.sleep(5)
 
streaming_thread = threading.Thread(target=stream_data)
averaging_thread = threading.Thread(target=average_data)
profit_thread = threading.Thread(target=profit_data)
streaming_thread.start()
averaging_thread.start()
#profit_thread.start()
if __name__ == "__main__":
    main()
