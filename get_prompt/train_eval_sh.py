import os

import pandas as pd

from check_understanding import creat_json

res = ['是？', '份是？', '内是？', '后是？', '复查是？', '就是？', '底是？', '是什么？', '是什事？', '是什点？', '是什级？', '是什？', '是啥？', '是指？', '是甚么？',
       '都是？', '超是？', '钟是？', 'h是？']


for cur_prompt in res:
    dataframe = pd.read_csv('../data/train.csv')
    creat_json(dataframe, 'train'+cur_prompt, '{quantity}' + cur_prompt)

    dataframe = pd.read_csv('../data/eval.csv')
    creat_json(dataframe, 'eval'+cur_prompt, '{quantity}' + cur_prompt)

    os.chdir("../../question_answering/")  # 修改当前工作目录
    os.system('./bert_train.sh ' + cur_prompt)
    os.chdir("../quantity_extraction_and_understanding/get_prompt/")  # 修改当前工作目录
