with open("order2.log", "r") as f:
    lines = f.readlines()

total_profit = 0.0

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

    if len(closing_trade_info) < 4:  # Ignore if there's no profit info
        continue

    profit = float(closing_trade_info[-1])
    total_profit += profit if order_type == "buy" else -profit

total_profit_percent = (total_profit / float(lines[0].split()[0])) * 100
print(f"Total Profit: {total_profit_percent:.2f}%")

