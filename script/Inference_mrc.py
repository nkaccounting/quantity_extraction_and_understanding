import time

from transformers import BertForQuestionAnswering, AutoTokenizer, QuestionAnsweringPipeline

from pre_process_for_text import pre_process
from quantity_extraction import extract_quantity

model = BertForQuestionAnswering.from_pretrained('../fine_tune_mrc_quantity')

tokenizers = AutoTokenizer.from_pretrained('../fine_tune_mrc_quantity')

pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizers)

context = input('输入待验证的文本：')

context = pre_process(context)

Quantities = extract_quantity(context)

quantities = [Q.value for Q in Quantities]

print(quantities)

context = [context] * len(quantities)

questions = ['{quantity}指的是？'.format(quantity=q) for q in quantities]

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
