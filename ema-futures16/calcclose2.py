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
        profit = (((float(closing_trade_info[0]) - float(lines[i].split()[0]) ))  * 100) - 0.03
#        closing2 = float(closing_trade_info[-1])
#        print(f"closing long: {closing2:.2f}%")
#        openinglong = float(lines[i].split()[0])
#        print(f"opening long: {openinglong:.2f}%")
        print(f"Profit long: {profit:.4f}%")
    else:
        profit = ((float(lines[i].split()[0]) - float(closing_trade_info[0])) * 100) - 0.03
        print(f"Profit short: {profit:.4f}%")
    total_profit += profit

print(f"Total profit: {total_profit}")

