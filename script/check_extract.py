import pandas as pd
from ast import literal_eval

dataframe = pd.read_csv('../data/extract_answer.csv')

a = list(dataframe['quantities'])

for i in a:
    k = literal_eval(i)
    print(k)
