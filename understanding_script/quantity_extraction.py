# encoding=utf-8
import re
from collections import Counter

import pandas as pd

dataframe = pd.read_csv('../data/unit.csv', header=None)

unit_list = list(dataframe[0])

situation = ["阳性", "弱阳性", "阴性"]

symbol = ["\+", "±", "-"]

base_mode = [
    '0\.?\d*',  # 0.35 mode
    '[1-9]\d*\.?\d*',  # normal digital mode
]

middle = ['\*?', '×?', 'x?', '-?', '/?', '~?']

# quantity mode
quantity_mode = [base_mode[0] + m + base_mode[0] for m in middle] \
                + [base_mode[0] + m + base_mode[1] for m in middle] \
                + [base_mode[1] + m + base_mode[1] for m in middle] \
                + base_mode


class Quantity:
    def __init__(self, num, interval, unit):
        self.value = num + interval + unit
        self.num = num
        self.interval = interval
        self.unit = unit


def extract_quantity(text: str):
    unit_pattern = '(' + '|'.join(unit_list) + ')'
    quantity_pattern = '|'.join(quantity_mode)
    nums = re.findall('(' + quantity_pattern + ')([ ]||\+)' + unit_pattern, text)

    unit_no_num_pattern = '([\(（][' + ''.join(symbol) + ']*[\)）])'
    quantity_no_num_pattern = '(' + "|".join(situation) + ')'
    nums_no_num = re.findall(quantity_no_num_pattern + unit_no_num_pattern, text)
    nums_no_num = [(num[0] + num[1], '', '') for num in nums_no_num]

    nums = nums + nums_no_num
    return [Quantity(num[0], num[1], num[2]) for num in nums]


if __name__ == '__main__':
    all = extract_quantity(input())
    print(len(all))
    quantities = [quantity.value for quantity in all]
    for quantity in quantities:
        print(quantity)
    print(Counter(quantities))
