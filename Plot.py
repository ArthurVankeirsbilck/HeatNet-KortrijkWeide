import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("Prod_heat.csv")

plt.rcParams.update({'font.size': 11})
# rc('figure', figsize=(11.69,8.27))
plt.rcParams["figure.figsize"] = (11.69/2,8.27/2)

plt.plot(df["5"].to_list(), label=r"$p^{el}_{CHP - node 1}$", color='#808080')
# plt.plot(df["9"].to_list(), label=r"$p_{CHP^{el} - node 4}$", color="blue")
# plt.plot(df["15"].to_list(), label=r"$p_{CHP^{el} - node 6}$", color="purple")

plt.gca().spines['right'].set_color('none')
plt.gca().spines['top'].set_color('none')
plt.xlabel("Time (hours)")
plt.ylabel("Production"+r"(${kWh})$")
plt.legend(loc="upper right")
plt.savefig('P_heat_CHP.png')
plt.show()

df = pd.read_csv("Prod_el.csv")

plt.plot(df["0"].to_list(), label=r"$p^{el}_{CHP - node 1}$", color='#808080')
plt.plot(df["9"].to_list(), label=r"$p_{CHP^{el} - node 4}$", color="blue")
plt.plot(df["15"].to_list(), label=r"$p_{CHP^{el} - node 6}$", color="purple")

plt.gca().spines['right'].set_color('none')
plt.gca().spines['top'].set_color('none')
plt.xlabel("Time (hours)")
plt.ylabel("Production"+r"(${kWh})$")
plt.legend(loc="upper right")
plt.savefig('P_el.png')
plt.show()

df = pd.read_csv("Exports.csv")

plt.plot(df["0"].to_list(), label=r"$E_{node 1}$", color='#808080')
plt.plot(df["3"], label=r"$E_{node 4}$", color="blue")
plt.plot(df["5"], label=r"$E_{node 6}$", color="purple")

plt.gca().spines['right'].set_color('none')
plt.gca().spines['top'].set_color('none')
plt.xlabel("Time (hours)")
plt.ylabel("Export"+r"(${kWh})$")
plt.legend(loc="upper right")
plt.savefig('Exports_CHP.png')
plt.show()

df = pd.read_csv("Imports.csv")

plt.plot(df["0"].to_list(), label=r"$I_{node 1}$", color='#808080')
plt.plot(df["3"], label=r"$I_{node 4}$", color="blue")
plt.plot(df["5"], label=r"$I_{node 6}$", color="purple")

plt.gca().spines['right'].set_color('none')
plt.gca().spines['top'].set_color('none')
plt.xlabel("Time (hours)")
plt.ylabel("Import"+r"(${kWh})$")
plt.legend(loc="upper right")
plt.savefig('Exports_CHP.png')
plt.show()

Nodes = ["Node 1","Node 2","Node 3","Node 4","Node 5","Node 6","Node 7"]
Percentages = [4.301513659, 10.32381597, 39.21088358, 20.82118096,	10.32183425,	8.603096542,	6.417675043]

plt.figure('Pie Chart Example', figsize=(4,4), facecolor='white',)

plt.pie(Percentages,labels=Nodes,autopct=lambda p: '{:.0f}%'.format(p))

plt.show()
Nodes = ["Node 2","Node 6","Node 7"]
Percentages = [11.49653274,72.7326724,15.74085956]

plt.figure('Pie Chart Example', figsize=(4,4), facecolor='white')

plt.pie(Percentages,labels=Nodes,autopct=lambda p: '{:.0f}%'.format(p))

plt.show()