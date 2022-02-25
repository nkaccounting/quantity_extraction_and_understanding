import json
import os

import pandas as pd

filePath = './supervise_result/'

subname = '/eval_results.json'

df = pd.DataFrame()
df['指标'] = pd.Series(['epoch','eval_P', 'eval_R', 'eval_exact_match', 'eval_f1'])

for firstname in os.listdir(filePath):
    name = filePath + firstname + subname
    with open(name, 'r') as file:
        str = file.read()
        data = json.loads(str)
        df[firstname] = pd.Series([v for k, v in data.items()])

df.to_csv('supervise_result.csv', index=0,encoding='utf-8')
