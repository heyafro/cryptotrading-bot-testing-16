import subprocess
subprocess.run(['python3', 'calcdelete.py'])
total_profit = 0
starting_balance = 10
starting_balance2 = 10
win_loss = 0
win_loss2 = 0
win_loss_long = 0
multiplier = 1.3
usdprofit = 0 
with open("order.log", "r") as f:
    lines = f.readlines()

for i in range(0, len(lines), 2):
    if "buy" in lines[i]:
        order_type = "buy"
    elif "sell" in lines[i]:
        order_type = "sell"
    else:
        continue

    if i+1 >= len(lines):
        break  # Ignore last line if there's no closing trade

    closing_trade_line = lines[i+1]
    closing_trade_info = closing_trade_line.split()

    if order_type == "buy":
        profit = (((float(closing_trade_info[0]) - float(lines[i].split()[0]) ))  * 100) - 0.06
        profit = round(profit, 2)
        usdprofittotal = profit / 100 * starting_balance
        starting_balance += usdprofittotal
        print(f"profit subtotal: {usdprofittotal:.4f}")
        if (profit > 0):
            win_loss_long += 1
        if (profit < 0 ):
            win_loss_long -= 1
        if (win_loss_long < -1):
            win_loss_long = -1
        if (win_loss_long > 2):
            win_loss_long = 2
        print(f"win/loss counter: {win_loss_long:.0f}")


        print(f"Profit long: {profit:.2f}%")
    if order_type == "sell":
        profit = ((float(lines[i].split()[0]) - float(closing_trade_info[0])) * 100) - 0.06
        profit = round(profit, 2)
        usdprofittotal = profit / 100 * starting_balance
        print(f"profit subtotal: {usdprofittotal:.4f}")
        starting_balance += usdprofittotal   
        if (profit > 0):
            win_loss += 1
        if (profit < 0 ):
            win_loss -= 1
        if (win_loss < -1):
            win_loss = -1
        if (win_loss > 2):
            win_loss = 2
        print(f"win/loss counter: {win_loss:.0f}")
        print(f"Profit short: {profit:.2f}%")
        
    total_profit += profit

print(f"Total profit: {total_profit:.4f}%")
print(f"win/loss short counter total: {win_loss:.0f}")
print(f"win/loss long counter total: {win_loss_long:.0f}")
print(f"total Balance $ {starting_balance:.5f}")
with open('winloss.txt', 'a') as f:
    f.write(str(win_loss) + " " + '\n')
f.close()
with open('winlosslong.txt', 'a') as f:
    f.write(str(win_loss_long) + " " + '\n')
f.close()


