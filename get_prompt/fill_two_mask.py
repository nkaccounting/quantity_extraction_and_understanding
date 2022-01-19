from collections import defaultdict

import pandas as pd
from transformers import pipeline

dataframe = pd.read_csv('../data/understanding.csv')
unmasker = pipeline('fill-mask', model='../../bert-base-chinese')

# prompt = '[MASK][MASK]是？'
# prompt = '是[MASK][MASK]？'
prompt = '[MASK]是[MASK]？'

analysis = dataframe['context'] + '。' + dataframe['question'] + prompt + dataframe['answer']

token_str_score = defaultdict(float)

for text in analysis:
    if len(text) < 512:
        res = unmasker(text)
        print(res)
        for r0 in res[0]:
            for r1 in res[1]:
                token_str_score[r0['token_str'] +'{是}'+ r1['token_str']] += r0['score'] * r1['score']
        print()

result = reversed(sorted(token_str_score.items(), key=lambda d: d[1]))
for r in result:
    print(r)
