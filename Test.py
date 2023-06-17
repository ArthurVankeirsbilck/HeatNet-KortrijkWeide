import numpy as np
import pandas as pd
prices = {}
time_list = range(1488)
node_list = [1,2,3,4,5,6,7]
Plant_list = [1,2,3]

price_list_node1_plant1 = [86.10]*744 + [75.20]*744
price_list_node1_plant2 = [86.10]*744 + [75.20]*744
price_list_node1_plant3 = [86.10]*744 + [75.20]*744

price_list_node2_plant1 = [86.10]*744 + [75.20]*744
price_list_node2_plant2 = [86.10]*744 + [75.20]*744
price_list_node2_plant3 = [86.10]*744 + [75.20]*744

price_list_node3_plant1 = [86.10]*744 + [75.20]*744
price_list_node3_plant2 = [86.10]*744 + [75.20]*744
price_list_node3_plant3 = [86.10]*744 + [75.20]*744

price_list_node4_plant1 = [86.10]*744 + [75.20]*744
price_list_node4_plant2 = [86.10]*744 + [75.20]*744
price_list_node4_plant3 = [86.10]*744 + [75.20]*744

price_list_node5_plant1 = [86.10]*744 + [75.20]*744
price_list_node5_plant2 = [86.10]*744 + [75.20]*744
price_list_node5_plant3 = [86.10]*744 + [75.20]*744

price_list_node6_plant1 = [119.17]*744 + [100.53]*744
price_list_node6_plant2 = [119.17]*744 + [100.53]*744
price_list_node6_plant3 = [119.17]*744 + [100.53]*744

price_list_node7_plant1 = [119.17]*744 + [100.53]*744
price_list_node7_plant2 = [119.17]*744 + [100.53]*744
price_list_node7_plant3 = [119.17]*744 + [100.53]*744

for i in node_list:
    for j in Plant_list:
        price_list = globals()[f"price_list_node{i}_plant{j}"]
        for time, price in zip(time_list, price_list):
            prices[(i, j, time)] = price

print(prices)