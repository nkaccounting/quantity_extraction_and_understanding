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
        one_result['指标名'] = '年龄'
    if one_result['指标名'] in ['左', '右'] and one_result['单位'] == "":
        one_result['指标名'] += "眼视力"
    if one_result['指标名'] == '空腹' and one_result['单位'] == "mmol/L":
        one_result['指标名'] += "血糖"
    for prune_name in ["昨日", "今晨", "最高"]:
        if prune_name in one_result['指标名']:
            one_result['指标名'] = one_result['指标名'].replace(prune_name, "")
    if one_result['指标名'] == "P蛋白抗体":
        one_result['指标名'] = "抗核糖体P蛋白抗体"
    if (one_result['指标名'] == "BP" or one_result['指标名'] == "血压") and '/' in one_result['数值']:
        systolic_blood_pressure, diastolic_blood_pressure = one_result['数值'].split("/")
        unit = one_result['单位']
        extra = one_result['可信度']
        time = one_result['时间']
        check = one_result["所属检查项目"]
        one_result = [
            {
                '数值': systolic_blood_pressure,
                '单位': unit,
                '指标名': '收缩压',
                "可信度": extra,
                '时间': time,
                "所属检查项目": check
            },
            {
                '数值': diastolic_blood_pressure,
                '单位': unit,
                '指标名': '舒张压',
                "可信度": extra,
                '时间': time,
                "所属检查项目": check
            }
        ]
    return one_result


def extract_one_item(time, context, pipeline, check):
    result = []
    quantity_plus_minus = re.findall("[、:：]([^、:：]*?)[:|：]([\+-]+)", context)
    for quantity in quantity_plus_minus:
        one_result = {
            '数值': quantity[1],
            '单位': '',
            '指标名': quantity[0],
            "可信度": "1.0000000000000000",
            "时间": time,
            "所属检查项目": check
        }
        result.append(one_result)

    # 抽取数值
    Quantities = extract_quantity(context)

    context = after_process(context)

    # 读取数值数字信息
    quantities = [after_process(Q.value) for Q in Quantities]
    # 准备模型输入
    contexts, questions = deal_context_question(context, quantities)

    print(contexts)
    print(questions)

    # t1 = time.time()
    model_res = pipeline(
        question=questions,
        context=contexts,
    )
    # t2 = time.time()

    model_res = [model_res] if isinstance(model_res, dict) else model_res

    for i, r in enumerate(model_res):
        one_result = {
            '数值': Quantities[i].num,
            '单位': Quantities[i].unit,
            '指标名': r['answer'],
            "可信度": str(r['score']),
            "时间": time,
            "所属检查项目": check
        }
        one_result = after_model_process(one_result)
        if isinstance(one_result, dict):
            result.append(one_result)
        elif isinstance(one_result, list):
            for i in one_result:
                result.append(i)

    return result
    # print("模型处理该条用时", t2 - t1)


def extract_one_time(time, content, pipeline):
    checks = pd.read_csv("../data/check.csv", header=None)
    patten_1 = "|".join(checks[0]) + "|" + "|".join(['；', '。', ';'])
    patten_2 = "|".join(checks[0])

    start_indexs = re.finditer(patten_1+"[\d+项]?", content)
    loc = []
    for start_index in start_indexs:
        start = start_index.start()
        if content[start] in ['；', '。', ';']:
            start += 1
        if not loc or start != loc[-1]:
            loc.append(start)

    pre = 0
    queue_content = []

    for location in loc:
        queue_content.append(content[pre:location])
        pre = location
    queue_content.append(content[pre:])
    result = []
    for one_item in queue_content:
        check_name = re.findall(patten_2, one_item)
        check_name = check_name[0] if check_name else ""
        for item in extract_one_item(time, one_item, pipeline, check_name):
            result.append(item)
    return result


def extract_one_text(context: str, pipeline):
    # 预处理文本
    context = pre_process(context)
    # 分时间段，分段处理文本
    times = re.findall("\d{4}-\d{2}-\d{2}", context)
    loc = [i.start() for i in re.finditer("\d{4}-\d{2}-\d{2}", context)]

    pre = 0
    queue_content = []

    for location in loc:
        queue_content.append(context[pre:location])
        pre = location
    queue_content.append(context[pre:])

    times = [""] + times
    result = []
    for i, content in enumerate(queue_content):
        for item in extract_one_time(times[i], content, pipeline):
            result.append(item)
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
                result = extract_one_text(one_text, pipeline)
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
    one_text = "患者今日仍诉乏力、厌油，但精神食欲较前明显好转，未再诉腹胀、恶心，无发热、畏寒，无腹痛、腹泻，大便通畅，小便色黄。查体：精神较前好转，皮肤巩膜重度黄染，双肺呼吸音清，双肺未闻及干湿鸣，心律齐，心音有力，各瓣膜区未闻及病理性杂音，腹软，全腹无明显压痛，肝脾肋下未及，墨菲氏征阴性，肝区叩痛，脾区及双肾区无叩痛，双下肢无浮肿。查尿常规：葡萄糖:+++、蛋白质:+-、胆红素:++、尿胆原:+-、酮体:+-、维生素C:+，提示患者血糖控制差；人免疫缺陷病毒抗原抗体（定量）:0.187、梅毒螺旋体特异抗体（定量）:0.047、快速血浆反应素试验（RPR）:阴性(-)；糖化血红蛋白A1C:6.70%↑、血红蛋白A1:8.40%↑；乙肝两对半：乙肝病毒表面抗体:>960.000mIU/ml↑、乙肝病毒核心抗体:>>13.170PEIU/ml↑，余项阴性；肝纤谱：血清Ⅳ型胶原测定:150.50ng/ml↑、血清Ⅲ型胶原测定:95.28ng/ml↑、血清层粘连蛋白测定:142.50ng/ml↑、血清透明质酸酶测定:218.47ng/ml↑；乙肝病毒DNA定量:"
    result = extract_one_text(one_text, pipeline)
    for r in result:
        print(r)


main()

