from collections import defaultdict

import pandas as pd
from transformers import pipeline

dataframe = pd.read_csv('../data/understanding.csv')
unmasker = pipeline('fill-mask', model='../../bert-base-chinese')

prompt = '是[MASK]？'
# prompt = '[MASK]是？'

analysis = dataframe['context'] + '。' + dataframe['question'] + prompt + dataframe['answer']

token_str_score = defaultdict(float)

for text in analysis:
    if len(text) < 512:
        res = unmasker(text)
        print(res)
        for r in res:
            token_str_score[r['token_str']] += r['score']
        print()

result = reversed(sorted(token_str_score.items(), key=lambda d: d[1]))
for r in result:
    print(r)
