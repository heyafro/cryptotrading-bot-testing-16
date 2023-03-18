with open('order3.log', 'r') as f:
    lines = f.readlines()
    lines.reverse()
total_profit = 0
profit = 0
for i in range(0, len(lines), 1):
    if 'buy order' in lines[i]:
        buy_price = float(lines[i].split()[0])
        sell_price = float(lines[i+1].split()[0])
        gain = ((sell_price - buy_price) / buy_price * 100) - 0.03
        if (sell_price < buy_price):            
            profit += gain
            print(f"Buy Loss: {buy_price:.4f} Sell: {sell_price:.4f} Gain/Loss: {gain:.4f}%")
        if (sell_price > buy_price):
            profit += gain
            print(f"Buy Win: {buy_price:.4f} Sell: {sell_price:.4f} Gain/Loss: {gain:.4f}%")
    
#for i in range(0, len(lines), 1):
    if 'sell order' in lines[i]:
        buy_price = float(lines[i].split()[0])
        sell_price = float(lines[i+1].split()[0])
        gain = ((buy_price - sell_price) / sell_price * 100) - 0.03
        if (sell_price > buy_price):
            profit += gain
            print(f"Sell Loss: {buy_price:.4f} Buy: {sell_price:.4f} Gain/Loss: {gain:.4f}%")
        if (sell_price < buy_price):
            profit += gain
            print(f"Sell Win: {buy_price:.4f} Buy: {sell_price:.4f} Gain/Loss: {gain:.4f}%")
        if IndexError:
            print(f"Total Gain/Loss: {profit:.4f}%")
            #exit(1)
            
            

