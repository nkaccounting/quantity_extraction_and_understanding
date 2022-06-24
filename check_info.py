import ast
import json
import os
import pandas as pd
import random

dataframe = pd.read_csv("./data/unit.csv", header=None, encoding="utf-8")
unit_list = list(dataframe[0])


def change_num(num: str):
    try:
        temp = int(num)
        id = random.randint(0, len(num) - 1)
        replace = random.randint(0, 9)
        if id == 0:
            while replace == 0:
                replace = random.randint(0, 9)
        num_list = list(num)
        num_list[id] = str(replace)
        return "".join(num_list)
    except:
        try:
            temp = float(num)
            id = start_id = num.index(".")
            while id == start_id:
                id = random.randint(0, len(num) - 1)
            replace = random.randint(0, 9)
            if id == 0:
                while replace == 0:
                    replace = random.randint(0, 9)
            num_list = list(num)
            num_list[id] = str(replace)
            return "".join(num_list)
        except:
            id = random.randint(0, len(num) - 1)
            replace = random.randint(0, 9)
            if id == 0:
                while replace == 0:
                    replace = random.randint(0, 9)
            num_list = list(num)
            num_list[id] = str(replace)
            return "".join(num_list)


def change_unit(unit: str):
    change = random.randint(0, 1)
    if change:
        new_unit = random.choice(unit_list)
        new_unit = new_unit.replace("\\", "")
        return new_unit
    else:
        return unit


def import_dataframe(dir: str):
    dataframe = pd.DataFrame()
    encoding_name = "error!"
    try:
        dataframe = pd.read_csv(dir, encoding="gb18030")
        encoding_name = "gb18030"
    except:
        try:
            dataframe = pd.read_csv(dir, encoding="utf-8-sig")
            encoding_name = "utf-8-sig"
        except:
            print("-----------------------------------------")
    return dataframe, encoding_name


filePath = "./understanding_script/out_structed_hospital"
dirs = []
for i, j, k in os.walk(filePath):
    dirs += [os.path.join(i, text_dir) for text_dir in k]

res = []
prompt = '{quantity}是什事？'
id = 0
data = []
file = 0
adversarial = True

for dir in dirs:
    if "diag" in dir:
        file += 1
        print(file)
        dataframe, encoding_name = import_dataframe(dir)
        for item in dataframe.itertuples():
            context = item[8]
            for one_quantity in ast.literal_eval(item[9]):
                answers = one_quantity["指标名"]
                question = one_quantity["数值"] + one_quantity["单位"]
                try:
                    answer_start = context.index(answers)
                    right_answers = {
                        "text": [answers],
                        'answer_start': [answer_start]
                    }
                    id += 1
                    if id == 5000:
                        break
                    result = {
                        "id": str(id) + "-hasAns",
                        "title": str(id),
                        "context": context,
                        "question": prompt.format(quantity=question),
                        "answers": right_answers
                    }
                    data.append(result)
                    if adversarial:
                        fake_num = change_num(one_quantity["数值"])
                        fake_unit = change_unit(one_quantity["单位"])
                        question = fake_num + fake_unit
                        result = {
                            "id": str(id) + "-hasNoAns",
                            "title": str(id),
                            "context": context,
                            "question": question,
                            "answers": {
                                "text": [],
                                "answer_start": []
                            }
                        }
                        data.append(result)
                except:
                    pass

if not os.path.exists('./data/json'):
    os.makedirs('./data/json')

with open('./data/json/VU_squad2.0_all.json', 'w', encoding='utf-8') as fp:
    json.dump({
        'version': 'v2.0',
        'data': data
    }, fp, ensure_ascii=False, indent=2)
