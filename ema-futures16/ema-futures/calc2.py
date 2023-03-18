log_file = "order.log"
trading_fee = 0.03 / 100  # 0.03%

with open(log_file, "r") as f:
    lines = f.readlines()

buys = []
sells = []

for line in lines:
    parts = line.split()
    if "buy" in parts:
        buys.append(float(parts[0]))
    elif "sell" in parts:
        sells.append(float(parts[0]))

profits = []
for i in range(min(len(buys), len(sells))):
    buy_price = buys[i] * (1 + trading_fee)
    sell_price = sells[i] * (1 - trading_fee)
    profit = (sell_price - buy_price) / buy_price
    profits.append(profit)

total_profit = sum(profits)
print("Total profit (including trading fees): {:.2%}".format(total_profit))

for i in range(min(len(buys), len(sells))):
    buy_price = buys[i] * (1 + trading_fee)
    sell_price = sells[i] * (1 - trading_fee)
    profit = (sell_price - buy_price) / buy_price
    print("Profit on trade {}: {:.2%}".format(i + 1, profit))

