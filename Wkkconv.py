import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Data/Energy/Gas/KWEA.csv", parse_dates =["Date"], index_col ="Date")
df = df.resample('H').mean()
df = df[:-1]
df = df.iloc[0:1488]
Total = df['Cons'].sum()

print(df)