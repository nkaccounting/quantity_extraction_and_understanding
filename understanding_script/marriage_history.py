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
    age_of_menarche_rule = set(re.findall("初潮[年龄]*(\d+)岁", context)) | set(re.findall("[年龄]*(\d+)岁初潮", context))
    age_of_menopause_rule = re.findall("[绝停]经[年龄]*(\d+)岁", context) + re.findall("[年龄]*(\d+)岁[绝停]经",
                                                                                 context) + re.findall(end_name_pattern,
                                                                                                       context)
    if age_of_menarche_rule:
        age_of_menarche = list(age_of_menarche_rule)[0]

    if age_of_menopause_rule:
        age_of_menopause = list(age_of_menopause_rule)[0]

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


def extract_marry_history(context: str):
    pass


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
            result = extract_menstrual_history(one_text)

            j = re.findall('\d+', dir)[0]
            with open('./res/{j}.json'.format(j=j), 'w', encoding='utf-8') as fp:
                json.dump({
                    '原文': one_text,
                    'result': result
                }, fp, ensure_ascii=False, indent=2)


def one_item():
    one_text = input("请输入")
    result = extract_menstrual_history(one_text)
    print(result)


main()

# 月经史：14岁，4-5/28-32，52岁，既往月经较规则，白带无异常，停经后阴道无异常流液。
# 初潮15岁，绝经50岁，月经正常
