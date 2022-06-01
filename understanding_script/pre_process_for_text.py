# 需要对文本进行预处理
import re


def better_tokenizer_pre_process(text: str):
    ans = ''
    for i in range(len(text) - 1):
        if (text[i + 1].isdigit() and text[i].encode('utf-8').isalpha()) or (
                text[i].isdigit() and text[i + 1].encode('utf-8').isalpha()) or (
                text[i] == "℃" and text[i + 1].encode('utf-8').isalpha()):
            ans += text[i]
            ans += ' '
        else:
            ans += text[i]
    ans += text[-1] if text else ''
    return ans


def removeTime(text: str):
    # 去除三个包含日期的表述，2022年1月11日；2022年1月；1月11日
    # 保留余下的，例如单独的患高血压4年，腹泻4日，心律不齐11月这样的描述
    mode = [
        '\d+年\d+月\d+日',
        '\d+年\d+月',
        '\d+月\d+日',
        '\d+时\d+分',
        '\d+时?[:：]\d+分'
    ]
    pattern = "|".join(mode)
    text = re.sub(pattern, '##', text)
    text = re.sub('\"', '', text)
    return re.sub(pattern, '##', text)


def pre_process(text: str):
    text = str(text)
    text = removeTime(text)
    return text + '=。'


def after_process(text: str):
    text = better_tokenizer_pre_process(text)
    return text


def history_process(text: str):
    text = str(text)
    text = "。" + text + "。"
    text = re.sub("\"|“|”", "", text)
    text = re.sub("（|）", " ", text)
    return text


if __name__ == '__main__':
    print(better_tokenizer_pre_process('患者因便血约3月门急诊拟 直肠癌入院。入院查体:T36.4℃,P82次/分,R20次/分,BP152/55mmHg'))
    print(removeTime('1月11日患者因便血约3月门急诊拟 直肠癌入院。入院查体:T36.4℃,P82次/分,R20次/分,BP152/55mmHg，例如单独的患高血压4年，腹泻4日，心律不齐11月这样的描述'))
    print(pre_process('1月11日患者因便血约3月门急诊拟 直肠癌入院。入院查体:T:36.4℃,P82次/分,R20次/分,BP152/55mmHg，例如单独的患高血压4年，腹泻4日，心律不齐11月这样的描述'))
