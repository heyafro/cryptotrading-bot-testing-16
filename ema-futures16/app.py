import time 
import sys
import math
from binance.client import Client 
from config import api_key , secret_key,symbol,interval,quantity,short_ema,long_ema,leverage
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
from binance.exceptions import BinanceAPIException
import threading
import datetime
import subprocess

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
            print(client.futures_create_order(symbol=symbol, quantity=6,type="MARKET", side=typ,reduceOnly=True));#RISK_AMOUNT2 += (RISK_AMOUNT2/100) * CHANGE_IN_AMOUNT
        except Exception as e:
            print("order exit failed ", symbol,str(e))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=6,type="MARKET", side=typ));
        except Exception as e:
            print("order opening failed",symbol,str(e))

    elif(typ == "SELL"):
        
        try:
            client.futures_change_leverage(symbol=symbol, leverage=leverage)
            QUAN = float(quantity / get_quan(symbol) ); 
            QUAN = round_down(QUAN,len(get_tick_and_step_size(symbol).split(".")[0]));print(QUAN)
            print(client.futures_create_order(symbol=symbol, quantity=6, type="MARKET", side=typ,reduceOnly=True))
        except Exception as e:
            print("order exit failed",symbol, str(e))
        try:
            print(client.futures_create_order(symbol=symbol, quantity=6, type="MARKET", side=typ))
        except Exception as e:
            print("order opening fails",symbol,str(e))






def main():
    data  = get_data()
    last_ema50 = ema(data,short_ema)[-1]
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
    for i in range(1):
    # Put your command here
        data  = get_data()
        price = get_quan(symbol)
        ema50 = ema(data,short_ema)[-1]
        #ema200 = ema(data,long_ema)[-1]
        #with open('ema200.txt', 'a') as f:
        #    f.write(str(ema200) + '\n')
        #    time.sleep(2.5)
        with open('ema50.txt', 'a') as f:
            f.write(str(ema50) + ' ' + str(price) + '\n')
            time.sleep(1.5)
            print("\033[31mStarting the bot for 90 seconds" + str(i * 1.5) + "\033[0m")
    while True:
        ##get EMA DATA AND PUT IN CACHE
        data  = get_data()
        price = get_quan(symbol)
        ema50 = ema(data,short_ema)[-1]
        ema200 = ema(data,long_ema)[-1]
        with open('ema50.txt', 'a') as f:
            f.write(str(ema50) + " " + str(price) + '\n')
        with open('ema200.txt', 'a') as f:
            f.write(str(ema200) + '\n')      
        #data1 = [ema50, last_ema50, last_ema501, last_ema502, last_ema503]
        #average = Average(data1)
        print("7 EMA" + str(ema50))
        counter += 1
        time.sleep(1.8)
        ##GET EMA DATA AND PUT IN CACHE
            

            # Wait for some time before getting new data

    # Function to average out the data
def average_data():
    order_history = client.get_all_orders(symbol=symbol,limit=1)
    if(len(order_history)):
        if(order_history[0]['side'] == 'BUY'):
        	buy = False
        	sell = False
        else:
            buy = False
            sell= False
            closed = True
        buy = False
        sell = False
        closed = True
        dont_short_close = True
        dont_long_close = True
        buy_price = 1
        sell_price = 1
        tp_buy_price = 1.4
        tp_sell_price = 1.4
        sl_sell_price = 1.4
        sl_buy_price = 1.4
        win_loss_long = 0
        bought_number = 0
        tolerance_var = 0
        sold_number = 0
        trail015 = False
        trail015short = False
        trail019short = False
        trail019 = False
        trail050short = False
        trail050 = False
        trail060short = False
        trail060 = False
        restartlong = False
        restartshort = False
        fake_order = False
        real_order = False
        ##first time reverse
        #to reverse orders on trade loss

        fake_normal = True
        fake_reversed = False
        #fake_longside_entry_short_exit = "BUY"
        #fake_longside_entry_comment = " buy order "
        #fake_longside_exit_comment = " closing trade long "
        #fake_longside_exit = "SELL"
        #fake_longside_entry_short_comment = " sell order "
        #fake_longside_exit_short_comment = " closing trade short "
        #reversed2 = True
        fake_longside_entry_short_exit = "SELL"
        fake_longside_entry_comment = " sell order "
        fake_longside_exit_comment = " closing trade short "
        fake_longside_exit = "BUY"
        fake_longside_entry_short_comment = " buy order "
        fake_longside_exit_short_comment = " closing trade long "
        reversed2 = False
        made_trade = 0
        win_trades = 0
##test order variable 
        #print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side=fake_longside_exit,reduceOnly=True, newOrderRespType="FULL", isHidden=True))
        exit
        #to reverse orders on trade loss end
        subprocess.run(['python3', 'calc.py'])
        subprocess.run(['python3', 'calc2.py'])
        time.sleep(0.2)
        with open('winloss2_long.txt', 'r') as f:
            last_line1 = f.readlines()[-1]
            first_number4 = int(last_line1.split()[0])
            win_loss2_long = first_number4 
        with open('winloss2_short.txt', 'r') as f:
            last_line1 = f.readlines()[-1]
            first_number5 = int(last_line1.split()[0])
            win_loss2_short = first_number5
        with open('winlosslong.txt', 'r') as f:
            last_line1 = f.readlines()[-1]
            first_number3 = int(last_line1.split()[0])
            win_loss_long = first_number3        
        with open('winloss.txt', 'r') as f:
            last_line1 = f.readlines()[-1]
            first_number1 = int(last_line1.split()[0])
            win_loss_short = first_number1
        with open('winloss2.txt', 'r') as f:
            last_line2 = f.readlines()[-1]
            first_number2 = int(last_line2.split()[0])
            win_loss_fake = first_number2 
            if (win_loss_fake == 0):
                if (reversed2):
                    fake_longside_entry_short_exit = "SELL"
                    fake_longside_entry_comment = " sell order "
                    fake_longside_exit_comment = " closing trade short "
                    fake_longside_exit = "BUY"
                    fake_longside_entry_short_comment = " buy order "
                    fake_longside_exit_short_comment = " closing trade long "
                    reversed2 = False
                    win_trades = 0
                else:
                    fake_longside_entry_short_exit = "SELL"
                    fake_longside_entry_comment = " sell order "
                    fake_longside_exit_comment = " closing trade short "
                    fake_longside_exit = "BUY"
                    fake_longside_entry_short_comment = " buy order "
                    fake_longside_exit_short_comment = " closing trade long "
                    reversed2 = False
                    win_trades = 0                    
                    
                    
                    #fake_longside_entry_short_exit = "BUY"
                    ##fake_longside_entry_comment = " buy order "
                    #fake_longside_exit_comment = " closing trade long "
                    #fake_longside_exit = "SELL"
                    #fake_longside_entry_short_comment = " sell order "
                    #fake_longside_exit_short_comment = " closing trade short "
                    #reversed2 = True
                    #win_trades = 0
                    
                made_trade = 0
            if (win_loss_fake == 1):
                made_trade = 0
                win_trades = 1

        tp_buy_price_str = float(tp_buy_price)
        tp_sell_price_str = float(tp_sell_price)
        time.sleep(5)
    while True:
        with open('ema50.txt', 'r') as f:
            lines = f.readlines()
            last_60_lines = lines[-80:]
            last_1_lines = lines[-1:]
            first_words = [line.split()[0] for line in last_60_lines]
            ema_current = last_1_lines[0].split()[0]
            price = get_quan(symbol)
            #current_price = float(price)
            current_price = last_1_lines[0].split()[1]
            values = [float(word.strip()) for word in first_words]
            differences = [values[i] - values[i-1] for i in range(1, len(values))]
            average_increase = sum(differences) / len(differences)
            average_increase *= 100 
            average_increase *= 100
            average_increase *= 3.33333333333
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        with open('scalpdata.txt', 'a') as f:
            f.write(str(average_increase) + " " + timestamp + " $" + str(current_price) + "\n")
            print("\033[31m" + "current price testbot " + str(current_price) + "\033[0m")
            print("\033[32m" + "current ema 7 testbot " + ema_current + "\033[0m")
            print("\033[33m" + " test bot Average Percentage Change last 60 Seconds: {:.2f}%".format(average_increase) + "\033[0m")
            print("tplong" + str(tp_buy_price))
            print("sllong" + str(sl_buy_price))
            print("tpshort" + str(tp_sell_price))
            print("slshort" + str(sl_sell_price))            
        with open('ema200.txt', 'r') as f:
            lines_long = f.readlines()
            last_1_lines_long = lines_long[-1:]
            ema_current_long = last_1_lines_long[0].split()[0]
            print("\033[32m" + "current ema long " + str(ema_current_long) + "\033[0m") 
            #trailing tp long
            if (average_increase > 0.85 and not sell and not closed and not dont_long_close):
                trail015 = True
            if (average_increase > 0.90 and not sell and not closed and not dont_long_close):
                trail019 = True
            if (average_increase > 1 and not sell and not closed and not dont_long_close):
                trail050 = True
            if (average_increase > 0.80 and not sell and not closed and not dont_long_close):
                trail060 = True                
            #trailing tp short
            if (average_increase < -0.85 and not buy and not closed and not dont_short_close):
                trail015short = True
            if (average_increase < -0.90 and not buy and not closed and not dont_short_close):
                trail019short = True
            if (average_increase < -1 and not buy and not closed and not dont_short_close):
                trail050short = True
            if (average_increase < -0.80 and not buy and not closed and not dont_short_close):
                trail060short = True

            ## LONG ORDERS
            if (average_increase > 0.4 and not buy and bought_number < 1 and closed): #and (float(current_price) - float(ema_current)) > 0 ):
                if (not restartshort):
            #if (average_increase > 0.01 and not buy and current_price > ema_current):
                    print("buy it")
                #place_order(symbol,"BUY")
                    with open('order.log', 'a') as f:
                        data  = get_data()
                        price = get_quan(symbol)
                        ema50 = ema(data,short_ema)[-1]
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #f.write(str(price) + " " + current_time + " buy order " + '\n')
                        buy = True
                        sell = False
                        closed = False
                        dont_short_close = True
                        dont_long_close = False
                        buy_price = float(current_price)
                        bought_number = 1
                        sold_number = 0
                        real_order = True
                        tp_buy_price = round(1.0056 * float(buy_price), 4)
                        sl_buy_price = round(0.9954 * float(buy_price), 4)
                        tp_buy_price = float(tp_buy_price)
                        sl_buy_price = float(sl_buy_price)
                        print("tplong" + str(tp_buy_price))
                        print("sllong" + str(sl_buy_price))
                        #print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side="BUY", newOrderRespType="FULL", isHidden=True))

##backetst and real order
                    if (win_loss_long > 0):
                        try:    
                            print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side="BUY", newOrderRespType="FULL", isHidden=True))
                            with open('order.log', 'a') as f:    
                                f.write(str(price) + " " + current_time + " buy order " + '\n')
                        except Exception as e:
                            print("order opening failed",symbol,str(e))
                            average_data()
                            return
                    if (win_loss_long < 1):
                        with open('order.log', 'a') as f:
                                f.write(str(price) + " " + current_time + " buy order backtest " + '\n')
#backtest and real order end 
                        #if (win_trades == 0):
                        #    with open('backetest.log', 'a') as f:
                        #    f.write(str(price) + " " + current_time + " buy order backtest " + '\n')
                    time.sleep(1)
                if (restartshort):
                    #dummy order
                    with open('orderfake.log', 'a') as f:
                        data  = get_data()
                        price = get_quan(symbol)
                        ema50 = ema(data,short_ema)[-1]
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #f.write(str(price) + " " + current_time + fake_longside_entry_comment + '\n')
                    restartshort = True
                    buy = True
                    sell = False
                    closed = False
                    dont_short_close = True
                    dont_long_close = False
                    buy_price = float(current_price)
                    bought_number = 1
                    sold_number = 0
                    fake_order = True
                    if (win_loss2_short > 0):
                        try:    
                            print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side=fake_longside_entry_short_exit, newOrderRespType="FULL", isHidden=True))
                            with open('orderfake.log', 'a') as f:
                                f.write(str(price) + " " + current_time + fake_longside_entry_comment + '\n')

                        except Exception as e:
                            print("order opening failed",symbol,str(e))
                            average_data()
                            return
                    if (win_loss2_short < 1):
                        with open('orderfake.log', 'a') as f:
                            f.write(str(price) + " " + current_time + fake_longside_entry_comment + " backtest " + '\n')
                    #try:
                    #print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side=fake_longside_entry_short_exit, newOrderRespType="FULL", isHidden=True))
                    #except Exception as e:
                    #    print("order opening failed",symbol,str(e))
                    #    average_data()
                    #    continue
                    tp_buy_price = round(1.0056 * float(buy_price), 4)
                    sl_buy_price = round(0.9954 * float(buy_price), 4)
                    tp_buy_price = float(tp_buy_price)
                    sl_buy_price = float(sl_buy_price)
                    print("tplong" + str(tp_buy_price))
                    print("sllong" + str(sl_buy_price))
            #if ((average_increase < -0.05 and not sell and not closed and not dont_long_close) or (float(tp_buy_price) > float(current_price) and not closed and not dont_long_close) or (float(sl_buy_price) < float(current_price) and not closed and not dont_long_close)):
            ##FLAT ORDER LONG
            if ((average_increase < -0.90 and not restartshort and not sell and not closed and not dont_long_close or average_increase < -0.04 and restartshort and not sell and not closed and not dont_long_close) and not sell and not closed and not dont_long_close or ((sl_buy_price - float(current_price) >= 0 or tp_buy_price - float(current_price) <= 0) and not sell and not closed and not dont_long_close) or (trail015 and average_increase < 0.25 or trail019 and average_increase < 0.30 or trail050 and average_increase < 0.40 or trail060 and average_increase < 0.25 ) and not sell and not closed and not dont_long_close): #or ema_current < ema_current_long and not sell and not closed and not dont_long_close ): 
                print("going flat")
                #place_order(symbol,"BUY")
                if (restartshort and fake_order):
                    #no order
                    with open('orderfake.log', 'a') as f:
                        data  = get_data()
                        price = get_quan(symbol)
                        ema50 = ema(data,short_ema)[-1]
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #f.write(str(price) + " " + current_time + fake_longside_exit_comment + str(ema50) + '\n')
                        buy = False
                        sell = False
                       
                        trail015 = False
                        trail015short = False
                        trail019short = False
                        trail019 = False
                        trail050 = False
                        trail050short = False
                        trail060short = False
                        trail060 = False
                        fake_order = False
                        closed = True
                        dont_long_close = False
                        dont_short_close = False 
                    if (win_loss2_short > 0):
                        try:    
                            print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side=fake_longside_exit,reduceOnly=True, newOrderRespType="FULL", isHidden=True))
                            with open('orderfake.log', 'a') as f:
                                f.write(str(price) + " " + current_time + fake_longside_exit_comment + str(ema50) + '\n')

                        except Exception as e:
                            print("order opening failed",symbol,str(e))
                            average_data()
                            return
                    if (win_loss2_short < 1):
                        with open('orderfake.log', 'a') as f:
                            f.write(str(price) + " " + current_time + fake_longside_exit_comment + " backtest " + str(ema50) + '\n')
                    subprocess.run(['python3', 'calc2.py'])
                    #try:
                    ##    print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side=fake_longside_exit,reduceOnly=True, newOrderRespType="FULL", isHidden=True))
                    #except Exception as e:
                    #    print("order opening failed",symbol,str(e))
                    #    average_data()
                    #    continue    
                    made_trade = 1               
                if (not restartshort and real_order):
                    #print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side="SELL",reduceOnly=True, newOrderRespType="FULL", isHidden=True))
                    with open('order.log', 'a') as f:
                        data  = get_data()
                        price = get_quan(symbol)
                        ema50 = ema(data,short_ema)[-1]
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #f.write(str(price) + " " + current_time + " closing trade long " + str(ema50) + '\n')
                        #print(client.futures_create_order(symbol="MATICBUSD", quantity=10, type="MARKET", side="SELL",reduceOnly=True))
                        buy = False
                        sell = False 
                        trail015 = False
                        trail015short = False
                        trail019short = False
                        trail019 = False
                        real_order = False
                        trail050 = False
                        trail050short = False
                        trail060short = False
                        trail060 = False
                        closed = True
                        dont_long_close = False
                        dont_short_close = False
##backetst and real order
                    if (win_loss_long > 0):
                        try:    
                            print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side="SELL",reduceOnly=True, newOrderRespType="FULL", isHidden=True))
                            with open('order.log', 'a') as f:    
                                f.write(str(price) + " " + current_time + " closing trade long " + str(ema50) + '\n')
                        except Exception as e:
                            print("order opening failed",symbol,str(e))
                            average_data()
                            return
                    if (win_loss_long < 1):
                        with open('order.log', 'a') as f:
                                f.write(str(price) + " " + current_time + " closing trade long backtest " + str(ema50) + '\n')
                    subprocess.run(['python3', 'calc.py'])
#backtest and real order end 
            ##flat order short
            if ((average_increase > 0.90 and not restartlong and not buy and not closed and not dont_short_close or average_increase > 0.04 and restartlong and not buy and not closed and not dont_short_close) and not buy and not closed and not dont_short_close or ((sl_sell_price - float(current_price) <= 0 or tp_sell_price - float(current_price) >= 0) and not buy and not closed and not dont_short_close) or (trail015short and average_increase > -0.25 or trail019short and average_increase > -0.30 or trail050short and average_increase > -0.40 or trail060short and average_increase > -0.20) and not buy and not closed and not dont_short_close): #or ema_current > ema_current_long and not buy and not closed and not dont_short_close): #or sl_sell_price - float(current_price) <= 0 and not buy and not closed and not dont_short_close):
                print("going flat")
                #place_order(symbol,"BUY")
                
                #print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side="BUY",reduceOnly=True, newOrderRespType="FULL", isHidden=True))
                if (not restartlong and real_order):
                    with open('order.log', 'a') as f:
                        data  = get_data()
                        price = get_quan(symbol)
                        ema50 = ema(data,short_ema)[-1]
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #f.write(str(price) + " " + current_time + " closing trade short " + str(ema50) + '\n')
                          
                        buy = False
                        sell = False  
                        closed = True
                        trail015short = False
                        trail015 = False
                        trail019short = False
                        trail019 = False
                        real_order = False
                        trail050 = False
                        trail050short = False
                        trail060short = False
                        trail060 = False
                        dont_short_close = False 
                        dont_long_close = False
##backetst and real order
                    if (win_loss_short > 0):
                        try:    
                            print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side="BUY",reduceOnly=True, newOrderRespType="FULL", isHidden=True))
                            with open('order.log', 'a') as f:    
                                f.write(str(price) + " " + current_time + " closing trade short " + str(ema50) + '\n')
                        except Exception as e:
                            print("order opening failed",symbol,str(e))
                            average_data()
                            return
                    if (win_loss_short < 1):
                        with open('order.log', 'a') as f:
                            f.write(str(price) + " " + current_time + " closing trade short backtest" + str(ema50) + '\n')
                    time.sleep(0.1)
                    subprocess.run(['python3', 'calc.py'])
#backtest and real order end                          
                if (restartlong or fake_order):
                    with open('orderfake.log', 'a') as f:
                        data  = get_data()
                        price = get_quan(symbol)
                        ema50 = ema(data,short_ema)[-1]
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #f.write(str(price) + " " + current_time + fake_longside_exit_short_comment + str(ema50) + '\n')
                    buy = False
                    sell = False  
                    closed = True
                    trail015short = False
                    trail015 = False
                    trail019short = False
                    fake_order = False
                    trail019 = False
                    trail050 = False
                    trail050short = False
                    trail060short = False
                    trail060 = False
                    dont_short_close = False 
                    dont_long_close = False  
                    if (win_loss2_long > 0):
                        try:    
                            print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side=fake_longside_entry_short_exit,reduceOnly=True))
                            with open('orderfake.log', 'a') as f:
                                f.write(str(price) + " " + current_time + fake_longside_exit_short_comment + str(ema50) + '\n')

                        except Exception as e:
                            print("order opening failed",symbol,str(e))
                            average_data()
                            return
                    if (win_loss2_long < 1):
                        with open('orderfake.log', 'a') as f:
                            f.write(str(price) + " " + current_time + fake_longside_exit_short_comment + " backtest " + str(ema50) + '\n')
                    subprocess.run(['python3', 'calc2.py'])
                    made_trade = 1                                  
            ####SELL ORDERS
            if (average_increase < -0.4 and not sell and sold_number < 1 and closed): #and (float(current_price) - float(ema_current)) < 0):
                if (not restartlong):#if (average_increase < -0.02 and not sell and current_price < ema_current):        
                #if (ema50  > last_ema50 and last_ema50 > last_ema501 and last_ema501 > last_ema502 and last_ema502 > last_ema503 and not sell):
                    print("sell it")
                    #print(client.futures_create_order(symbol="MATICBUSD", quantity=10, type="MARKET", side="SELL", newOrderRespType="FULL", isHidden=True))
                    with open('order.log', 'a') as f:
                        data  = get_data()
                        price = get_quan(symbol)
                        ema50 = ema(data,short_ema)[-1]
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #f.write(str(price) + " " + current_time + " sell order " + '\n')
                        #place_order(symbol,"SELL")
                        
                        sell = True
                        buy = False
                        closed = False
                        dont_long_close = True
                        dont_short_close = False
                        bought_number = 0
                        real_order = True
                        sold_number = 1
                        sell_price = current_price
                        tp_sell_price = round(0.9944 * float(sell_price), 4)
                        sl_sell_price = round(1.0043 * float(sell_price), 4)   
##backetst and real order
                    if (win_loss_short > 0):
                        try:    
                            print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side="SELL", newOrderRespType="FULL", isHidden=True))
                            with open('order.log', 'a') as f:    
                                f.write(str(price) + " " + current_time + " sell order " + '\n')
                        except Exception as e:
                            print("order opening failed",symbol,str(e))
                            average_data()
                            return
                    if (win_loss_short < 1):
                        with open('order.log', 'a') as f:
                            f.write(str(price) + " " + current_time + " sell order backtest " + '\n')
#backtest and real order end       
                    time.sleep(1)
                if (restartlong):
                    with open('orderfake.log', 'a') as f:
                        data  = get_data()
                        price = get_quan(symbol)
                        ema50 = ema(data,short_ema)[-1]
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        sell = True
                        buy = False
                        closed = False
                        dont_long_close = True
                        dont_short_close = False
                        fake_order = True
                        bought_number = 0
                        sold_number = 1
                        sell_price = current_price
                        tp_sell_price = round(0.9944 * float(sell_price), 4)
                        sl_sell_price = round(1.0044 * float(sell_price), 4)  
                    if (win_loss2_long > 0):
                        try:    
                            print(client.futures_create_order(symbol="MATICBUSD", quantity=8, type="MARKET", side=fake_longside_exit, newOrderRespType="FULL", isHidden=True))
                            with open('orderfake.log', 'a') as f:    
                                f.write(str(price) + " " + current_time + fake_longside_entry_short_comment + '\n')
                            
                        except Exception as e:
                            print("order opening failed",symbol,str(e))
                            average_data()                   
                            return
                    if (win_loss2_long < 1):
                        with open('orderfake.log', 'a') as f:
                            f.write(str(price) + " " + current_time + fake_longside_entry_short_comment + " backtest " + '\n')


            ####end SELL ORDERS
            ##restart long orders
            if (ema_current > ema_current_long):
                restartlong = True
                restartshort = False

            ##restart short orders
            if (ema_current < ema_current_long):
                restartshort = True
                restartlong = False

            print("trying to buy?" + str(sell))
            print("trying to sell?" + str(buy))
            print("order closed?" + str(closed))
            print("dont short close" + str(dont_short_close))
            print("dont long close" + str(dont_long_close))
            print("sold number" + str(sold_number))
            print("bought number" + str(bought_number))
            print("restart short" + str(restartshort))
            print("restart long" + str(restartlong))
            print("reversed? " + str(reversed2))
            print("win_trades" +" " + str(win_trades))
            print("normal_long_trades" +" " + str(win_loss_long))
            print("normal_short_trades" +" " + str(win_loss_short))
            print("stophunt_short_trades" +" " + str(win_loss2_short))
            print("stophunt_long_trades" +" " + str(win_loss2_long))
            print("fake_longside_entry_short_exit" +" " + str(fake_longside_entry_short_exit))
###Flipping orders on loss
            #subprocess.run(['python3', 'calc.py'])
            with open('winlosslong.txt', 'r') as f:
                last_line1 = f.readlines()[-1]
                first_number3 = int(last_line1.split()[0])
                win_loss_long = first_number3        
            with open('winloss.txt', 'r') as f:
                last_line1 = f.readlines()[-1]
                first_number1 = int(last_line1.split()[0])
                win_loss_short = first_number1            
            with open('winloss2_long.txt', 'r') as f:
                last_line1 = f.readlines()[-1]
                first_number4 = int(last_line1.split()[0])
                win_loss2_long = first_number4 
            with open('winloss2_short.txt', 'r') as f:
                last_line1 = f.readlines()[-1]
                first_number5 = int(last_line1.split()[0])
                win_loss2_short = first_number5        
            if (made_trade == 3):
                subprocess.run(['python3', 'calc.py'])
                subprocess.run(['python3', 'calc2.py'])
                time.sleep(0.2)
                with open('winloss2.txt', 'r') as f:
                    last_line2 = f.readlines()[-1]
                    first_number2 = int(last_line2.split()[0])
                    win_loss_fake = first_number2 
                    if (win_loss_fake == 0):
                        if (reversed2):
                            fake_longside_entry_short_exit = "SELL"
                            fake_longside_entry_comment = " sell order "
                            fake_longside_exit_comment = " closing trade short "
                            fake_longside_exit = "BUY"
                            fake_longside_entry_short_comment = " buy order "
                            fake_longside_exit_short_comment = " closing trade long "
                            reversed2 = False
                            win_trades = 0
                        else:
                            fake_longside_entry_short_exit = "SELL"
                            fake_longside_entry_comment = " sell order "
                            fake_longside_exit_comment = " closing trade short "
                            fake_longside_exit = "BUY"
                            fake_longside_entry_short_comment = " buy order "
                            fake_longside_exit_short_comment = " closing trade long "
                            reversed2 = False
                            win_trades = 0
                            
                            #fake_longside_entry_short_exit = "BUY"
                            #fake_longside_entry_comment = " buy order "
                            #fake_longside_exit_comment = " closing trade long "
                            #fake_longside_exit = "SELL"
                            #fake_longside_entry_short_comment = " sell order "
                            #fake_longside_exit_short_comment = " closing trade short "
                            #reversed2 = True
                            #win_trades = 0
                    
                        made_trade = 0
                    if (win_loss_fake == 1):
                        made_trade = 0
                        win_trades = 1
            time.sleep(1.8)
### end flipping orders on loss
            f.close()
def profit_data():
    while True:
        total_profit = 0

        with open("order.log", "r") as f:
            lines = f.readlines()

        for i in range(0, len(lines), 2):
            if "buy order" in lines[i]:
                order_type = "buy"
            elif "sell order" in lines[i]:
                order_type = "sell"
            else:
                continue

            if i+1 >= len(lines):
                break  # Ignore last line if there's no closing trade

            closing_trade_line = lines[i+1]
            closing_trade_info = closing_trade_line.split()

            if order_type == "buy":
                profit = (((float(closing_trade_info[0]) - float(lines[i].split()[0]) ))  * 100) - 0.06

            else:
                profit = ((float(lines[i].split()[0]) - float(closing_trade_info[0])) * 100) - 0.06

            total_profit += profit

            print("\033[32m" + f"Total profit: {total_profit:.4f}%" + "\033[0m")
            f.close()
            time.sleep(1.5)
 
streaming_thread = threading.Thread(target=stream_data)
averaging_thread = threading.Thread(target=average_data)
profit_thread = threading.Thread(target=profit_data)
streaming_thread.start()
averaging_thread.start()
#profit_thread.start()
if __name__ == "__main__":
    main()
