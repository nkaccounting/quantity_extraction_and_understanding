from transformers import MarianTokenizer, MarianMTModel

# Paraphrasing-based Generation，通过回译的方法，丰富现有的问句形式，探索是否存在是什事？更加符合natural language的表达形式。
def back_translation(
        sample_text,
        forward='../opus-mt-zh-en',
        backward='../opus-mt-en-zh',
        forward_nums=6,
        backward_nums=4
):
    forward_model = MarianMTModel.from_pretrained(forward)
    forward_tokenizer = MarianTokenizer.from_pretrained(forward)

    batch = forward_tokenizer([sample_text], return_tensors="pt")
    gen = forward_model.generate(**batch, num_return_sequences=forward_nums)
    zh2en = forward_tokenizer.batch_decode(gen, skip_special_tokens=True)

    backward_model = MarianMTModel.from_pretrained(backward)
    backward_tokenizer = MarianTokenizer.from_pretrained(backward)

    batch = backward_tokenizer(zh2en, padding=True, truncation=True, return_tensors="pt")
    gen = backward_model.generate(**batch, num_return_sequences=backward_nums)
    en2zh = backward_tokenizer.batch_decode(gen, skip_special_tokens=True)
    loc = 0
    for i, e2z in enumerate(en2zh):
        if i % backward_nums == 0:
            print()
            print(zh2en[loc])
            loc += 1
        print(e2z)


back_translation('是什事？')
