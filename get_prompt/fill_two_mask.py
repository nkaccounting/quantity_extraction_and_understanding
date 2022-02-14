import os
from collections import defaultdict

import pandas as pd
from transformers import pipeline

from script.check_understanding import creat_json

dataframe = pd.read_csv('../data/understanding.csv')
unmasker = pipeline('fill-mask', model='../../bert-base-chinese')

# prompt = '[MASK][MASK]是？'
# prompt = '是[MASK][MASK]？'

# 意义不是很大
prompt = '[MASK]是[MASK]？'

analysis = dataframe['context'] + '。' + dataframe['question'] + prompt + dataframe['answer']

token_str_score = defaultdict(float)

for text in analysis:
    if len(text) < 512:
        res = unmasker(text)
        print(res)
        for r0 in res[0]:
            for r1 in res[1]:
                token_str_score[r0['token_str'] + r1['token_str']] += r0['score'] * r1['score']
        print()

result = reversed(sorted(token_str_score.items(), key=lambda d: d[1]))
for r in result:
    if r[1] > 0.1:
        print(r[0])
        cur_prompt = prompt.replace("[MASK][MASK]", r[0])
        print(cur_prompt)
        dataframe = pd.read_csv('../data/understanding.csv')
        creat_json(dataframe, cur_prompt, '{quantity}' + cur_prompt)
        os.system('./bert_train.sh ' + cur_prompt)

# for r in result:
#     if r[1] > 0.1:
#         cur_prompt =
#         print(cur_prompt)
#         dataframe = pd.read_csv('../data/understanding.csv')
#         creat_json(dataframe, cur_prompt, '{quantity}' + cur_prompt)
#         # os.system('./test_shell_2_para.sh ' + arg0 + ' ' + arg1)
