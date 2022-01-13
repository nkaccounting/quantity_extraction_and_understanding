import json

from transformers import pipeline

unmasker = pipeline('fill-mask', model='../../bert-base-chinese')

t = unmasker("北京是[MASK]国的首[MASK]")

print(json.dumps(t, indent=4, ensure_ascii=False))

# 等规则抽取比较ok以后再往下进行
