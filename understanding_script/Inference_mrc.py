import time

import torch
from transformers import BertForQuestionAnswering, AutoTokenizer, QuestionAnsweringPipeline

from pre_process_for_text import pre_process, after_process
from quantity_extraction import extract_quantity

model_dir = '../whatisit'
# model_dir = '../../chinese_pretrain_mrc_roberta_wwm_ext_large'

model = BertForQuestionAnswering.from_pretrained(model_dir)

tokenizers = AutoTokenizer.from_pretrained(model_dir)

if torch.cuda.is_available():
    pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizers, device=0)
else:
    pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizers)

context = input('输入待验证的文本：')

context = pre_process(context)

Quantities = extract_quantity(context)

context = after_process(context)

quantities = [after_process(Q.value) for Q in Quantities]

print(quantities)

context = [context] * len(quantities)

questions = ['如果你觉得可能有多个答案的时候找最近的那个，{quantity}是什事？'.format(quantity=q) for q in quantities]

print(questions)

t1 = time.time()
res = pipeline(
    question=questions,
    context=context,
)
t2 = time.time()

res = [res] if isinstance(res, dict) else res

for i, r in enumerate(res):
    print(quantities[i], r['answer'], r['score'])

print(t2 - t1)
