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

    closing_trade_line = lines[i+1]
    closing_trade_info = closing_trade_line.split()

    if order_type == "buy":
        profit = float(closing_trade_info[-1]) - float(lines[i].split()[0])
    else:
        profit = float(lines[i].split()[0]) - float(closing_trade_info[-1])

    total_profit += profit

print(f"Total profit: {total_profit}")

