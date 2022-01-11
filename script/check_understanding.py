import json
import os

import pandas as pd


def creat_json(df: pd.DataFrame, type: str, prompt: str):
    data = []
    index = 0
    for i in df.itertuples():
        id = str(index)
        index += 1
        context = i[1]
        question = i[2]
        answers = i[3]

        # if answers == "##":
        #     result = {
        #         "id": str(id) + "-hasNoAns",
        #         "title": str(id),
        #         "context": context,
        #         "question": question,
        #         "answers": {
        #             "text": [],
        #             "answer_start": []
        #         }
        #     }
        #     data.append(result)
        if answers != "##":
            try:
                answer_start = context.index(answers)
                right_answers = {
                    "text": [answers],
                    'answer_start': [answer_start]
                }
                result = {
                    "id": str(id) + "-hasAns",
                    "title": str(id),
                    "context": context,
                    "question": prompt.format(quantity=question),
                    "answers": right_answers
                }
                data.append(result)
            except:
                print('未找到')
                print(question)

    if not os.path.exists('../data/json'):
        os.makedirs('../data/json')

    with open(('../data/json/VU_squad2.0_{type}.json').format(type=type), 'w', encoding='utf-8') as fp:
        json.dump({
            'version': 'v2.0',
            'data': data
        }, fp, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    dataframe = pd.read_csv('../data/understanding.csv')
    creat_json(dataframe, 'eval', '{quantity}指的是？')
