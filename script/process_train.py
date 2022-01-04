from collections import Counter, defaultdict

import pandas as pd
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, QuestionAnsweringPipeline

from quantity_extraction import extract_quantity


def cal_index(s: str, target: str):
    n = s.find(target)
    ans = []
    while n != -1:
        ans.append(n)
        n = s.find(target, n + 1)
    return ans


tokenizer = AutoTokenizer.from_pretrained('../../question_answering/chinese_pretrain_mrc_roberta_wwm_ext_large')

model = AutoModelForQuestionAnswering.from_pretrained(
    '../../question_answering/chinese_pretrain_mrc_roberta_wwm_ext_large')

pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer)

df = pd.read_csv('../data/medical_data.csv')

text = []
for column in df.columns[2:6]:
    text += list(df[column])

f = open("out_after_fine-tune.txt", "w")

out_c1 = []
out_qlist = []

out_c2 = []
out_q2 = []
out_a2 = []
out_s2 = []

for context in text:
    if len(context) > 3:
        print(context, file=f)
        quantities_obj = extract_quantity(context)
        quantities = [quantity.value for quantity in quantities_obj]

        out_c1.append(context)
        out_qlist.append(quantities)

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

        out_c2 += contexts
        out_q2 += questions
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
                out_a2.append(one_answer['answer'])
                out_s2.append(one_answer['score'])
                result.append(quantity)

        for re in result:
            print(re, file=f)

f.close()

df_extract = pd.DataFrame()
df_extract['context'] = pd.Series(out_c1)
df_extract['quantities'] = pd.Series(out_qlist)

df_extract.to_csv('extract_answer.csv', index=0, encoding='utf-8')

df_understanding = pd.DataFrame()
df_understanding['context'] = pd.Series(out_c2)
df_understanding['question'] = pd.Series(out_q2)
df_understanding['answer'] = pd.Series(out_a2)
df_understanding['score'] = pd.Series(out_s2)

df_understanding.to_csv('understanding.csv', index=0, encoding='utf-8')
