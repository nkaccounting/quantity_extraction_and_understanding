# encoding=utf-8
import json
import os
import re
from collections import Counter, defaultdict

import pandas as pd
import torch
from transformers import BertForQuestionAnswering, AutoTokenizer, QuestionAnsweringPipeline

from pre_process_for_text import pre_process, after_process
from quantity_extraction import extract_quantity


# 准备模型
def prepareMTP(model_dir: str = '../whatisit'):
    model = BertForQuestionAnswering.from_pretrained(model_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    if torch.cuda.is_available():
        pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer, device=0)
    else:
        pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer)
    return pipeline


# 辅助去重过程
def cal_index(s: str, target: str):
    n = s.find(target)
    ans = []
    while n != -1:
        ans.append(n)
        n = s.find(target, n + 1)
    return ans


# 输入一个content，和一组数值；构造成每个数值对应的content(主要去重）
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


# 模型后处理过程
def after_model_process(one_result):
    if one_result['单位'] in ["↑", "↓", "、", "，", "。", "；"]:
        one_result['单位'] = ''
    if re.match("\d+\.$", one_result['数值']):
        return None
    if one_result['单位'] == '岁':
        return None
    return one_result


def extract_quantity_dimension(context, pipeline):
    result = []
    context = pre_process(context)
    # 抽取数值
    Quantities = extract_quantity(context)
    context = after_process(context)
    # 读取数值数字信息
    quantities = [after_process(Q.value) for Q in Quantities]
    # 准备模型输入
    contexts, questions = deal_context_question(context, quantities)
    print(contexts)
    print(questions)
    model_res = pipeline(
        question=questions,
        context=contexts,
    )
    model_res = [model_res] if isinstance(model_res, dict) else model_res

    for i, r in enumerate(model_res):
        # TODO 临时针对相似度过高造成的类似数值进行处理，重新训练模型后记得删除
        if r['score'] < 0.5:
            loc = contexts[i].index(questions[i][:-4])
            start = loc - 20 if loc - 20 >= 0 else 0
            c = contexts[i][start:loc + 20]
            q = questions[i]
            temp_res = pipeline(
                question=q,
                context=c,
            )
            if temp_res['score'] > 0.9:
                r['answer'] = temp_res['answer']
                r['score'] = temp_res['score']

        one_result = {
            '数值': Quantities[i].num,
            '单位': Quantities[i].unit,
            '指标名': r['answer'],
        }
        one_result = after_model_process(one_result)
        if isinstance(one_result, dict):
            result.append(one_result)
        elif isinstance(one_result, list):
            for i in one_result:
                result.append(i)
    return result


def extract_past_history(context: str):
    result = []
    has_info_remove_set = set()
    in_table_past_history_remove_set = set()
    past_history = pd.read_csv("../data/past_history.csv", header=None)
    family = pd.read_csv("../data/family.csv", header=None)

    past_history_pattern = "|".join(past_history[0])
    family_pattern = "|".join(family[0])

    has_info = set(re.findall("有(.*?)[、，]", context))
    in_table_past_history = set(
        re.findall(
            "[^否认|^无]({past_history_pattern})".format(past_history_pattern=past_history_pattern),
            context
        )
    )
    family_history = set(
        re.findall(
            "({family_pattern})?[及和]?({family_pattern})有({past_history_pattern})".format(
                family_pattern=family_pattern,
                past_history_pattern=past_history_pattern
            ),
            context
        )
    )
    if family_history:
        for item in family_history:
            in_table_past_history_remove_set.add(item[2])
            if item[0] and item[1]:
                family_name = item[0] + "和" + item[1]
            else:
                family_name = item[1]
            one_result = {
                "类别": "家族史",
                "名称": item[2],
                "数值": [],
                "单位": [],
                "家人": family_name,
            }
            result.append(one_result)
    for in_table_past_history_item in in_table_past_history:
        for has_info_item in has_info:
            # 术语表的表述比有XXX抽取出来更规范
            if in_table_past_history_item in has_info_item:
                has_info_remove_set.add(has_info_item)
    # 既往史中删除有XXX中表达冗余的部分
    has_info.difference_update(has_info_remove_set)
    # 既往史中删除家族史
    past_history_set = (in_table_past_history | has_info).difference(in_table_past_history_remove_set)
    for item in past_history_set:
        one_result = {
            "类别": "既往史",
            "名称": item,
            "数值": [],
            "单位": [],
        }
        result.append(one_result)

    return result


def extract_personal_history(context: str):
    result = []
    personal_history = pd.read_csv("../data/personal_history.csv", header=None)
    personal_history_pattern = "|".join(personal_history[0])
    in_table_personal_history = set(
        re.findall(
            "[^否认|^无]({personal_history_pattern})".format(personal_history_pattern=personal_history_pattern),
            context
        )
    )
    # print(in_table_personal_history)
    # ring_name = []
    # remove_set=set()
    # for item in in_table_personal_history:
    #     ring = re.findall("戒(.*)", item)
    #     if ring:
    #         ring_name.append(ring[0])
    # for item in in_table_personal_history:
    #     if not "戒" in item:
    #         for ring in ring_name:
    #             if ring in item:
    #                 remove_set.add(item)
    # print(remove_set)
    for item in in_table_personal_history:
        one_result = {
            "类别": "个人史",
            "名称": item,
            "数值": [],
            "单位": [],
        }
        result.append(one_result)
    return result


def extract_menstrual_history(context: str):
    result = []
    menstrual_history = set(re.findall("月经史[：:](.*?)[，,](.*?)[，,](.*?)[，,]", context))
    for item in menstrual_history:
        one_result = {
            "类别": "月经史",
            "名称": "月经史",
            "数值": [],
            "单位": [],
            "初潮年龄": item[0],
            "经期长度/经期间隔": item[1],
            "绝经年龄": item[2]
        }
        result.append(one_result)

    return result


# 程序入口，读取文本，然后文本一条一条送入程序
def main():
    count = 0
    pipeline = prepareMTP()
    filePath = './data'
    for i, j, k in os.walk(filePath):
        dirs = [os.path.join(filePath, text_dir) for text_dir in k]
    for dir in dirs:
        with open(dir, 'r', encoding='utf-8') as f:
            one_text = f.read()
            if len(one_text) <= 512:
                count += 1
                result = extract_quantity_dimension(one_text, pipeline)
                j = re.findall('\d+', dir)[0]
                with open('./res/{j}.json'.format(j=j), 'w', encoding='utf-8') as fp:
                    json.dump({
                        '原文': one_text,
                        'result': result
                    }, fp, ensure_ascii=False, indent=2)
                if count == 100:
                    break


def one_item():
    pipeline = prepareMTP()
    one_text = input('请输入')
    result = extract_past_history(one_text) + extract_personal_history(one_text) + extract_menstrual_history(one_text)

    quantity_result = extract_quantity_dimension(one_text, pipeline)
    for quantity_res in quantity_result:
        name = quantity_res["指标名"]
        for res in result:
            if res["名称"] in name or name in res["名称"]:
                res["数值"].append(quantity_res["数值"])
                res["单位"].append(quantity_res["单位"])
    for r in result:
        print(r)


one_item()

# {
#     "类别": "既往史/个人史/婚育史/月经史",
#     "名称": "高血压",
#     "数值": "30",  # 没有的话不会出现该字段/为空
#     "单位": "年",  # 没有的话不会出现该字段/为空
#     "家人": "姐姐和妹妹",  # 没有的话不会出现该字段/为空
#     "初潮年龄": "14岁",  # 没有的话不会出现该字段/为空
#     "经期长度/经期间隔": "4-5/28-32",  # 没有的话不会出现该字段/为空
#     "绝经年龄": "52岁"  # 没有的话不会出现该字段/为空
# }
