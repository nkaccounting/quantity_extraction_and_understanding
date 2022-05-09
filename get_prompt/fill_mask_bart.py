from transformers import BertTokenizer, BartForConditionalGeneration, Text2TextGenerationPipeline

tokenizer = BertTokenizer.from_pretrained("../../bart-base-chinese-cluecorpussmall")
model = BartForConditionalGeneration.from_pretrained("../../bart-base-chinese-cluecorpussmall")
text2text_generator = Text2TextGenerationPipeline(model, tokenizer)
a = text2text_generator("未闻及干湿性啰音，心率83次/分。83次/分[MASK]？心 率", max_length=50, do_sample=False)

print(a)
# [{'generated_text': '83 次 / 分 是 什 么 ？ 心 率 未 闻 及 干 湿 性 啰 音 ， 心 率 83 次 / 分 。'}]


a = text2text_generator("未闻及干湿性啰音，心率83次/分。问题：83次/分是什么？答案：[MASK]", max_length=50, do_sample=False)

print(a)
