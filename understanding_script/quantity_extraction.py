# encoding=utf-8
import re
from collections import Counter

import pandas as pd

dataframe = pd.read_csv('../data/unit.csv', header=None)

unit_list = list(dataframe[0])

base_mode = [
    '0\.?\d*',  # 0.35 mode
    '[1-9]\d*\.?\d*',  # normal digital mode
]

# quantity mode
quantity_mode = [
                    base_mode[0] + '\*?' + base_mode[0] + '\*?' + base_mode[0],
                    base_mode[1] + '\*?' + base_mode[1] + '\*?' + base_mode[1],  # 3*4*5cm mode
                    base_mode[0] + '\*?' + base_mode[0],
                    base_mode[1] + '\*?' + base_mode[1],  # 3*4cm mode
                    base_mode[0] + '×?' + base_mode[0] + '×?' + base_mode[0],
                    base_mode[1] + '×?' + base_mode[1] + '×?' + base_mode[1],  # 3*4*5cm mode
                    base_mode[0] + '×?' + base_mode[0],
                    base_mode[1] + '×?' + base_mode[1],  # 3*4cm mode
                    base_mode[0] + '-?' + base_mode[0],
                    base_mode[1] + '-?' + base_mode[1],  # 6-7次/分 mode
                    base_mode[0] + '-?' + base_mode[1],  # 0-7次/分 mode,
                    base_mode[0] + '/?' + base_mode[0],
                    base_mode[1] + '/?' + base_mode[1],  # 159/87mmHg mode,
                    base_mode[0] + '/?' + base_mode[1],  # 0/87mmHg mode
                ] + base_mode


class Quantity:
    def __init__(self, num, interval, unit):
        self.value = num + interval + unit
        self.num = num
        self.interval = interval
        self.unit = unit


def extract_quantity(text: str):
    unit_pattern = '(' + '|'.join(unit_list) + ')'
    quantity_pattern = '|'.join(quantity_mode)
    nums = re.findall('(' + quantity_pattern + ')([ ]*)' + unit_pattern, text)
    return [Quantity(num[0], num[1], num[2]) for num in nums]


if __name__ == '__main__':
    all = extract_quantity(input())
    print(len(all))
    quantities=[quantity.value for quantity in all]
    for quantity in quantities:
        print(quantity)
    print(Counter(quantities))
