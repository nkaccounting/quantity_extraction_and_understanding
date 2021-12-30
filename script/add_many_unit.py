# encoding=utf-8
# 快速补充未完善的单位（批量）
import pandas as pd

dataframe = pd.read_csv('../data/unit.csv', header=None)

unit_list = list(dataframe[0])

# Add a list of unit
new_unit = ['月前', '年前', '天前', '周前', '余月前', '余年前', '余天前', '余周前', '月余', '年余', '天余', '周余', '月后', '年后', '天后', '周后', '余月后', '余年后', '余天后', '余周后', '月内', '年内', '天内', '周内', '余月内', '余年内', '余天内', '余周内']

unit_list = list(set(unit_list + new_unit))

unit_list.sort(key=lambda x: len(x), reverse=True)

new_unit_list = pd.Series(unit_list)
new_unit_list.to_csv('../data/unit.csv', header=None, index=0)

# 目前补充了哪些单位规则？
# 原有项目的base unit
# 郭老师整理的unit
# 微软text-recognizer
# 自己发现的一些医学表达

# TODO： 后期在使用的过程中可以自行添加unit
