# encoding=utf-8
# 快速补充未完善的单位（批量）
import pandas as pd

dataframe = pd.read_csv('../data/unit.csv', header=None)

unit_list = list(dataframe[0])

# Add a list of unit
new_unit = ['个/HPF', '/HPF', 'mmHg', '%', 'mmol/dl', 'mmol/L', 'ml/dl', 'g/L', 'mg/dl', '个/μl', '/μl', 'mg/L', 'g/dL', 'mg', 'mmol', 'mg/24h', 'mmol/24h', '个/LPF', '/LPF', 'Ms/cm', '\*10\^9/L', '10\^9/L', '\*10\^12/L', '10\^12/L', 'mm/h', 'μmol/L', 'U/L', 'mU/L', 'pmol/L', 'nmol/L', 'μg/dl', 'S/CO', 'ng/mL', 'mmol/L', '包/天', '根/天', 'PEI U/mL', 'IU/mL', 'mIU/mL', '个', 'umol/L', 'mIU/L', 'mm/60min', 'IU/L', 'ug/dl', 'cm', 'kg', 'kg/m\^2', '℃', '次/分', 'm', 'ng/L', 'U/mL', 'mU/mL', 'L', 'ml', 'dl', 'mL', 'dL', 'μl', 'ul']

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
