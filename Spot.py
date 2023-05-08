import pandas as pd
import matplotlib.pyplot as plt
spot = pd.read_csv("Data/Costs/spot.csv", decimal=',')
spot = spot[::-1]
spot = spot.reset_index(drop=True)
print(spot)