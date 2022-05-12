# 快速补充未完善的单位
import pandas as pd

dataframe = pd.read_csv('../data/unit.csv', header=None)

unit_list = list(dataframe[0])

new_unit = input('Add a new unit (hint for * . ? + ^ $ | \ / [ ] ( ) { }ect:')

if new_unit in unit_list:
    print('The unit already exists！')
else:
    unit_list.append(new_unit)
    unit_list.sort(key=lambda x: len(x), reverse=True)

new_unit_list = pd.Series(unit_list)
new_unit_list.to_csv('../data/unit.csv', header=None, index=0)
