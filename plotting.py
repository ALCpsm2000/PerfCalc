from holdings import iterate_calendar, valuations
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("holdings.csv")
df2 = pd.read_csv("transactions.csv")






iterate_calendar("2022-01-01", "2023-12-31",df, df2)
df = pd.DataFrame.from_dict(valuations, orient='index')
df = df.dropna()
print(df)
df.plot()

plt.show()