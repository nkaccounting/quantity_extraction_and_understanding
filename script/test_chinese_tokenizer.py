from transformers import BertTokenizer

tokenizer_list = [
    BertTokenizer.from_pretrained('../../chinese_pretrain_mrc_roberta_wwm_ext_large'),
    BertTokenizer.from_pretrained('../../bert-base-chinese'),
    BertTokenizer.from_pretrained('../../bert-base-multilingual-cased'),
    BertTokenizer.from_pretrained('../../chinese-roberta-wwm-ext-large')
]


def print_token_info(input_str: str, tokenizer):
    # print('Original str:', input_str)
    # print('Original len:', len(input_str))

    sample1 = tokenizer.encode(input_str)
    print(sample1)
    # print('After tokenizer len:', len(sample1))

    tokenizer_sample1 = tokenizer.decode(sample1)
    print(tokenizer_sample1.split(' '))


test_str = [
    '1.患者，男性，86岁；2.因“反复便血11月，再发伴乏力3月，腹胀4天。',
    '患者徐妹仙，女，63岁。因 确诊直肠癌11月余 门诊拟直肠癌收入院。入院查体：T：36.8℃，P 67次/分，R 19次/分，BP 126/64 mmHg',
    '谷草转氨酶(AST) 16.6 IU/L,钾(K+) 3.64 mmol/L,钠(Na+) 142.6 mmol/L,磷(PHOS) 1.24 mmol/L,剂量为30mg每天my baby,hello bathgate',
    'T30mg',
    'T 30 mg'
]

for text in test_str:
    for tokenizer in tokenizer_list:
        print_token_info(text, tokenizer)
    print()

tokenizer=BertTokenizer.from_pretrained('../../chinese-roberta-wwm-ext-large')

# t3
# ##0m
# ##g
print(tokenizer.decode([11291]))
print(tokenizer.decode([13079]))
print(tokenizer.decode([8181]))

# t
# 30
# mg
print(tokenizer.decode([162]))
print(tokenizer.decode([8114]))
print(tokenizer.decode([9404]))
