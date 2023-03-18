log_file = "ordershort.log"

with open(log_file, "r") as f:
    lines = f.readlines()

total_percent_difference = 0
num_trades = 0

for i in range(len(lines)-1):
    if "sell order" in lines[i]:
        sell_order_value = float(lines[i].split()[0])
        for j in range(i+1, len(lines)):
            if "closing trade" in lines[j]:
                closing_trade_value = float(lines[j].split()[0])
                percent_difference = abs(closing_trade_value - sell_order_value) / sell_order_value * 100
                total_percent_difference += percent_difference
                num_trades += 1
                print("Percent difference: {:.6f}%".format(percent_difference))
                break

if num_trades > 0:
    average_percent_difference = total_percent_difference / num_trades
    print("Total percent difference: {:.6f}%".format(total_percent_difference))
    print("Average percent difference: {:.6f}%".format(average_percent_difference))
else:
    print("No trades found in the log file.")
