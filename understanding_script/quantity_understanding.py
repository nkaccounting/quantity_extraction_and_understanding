# encoding=utf-8
from quantity_extraction import extract_quantity

if __name__ == '__main__':
    from transformers import AutoTokenizer, AutoModelForQuestionAnswering, QuestionAnsweringPipeline

    tokenizer = AutoTokenizer.from_pretrained('../../chinese_pretrain_mrc_roberta_wwm_ext_large')

    model = AutoModelForQuestionAnswering.from_pretrained('../../chinese_pretrain_mrc_roberta_wwm_ext_large')

    pipeline = QuestionAnsweringPipeline(model=model, tokenizer=tokenizer)

    context = input('请输入：')

    quantities = extract_quantity(context)

    questions = [quantity.value + '指的是？' for quantity in quantities]
    batch = 10
    epoches = len(questions) // batch + 1
    result = []
    for epoch in range(epoches):
        res = pipeline(
            question=questions[epoch*batch:epoch*batch+batch],
            context=context
        )
        if isinstance(res, dict):
            res = [res]
        for i, one_answer in enumerate(res):
            quantity = {
                "Quantity": quantities[i].value,
                "MeasuredProperty": one_answer,
                "Unit": quantities[i].unit,
            }
            result.append(quantity)

    for re in result:
        print(re)
