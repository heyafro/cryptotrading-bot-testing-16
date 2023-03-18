total_profit = 0
starting_balance = 10
win_loss = 1
multiplier = 1.3
usdprofit = 0 
with open("orderfake.log", "r") as f:
    lines = f.readlines()

for i in range(0, len(lines), 2):
    if "buy order" in lines[i]:
        order_type = "sell"
    elif "sell order" in lines[i]:
        order_type = "buy"
    else:
        continue

    if i+1 >= len(lines):
        break  # Ignore last line if there's no closing trade

    closing_trade_line = lines[i+1]
    closing_trade_info = closing_trade_line.split()

    if order_type == "buy":
        profit = (((float(closing_trade_info[0]) - float(lines[i].split()[0]) ))  * 100) - 0.06
        usdprofittotal = (float(starting_balance) * profit)
        starting_balance += usdprofittotal
#        print(f"profit subtotal: {usdprofittotal:.4f}")
        if (profit > 0):
            win_loss += 1
        if (profit < 0 ):
            win_loss -= 1
        if (win_loss < 0):
            win_loss = 0
#        print(f"win/loss counter: {win_loss:.0f}")

#        closing2 = float(closing_trade_info[-1])
#        print(f"closing long: {closing2:.2f}%")
#        openinglong = float(lines[i].split()[0])
#        print(f"opening long: {openinglong:.2f}%")
        print(f"Profit long: {profit:.4f}%")
    else:
        profit = ((float(lines[i].split()[0]) - float(closing_trade_info[0])) * 100) - 0.06
        usdprofittotal = float(starting_balance) * (profit)
 #       print(f"profit subtotal: {usdprofittotal:.4f}")
        starting_balance += usdprofittotal   
        if (profit > 0):
            win_loss += 1
        if (profit < 0 ):
            win_loss -= 1
        if (win_loss < 0):
            win_loss = 0
  #      print(f"win/loss counter: {win_loss:.0f}")
        print(f"Profit short: {profit:.4f}%")
        
    total_profit += profit

print(f"Total profit: {total_profit:.4f}%")
print(f"win/loss counter total: {win_loss:.0f}")
print(f"total Profit {starting_balance:.5f}")

#print("\033[32m" + f"Total profit: {total_profit:.4f}%" + "\033[0m")
#print("\033[32m" + f"Total profit: {total_profit:.4f}%" + "\033[0m")
