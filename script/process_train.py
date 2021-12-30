from collections import Counter, defaultdict

import pandas as pd
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, QuestionAnsweringPipeline

from script.quantity_extraction import extract_quantity


def cal_index(s: str, target: str):
    n = s.find(target)
    ans = []
    while n != -1:
        ans.append(n)
        n = s.find(target, n + 1)
    return ans


tokenizer = AutoTokenizer.from_pretrained('../../chinese_pretrain_mrc_roberta_wwm_ext_large')

model = AutoModelForQuestionAnswering.from_pretrained('../../chinese_pretrain_mrc_roberta_wwm_ext_large')

pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer)

df = pd.read_csv('../data/medical_data.csv')

text = []
for column in df.columns[2:6]:
    text += list(df[column])

f = open("out_no_reinit.txt", "w")

for context in text:
    if len(context) > 3:
        print(context, file=f)
        quantities_obj = extract_quantity(context)
        quantities = [quantity.value for quantity in quantities_obj]

        quantities_count = Counter(quantities)
        quantities_loc = defaultdict(int)

        questions = []
        contexts = []

        for quantity in quantities:
            questions.append(quantity + '指的是？')
            if quantities_count[quantity] > 1:
                index_list = cal_index(context, quantity)
                cur = quantities_loc[quantity]
                if cur == 0:
                    contexts.append(context[:index_list[cur + 1]])
                elif cur == len(index_list) - 1:
                    contexts.append(context[index_list[cur - 1] + len(quantity):])
                else:
                    contexts.append(context[index_list[cur - 1] + len(quantity):index_list[cur + 1]])
                quantities_loc[quantity] += 1
            else:
                contexts.append(context)

        print(questions)
        print(contexts)
        batch = 10
        epoches = len(questions) // batch + 1
        result = []
        for epoch in range(epoches):
            res = pipeline(
                question=questions[epoch * batch:epoch * batch + batch],
                context=contexts[epoch * batch:epoch * batch + batch]
            )
            if isinstance(res, dict):
                res = [res]
            for i, one_answer in enumerate(res):
                quantity = {
                    "Quantity": quantities_obj[i + batch * epoch].value,
                    "MeasuredProperty": one_answer,
                    "Unit": quantities_obj[i + batch * epoch].unit,
                }
                result.append(quantity)

        for re in result:
            print(re, file=f)

f.close()
