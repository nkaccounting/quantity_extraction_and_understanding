from transformers import pipeline

unmasker = pipeline('fill-mask', model='../../bert-base-chinese')

analysis = '中国的首都是[MASK][MASK]。我爱这个城市。'

res = unmasker(analysis)

for r in res:
    for rr in r:
        print(rr)

# {'score': 0.3788018226623535, 'token': 1266, 'token_str': '北', 'sequence': '[CLS] 中 国 的 首 都 是 北 [MASK] 。 我 爱 这 个 城 市 。 [SEP]'}
# {'score': 0.4389030933380127, 'token': 776, 'token_str': '京', 'sequence': '[CLS] 中 国 的 首 都 是 [MASK] 京 。 我 爱 这 个 城 市 。 [SEP]'}
print()

analysis = '中国的首都是[MASK][MASK]。'

res = unmasker(analysis)

for r in res:
    for rr in r:
        print(rr)
# {'score': 0.5172104835510254, 'token': 1266, 'token_str': '北', 'sequence': '[CLS] 中 国 的 首 都 是 北 [MASK] 。 [SEP]'}
# {'score': 0.534919261932373, 'token': 776, 'token_str': '京', 'sequence': '[CLS] 中 国 的 首 都 是 [MASK] 京 。 [SEP]'}
print()

analysis = '中国的首都是[MASK][MASK]'

res = unmasker(analysis)

for r in res:
    for rr in r:
        print(rr)
# {'score': 0.2685059607028961, 'token': 1525, 'token_str': '哪', 'sequence': '[CLS] 中 国 的 首 都 是 哪 [MASK] [SEP]'}
# {'score': 0.8627076148986816, 'token': 8043, 'token_str': '？', 'sequence': '[CLS] 中 国 的 首 都 是 [MASK] ？ [SEP]'}
