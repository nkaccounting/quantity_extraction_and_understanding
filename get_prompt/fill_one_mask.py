import os
from collections import defaultdict

import pandas as pd
from transformers import pipeline

from script.check_understanding import creat_json

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
    if r[1] > 0.1:
        cur_prompt = prompt.replace("[MASK]", r[0])
        print(cur_prompt)
        dataframe = pd.read_csv('../data/understanding.csv')
        creat_json(dataframe, cur_prompt, '{quantity}' + cur_prompt)
        # os.system('./test_shell_2_para.sh ' + arg0 + ' ' + arg1)
