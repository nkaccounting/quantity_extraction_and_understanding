import json
import os
import re

end_name_table = ['末次月经', '已绝经', '已停经', '绝经', '停经', '末次']
end_name_pattern = "|".join(end_name_table)


def extract_menstrual_history(context: str):
    result = []
    age_of_menarche = ""
    age_of_menopause = ""
    interval = ""

    # 找关键词类型
    age_of_menarche_rule = re.findall("初潮[年龄]*(\d+)岁", context) + re.findall("[年龄]*(\d+)岁初潮", context)
    age_of_menopause_rule = re.findall("[绝停]经[年龄]*(\d+)岁", context) + re.findall("[年龄]*(\d+)岁[绝停]经",
                                                                                 context) + re.findall(end_name_pattern,
                                                                                                       context)
    if age_of_menarche_rule:
        age_of_menarche = age_of_menarche_rule[0]

    if age_of_menopause_rule:
        age_of_menopause = age_of_menopause_rule[0]

    # 找日期类型
    menstrual_history = set(re.findall("(\d+)[岁 ,，]*(\d+-\d+|\d+).?/[ ]?(\d+-\d+|\d+).?[ ，,](\d+)?[岁 ,，。]", context))
    if menstrual_history:
        item = list(menstrual_history)[0]
        age_of_menarche = item[0]
        interval = item[1] + "/" + item[2]
        age_of_menopause = item[3]

    # 没找到标准格式的interval,就单独找/两端的情况
    if not interval:
        long_and_interval = re.findall("(\d+-\d+|\d+).?/(\d+-\d+|\d+).?", context)
        if long_and_interval:
            interval = long_and_interval[0][0] + "/" + long_and_interval[0][1]

    one_result = {
        "类别": "月经史",
        "数值": [],
        "单位": [],
        "初潮年龄": age_of_menarche,
        "经期长度/经期间隔": interval,
        "绝经年龄": age_of_menopause
    }
    result.append(one_result)
    return result


marriage_state = ['离异', '离婚', '丧偶', '未婚', "已婚", "结婚"]

end_state = ['离异', '离婚', '丧偶']


def extract_marry_history(context: str):
    state = re.findall("|".join(marriage_state), context)

    if state:
        # 把离异，离婚，丧偶设置为优先
        state.sort(key=lambda x: -1 if x in end_state else 1)

    state = state[0] if state else ""

    age = re.findall("结婚[年龄]*(\d+)", context) + re.findall("(\d+)岁结婚", context)
    age = age[0] if age else ""

    boy = re.findall("([\d一二三四五六七八九十百千]+)[子儿]", context)
    boy = boy[0] if boy else ""

    girl = re.findall("([\d一二三四五六七八九十百千]+)女", context)
    girl = girl[0] if girl else ""

    child = re.findall("([\d一二三四五六七八九十百千]+)孩", context)
    child = child[0] if child else ""

    G = re.findall("[Gg]([\d一二三四五六七八九十百千]+)", context)
    G = G[0] if G else ""

    P = re.findall("[Pp]([\d一二三四五六七八九十百千]+)", context)
    P = P[0] if P else ""

    one_result = {
        "状态": state,
        "结婚年龄": age,
        "子": boy,
        "女": girl,
        "孩子": child,
        "G": G,
        "P": P
    }
    return one_result


def main():
    filePath = './data'
    for i, j, k in os.walk(filePath):
        dirs = [os.path.join(filePath, text_dir) for text_dir in k]
    for dir in dirs:
        with open(dir, 'r', encoding='utf-8') as f:
            one_text = f.read()
            one_text = "。" + one_text + "。"
            one_text = re.sub("\"|“|”", "", one_text)
            one_text = re.sub("（|）", " ", one_text)
            result = extract_marry_history(one_text)

            j = re.findall('\d+', dir)[0]
            with open('./res/{j}.json'.format(j=j), 'w', encoding='utf-8') as fp:
                json.dump({
                    '原文': one_text,
                    'result': result
                }, fp, ensure_ascii=False, indent=2)


def one_item():
    one_text = input("请输入")
    result = extract_marry_history(one_text)
    print(result)


one_item()
