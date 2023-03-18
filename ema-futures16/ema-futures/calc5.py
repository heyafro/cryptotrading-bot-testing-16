total_profit = 0.0

with open('order.log', 'r') as f:
    lines = f.readlines()
    for i in range(len(lines)):
        line = lines[i].strip().split('\t')
        price = float(line[0].split()[0])
        timestamp = line[1]
        order_type = line[2]
        if order_type == 'buy order':
            j = i+1
            while j < len(lines) and 'closing trade' not in lines[j]:
                j += 1
            if j < len(lines):
                close_line = lines[j].strip().split('\t')
                close_price = float(close_line[3])
                profit = float(close_line[4])
                total_profit += profit
        elif order_type == 'sell order':
            j = i+1
            while j < len(lines) and 'closing trade' not in lines[j]:
                j += 1
            if j < len(lines):
                close_line = lines[j].strip().split('\t')
                close_price = float(close_line[3])
                profit = float(close_line[4])
                total_profit += profit
    if lines[-1].strip().split('\t')[2] != 'closing trade':
        lines.pop()
        last_trade_line = lines[-1].strip().split('\t')
        last_trade_profit = float(last_trade_line[4])
        total_profit -= last_trade_profit

print('Total profit:', total_profit)

