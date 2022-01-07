import time

from transformers import BertForQuestionAnswering, AutoTokenizer, QuestionAnsweringPipeline

from quantity_extraction import extract_quantity

model = BertForQuestionAnswering.from_pretrained('../fine_tune_mrc_quantity')

tokenizers = AutoTokenizer.from_pretrained('../fine_tune_mrc_quantity')

pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizers)

context = input('输入待验证的文本：')

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
for i, r in enumerate(res):
    print(questions[i], r)

print(t2 - t1)