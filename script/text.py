import pandas as pd

df = pd.read_csv('../data/medical_data.csv')

text = []
for column in df.columns[2:6]:
    text += list(df[column])

for t in text:
    print(t)
    print()
