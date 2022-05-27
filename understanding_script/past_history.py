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
                contexts.append(context[:index_list[cur + 1]] + "。")
            elif cur == len(index_list) - 1:
                contexts.append(context[index_list[cur - 1] + len(quantity):] + "。")
            else:
                contexts.append(context[index_list[cur - 1] + len(quantity):index_list[cur + 1]] + "。")
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
    one_result["指标名"] = one_result["指标名"].replace("有", "")
    if one_result["指标名"] == "每日" and "支" in one_result["单位"]:
        one_result["指标名"] = "吸烟抽烟"
        one_result["单位"] = "支/日"
    if one_result["指标名"] == "平均" and "克/日" in one_result["单位"]:
        one_result["指标名"] = "饮酒喝酒"
        one_result["单位"] = "克/日"
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


def extract_one_family(family_name: str, context: str):
    result = []
    past_history = pd.read_csv("../data/past_history.csv", header=None)
    past_history_pattern = "|".join(past_history[0])

    family_history_temp = set(re.findall("({past_history_pattern})[及、和]?({past_history_pattern})?".format(
        past_history_pattern=past_history_pattern), context))

    family_history = set()

    for f in family_history_temp:
        if f[1]:
            family_history.add(f[0] + "和" + f[1])
        else:
            family_history.add(f[0])
    no_info = get_no_info(context)
    no_remove = get_remove_set(family_history, no_info)
    family_history.difference_update(no_remove)
    if family_history:
        for item in family_history:
            one_result = {
                "类别": "家族史",
                "名称": item,
                "数值": [],
                "单位": [],
                "家人": family_name,
            }
            result.append(one_result)
    return result


def extract_family_history(context: str):
    result = []
    family = pd.read_csv("../data/family.csv", header=None)
    family_pattern = "|".join(family[0])
    start_indexs = re.finditer("({family_pattern})?[及和、]?({family_pattern})".format(family_pattern=family_pattern),
                               context)
    loc = []
    name = [""]
    for start_index in start_indexs:
        start = start_index.start()
        end = start_index.end()
        loc.append(start)
        name.append(context[start:end])
    pre = 0
    queue_content = []
    for location in loc:
        queue_content.append(context[pre:location])
        pre = location
    queue_content.append(context[pre:])
    for i, one_item in enumerate(queue_content):
        for item in extract_one_family(name[i], one_item):
            result.append(item)
    return result


def get_no_info(context: str):
    # 否认和无和不的表述
    no_info = set(re.findall("否认(.*?)[，。；,有]", context)) | set(re.findall("无(.*?)[，。；,有]", context)) | set(
        re.findall("不(.*?)[，。；,有]", context))
    no_info_long = set()
    no_info_set = set()
    # 将带、的长文本拆解出来并记录，将拆解结果送入集合
    for no in no_info:
        if "、" in no:
            no_info_long.add(no)
            no_info_set.update(no.split("、"))
    no_info.difference_update(no_info_long)
    no_info.update(no_info_set)
    return no_info


def get_remove_set(positive_set, negative_set):
    remove_set = set()
    for positive_item in positive_set:
        for negative_item in negative_set:
            if positive_item in negative_item:
                remove_set.add(positive_item)
    return remove_set


def extract_past_history(context: str):
    result = []
    # 抽取出术语表里的表述
    past_history = pd.read_csv("../data/past_history.csv", header=None)
    past_history_pattern = "|".join(past_history[0])
    in_table_past_history = set(
        re.findall(
            "({past_history_pattern})".format(past_history_pattern=past_history_pattern),
            context
        )
    )
    # 抽取出有XXX的表述
    has_info = set(re.findall("有(.*?)[、，。；,]", context))

    # 找出术语表的表述比有XXX抽取出来更规范，删掉有XXX
    has_info_remove_set = set()
    for in_table_past_history_item in in_table_past_history:
        for has_info_item in has_info:
            if in_table_past_history_item in has_info_item:
                has_info_remove_set.add(has_info_item)
    has_info.difference_update(has_info_remove_set)

    # 合并两种规则
    past_history_set = in_table_past_history | has_info

    # 获取无，否认，不的相关表述（、还有长串）
    no_info = get_no_info(context)
    # 移除掉无和否认和不
    no_remove = get_remove_set(past_history_set, no_info)
    past_history_set.difference_update(no_remove)

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
    # 查找个人史里的内容
    personal_history = pd.read_csv("../data/personal_history.csv", header=None)
    personal_history_pattern = "|".join(personal_history[0])
    in_table_personal_history = set(
        re.findall(
            "({personal_history_pattern})".format(personal_history_pattern=personal_history_pattern),
            context
        )
    )
    # 去除否定相关表述
    no_info = get_no_info(context)
    no_remove = get_remove_set(in_table_personal_history, no_info)
    in_table_personal_history.difference_update(no_remove)

    # 获取个人史程度相关表述
    degree_history = pd.read_csv("../data/adv.csv", header=None)
    degree_pattern = "|".join(degree_history[0])
    for item in in_table_personal_history:
        degree = ""
        if item in ['吸烟', '抽烟', '饮酒', '喝酒']:
            # 程度词在前与程度词在后，两种模式
            degree = set(
                re.findall("({degree_pattern}){item}".format(degree_pattern=degree_pattern, item=item), context)
            ) | set(re.findall("{item}({degree_pattern})".format(degree_pattern=degree_pattern, item=item), context))
        degree = list(degree)[0] if degree else ""
        one_result = {
            "类别": "个人史",
            "名称": item,
            "程度": degree,
            "数值": [],
            "单位": [],
        }
        result.append(one_result)
    return result


# 程序入口，读取文本，然后文本一条一条送入程序
def main():
    pipeline = prepareMTP()
    filePath = './data'
    for i, j, k in os.walk(filePath):
        dirs = [os.path.join(filePath, text_dir) for text_dir in k]
    for dir in dirs:
        with open(dir, 'r', encoding='utf-8') as f:
            one_text = f.read()
            one_text = "。" + one_text
            one_text = one_text.replace("\"", "")
            one_text = one_text.replace("“", "")
            one_text = one_text.replace("”", "")
            # print(one_text)

            result = extract_family_history(one_text)

            quantity_result = extract_quantity_dimension(one_text, pipeline)
            for qr in quantity_result:
                print(qr)
            for quantity_res in quantity_result:
                name = quantity_res["指标名"]
                for res in result:
                    if res["名称"] in name or name in res["名称"]:
                        res["数值"].append(quantity_res["数值"])
                        res["单位"].append(quantity_res["单位"])
            for r in result:
                r['名称'] = re.sub("\d+[年月周日]", "", r['名称'])
            j = re.findall('\d+', dir)[0]
            with open('./res/{j}.json'.format(j=j), 'w', encoding='utf-8') as fp:
                json.dump({
                    '原文': one_text,
                    'result': result
                }, fp, ensure_ascii=False, indent=2)


def one_item():
    pipeline = prepareMTP()
    one_text = input('请输入')
    one_text = "。" + one_text
    one_text = one_text.replace("\"", "")
    # 实际处理的时候把它们划分开来
    result = extract_family_history(one_text)

    quantity_result = extract_quantity_dimension(one_text, pipeline)
    for qr in quantity_result:
        print(qr)
    for quantity_res in quantity_result:
        name = quantity_res["指标名"]
        for res in result:
            if res["名称"] in name or name in res["名称"]:
                res["数值"].append(quantity_res["数值"])
                res["单位"].append(quantity_res["单位"])
    for r in result:
        r['名称'] = re.sub("\d+[年月周日]", "", r['名称'])
    for r in result:
        print(r)


main()

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
