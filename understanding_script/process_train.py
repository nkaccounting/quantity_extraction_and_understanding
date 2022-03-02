from collections import Counter, defaultdict

import pandas as pd
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, QuestionAnsweringPipeline

from quantity_extraction import extract_quantity
from pre_process_for_text import pre_process

# fine_tune_dir = '../../question_answering/chinese_pretrain_mrc_roberta_wwm_ext_large'
# data_dir = '../data/medical_data.csv'
fine_tune_dir = '../是什事？'
data_dir = '../data/unseen.csv'


def cal_index(s: str, target: str):
    n = s.find(target)
    ans = []
    while n != -1:
        ans.append(n)
        n = s.find(target, n + 1)
    return ans


def prepareMTP(model_dir: str):
    model = AutoModelForQuestionAnswering.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer)
    return pipeline


def collect_text(data_dir: str):
    df = pd.read_csv(data_dir)
    df = df.fillna('##')
    text = []
    for column in df.columns[2:6]:
        text += list(df[column])
    # 对获取的文本进行预处理操作
    return [pre_process(t) for t in text]


def extract_quantity_from_text_list(text: list, out_dir: str = '../unseen_result/extract_answer.csv'):
    all_context = []
    all_quantity = []
    all_Quantity = []
    for context in text:
        if len(context) > 3:
            quantities_obj = extract_quantity(context)
            quantities = [quantity.value for quantity in quantities_obj]
            all_context.append(context)
            all_quantity.append(quantities)
            all_Quantity.append(quantities_obj)
    df_extract = pd.DataFrame()
    df_extract['context'] = pd.Series(all_context)
    df_extract['quantities'] = pd.Series(all_quantity)
    df_extract.to_csv(out_dir, index=0, encoding='utf-8')

    return all_context, all_Quantity


def deal_context_question(context: str, quantities: list, prompt: str = '{quantity}是什事？', deal_DUP: bool = True):
    quantities_count = Counter(quantities)
    quantities_loc = defaultdict(int)

    questions = []
    contexts = []

    for quantity in quantities:

        questions.append(prompt.format(quantity=quantity))

        if deal_DUP and quantities_count[quantity] > 1:
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
    return contexts, questions


def process_medical_csv(data_dir: str, out_dir: str = '../unseen_result/understanding.csv', batch: int = 10):
    pipeline = prepareMTP(fine_tune_dir)
    text = collect_text(data_dir)
    all_context, all_Quantity = extract_quantity_from_text_list(text)

    f = open("../unseen_result/out_after_fine-tune.txt", "w")
    all_contexts = []
    all_questions = []
    all_answers = []
    all_scores = []
    for context, Quantities in zip(all_context, all_Quantity):
        print(context, file=f)
        quantities = [quantity.value for quantity in Quantities]

        contexts, questions = deal_context_question(context, quantities)

        all_contexts += contexts
        all_questions += quantities

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
                    "Quantity": Quantities[i + batch * epoch].value,
                    "MeasuredProperty": one_answer,
                    "Unit": Quantities[i + batch * epoch].unit,
                }
                all_answers.append(one_answer['answer'])
                all_scores.append(one_answer['score'])
                result.append(quantity)

        for re in result:
            print(re, file=f)

    f.close()

    df_understanding = pd.DataFrame()
    df_understanding['context'] = pd.Series(all_contexts)
    df_understanding['question'] = pd.Series(all_questions)
    df_understanding['answer'] = pd.Series(all_answers)
    df_understanding['score'] = pd.Series(all_scores)
    df_understanding.to_csv(out_dir, index=0, encoding='utf-8')


process_medical_csv(data_dir)
