with open('order.log', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if 'closing trade' in line and ('buy' not in lines[i-1] and 'sell' not in lines[i-1]):
        continue
    new_lines.append(line)

with open('order.log', 'w') as f:
    f.writelines(new_lines)