import json
import matplotlib.pyplot as plt

file = open("datacollect.json", "r")
raw = json.load(file)
file.close()

ask = raw["ask"]
bid = raw["bid"]
x= []
y = []

min = 2
max = -100
for spread in ask.keys():
    f_spread = float(spread)
    if (f_spread < min):
        min = f_spread
    if (f_spread > max):
        max = f_spread
    for i in range(ask[spread]):
        x.append(f_spread)

for spread in bid.keys():
    f_spread = float(spread)
    for i in range(bid[spread]):
        y.append(f_spread)


ax = plt.subplot(1,2,1)

plt.hist(x, bins=50, density=True)

ax = plt.subplot(1,2,2)
plt.hist(y,bins=50, density=True)

plt.show()