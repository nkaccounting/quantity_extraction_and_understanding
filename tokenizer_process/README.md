## 关于token的实验验证和思考：

第一个样本

    Original str: 1.患者，男性，86岁；2.因“反复便血11月，再发伴乏力3月，腹胀4天。
    Original len: 37
    [101, 122, 119, 2642, 5442, 8024, 4511, 2595, 8024, 8352, 2259, 8039, 123, 119, 1728, 100, 1353, 1908, 912, 6117, 8111, 3299, 8024, 1086, 1355, 845, 726, 1213, 124, 3299, 8024, 5592, 5515, 125, 1921, 511, 102]
    After tokenizer len: 37
    ['[CLS]', '1.', '患', '者', '，', '男', '性', '，', '86', '岁', '；', '2.', '因', '[UNK]', '反', '复', '便', '血', '11', '月', '，', '再', '发', '伴', '乏', '力', '3', '月', '，', '腹', '胀', '4', '天', '。', '[SEP]']
    Original str: 1.患者，男性，86岁；2.因“反复便血11月，再发伴乏力3月，腹胀4天。
    Original len: 37
    [101, 122, 119, 2642, 5442, 8024, 4511, 2595, 8024, 8352, 2259, 8039, 123, 119, 1728, 100, 1353, 1908, 912, 6117, 8111, 3299, 8024, 1086, 1355, 845, 726, 1213, 124, 3299, 8024, 5592, 5515, 125, 1921, 511, 102]
    After tokenizer len: 37
    ['[CLS]', '1.', '患', '者', '，', '男', '性', '，', '86', '岁', '；', '2.', '因', '[UNK]', '反', '复', '便', '血', '11', '月', '，', '再', '发', '伴', '乏', '力', '3', '月', '，', '腹', '胀', '4', '天', '。', '[SEP]']

两个模型的tokenizer基本都没有什么问题

第二个样本：

    Original str: 患者徐妹仙，女，63岁。因 确诊直肠癌11月余 门诊拟直肠癌收入院。入院查体：T36.8℃，P67次/分，R19次/分，BP126/64mmHg
    Original len: 72
    [101, 2642, 5442, 2528, 1987, 803, 8024, 1957, 8024, 8381, 2259, 511, 1728, 4802, 6402, 4684, 5499, 4617, 8111, 3299, 865, 7305, 6402, 2877, 4684, 5499, 4617, 3119, 1057, 7368, 511, 1057, 7368, 3389, 860, 8038, 11291, 8158, 119, 129, 8320, 8024, 158, 9411, 3613, 120, 1146, 8024, 12026, 8160, 3613, 120, 1146, 8024, 12203, 8455, 8158, 120, 8308, 8278, 12207, 102]
    After tokenizer len: 62
    ['[CLS]', '患', '者', '徐', '妹', '仙', '，', '女', '，', '63', '岁', '。', '因', '确', '诊', '直', '肠', '癌', '11', '月', '余', '门', '诊', '拟', '直', '肠', '癌', '收', '入', '院', '。', '入', '院', '查', '体', '：', 't36.', '8℃', '，', 'p67', '次', '/', '分', '，', 'r19', '次', '/', '分', '，', 'bp126', '/', '64mmhg', '[SEP]']
    Original str: 患者徐妹仙，女，63岁。因 确诊直肠癌11月余 门诊拟直肠癌收入院。入院查体：T36.8℃，P67次/分，R19次/分，BP126/64mmHg
    Original len: 72
    [101, 2642, 5442, 2528, 1987, 803, 8024, 1957, 8024, 8381, 2259, 511, 1728, 4802, 6402, 4684, 5499, 4617, 8111, 3299, 865, 7305, 6402, 2877, 4684, 5499, 4617, 3119, 1057, 7368, 511, 1057, 7368, 3389, 860, 8038, 100, 119, 129, 8320, 8024, 100, 3613, 120, 1146, 8024, 100, 3613, 120, 1146, 8024, 100, 120, 100, 102]
    After tokenizer len: 55
    ['[CLS]', '患', '者', '徐', '妹', '仙', '，', '女', '，', '63', '岁', '。', '因', '确', '诊', '直', '肠', '癌', '11', '月', '余', '门', '诊', '拟', '直', '肠', '癌', '收', '入', '院', '。', '入', '院', '查', '体', '：', '[UNK].', '8℃', '，', '[UNK]', '次', '/', '分', '，', '[UNK]', '次', '/', '分', '，', '[UNK]', '/', '[UNK]', '[SEP]']

但是在这里就能明显看出，bert-chinese对于英文字母+数字的处理情况

尤其是bert_base_chinese有很多token在embedding的时候变成了unk，甚至包含了部分数字，这也是导致模型输出不对的问题所在

也有一些输入并不是我们所想的格式，例如T36.和8分开了,出现p67，r19等问题，在这些比较新的模型中会按照子词的方式去处理，但处理成的子词，并不一定是我们所期望的划分

这种错误的分字方式，也会导致后续的分析无法准确

例如：当我们提问36.8度指的是什么的时候，原文只有T36. 8两个token，那模型的输出就会自然而然地输出T36，这也就是之前为什么有很多bug存在的情况

（了解了这种情况以后，再去思考怎么解决中文里面出现英文，并很好地指向英文的情况

引入更多的预训练模型来对比，思考最佳的预训练选择，以及解决方案：

每一组依次是MRC，bert_base，多语言bert，以及MRC的bert

    ['[CLS]', '1.', '患', '者', '，', '男', '性', '，', '86', '岁', '；', '2.', '因', '[UNK]', '反', '复', '便', '血', '11', '月', '，', '再', '发', '伴', '乏', '力', '3', '月', '，', '腹', '胀', '4', '天', '。', '[SEP]']
    ['[CLS]', '1.', '患', '者', '，', '男', '性', '，', '86', '岁', '；', '2.', '因', '[UNK]', '反', '复', '便', '血', '11', '月', '，', '再', '发', '伴', '乏', '力', '3', '月', '，', '腹', '胀', '4', '天', '。', '[SEP]']
    ['[CLS]', '1.', '患', '者', '，', '男', '性', '，', '86', '岁', '；', '2.', '因', '[UNK]', '反', '复', '便', '血', '11', '月', '，', '再', '发', '伴', '乏', '力', '3', '月', '，', '腹', '胀', '4', '天', '。', '[SEP]']
    ['[CLS]', '1.', '患', '者', '，', '男', '性', '，', '86', '岁', '；', '2.', '因', '[UNK]', '反', '复', '便', '血', '11', '月', '，', '再', '发', '伴', '乏', '力', '3', '月', '，', '腹', '胀', '4', '天', '。', '[SEP]']
    
    ['[CLS]', '患', '者', '徐', '妹', '仙', '，', '女', '，', '63', '岁', '。', '因', '确', '诊', '直', '肠', '癌', '11', '月', '余', '门', '诊', '拟', '直', '肠', '癌', '收', '入', '院', '。', '入', '院', '查', '体', '：', 't36.', '8℃', '，', 'p67', '次', '/', '分', '，', 'r19', '次', '/', '分', '，', 'bp126', '/', '64mmhg', '[SEP]']
    ['[CLS]', '患', '者', '徐', '妹', '仙', '，', '女', '，', '63', '岁', '。', '因', '确', '诊', '直', '肠', '癌', '11', '月', '余', '门', '诊', '拟', '直', '肠', '癌', '收', '入', '院', '。', '入', '院', '查', '体', '：', '[UNK].', '8℃', '，', '[UNK]', '次', '/', '分', '，', '[UNK]', '次', '/', '分', '，', '[UNK]', '/', '[UNK]', '[SEP]']
    ['[CLS]', '患', '者', '徐', '妹', '仙', '，', '女', '，', '63', '岁', '。', '因', '确', '诊', '直', '肠', '癌', '11', '月', '余', '门', '诊', '拟', '直', '肠', '癌', '收', '入', '院', '。', '入', '院', '查', '体', '：', 'T36.', '8℃', '，', 'P67', '次', '/', '分', '，', 'R19', '次', '/', '分', '，', 'BP126', '/', '64mmHg', '[SEP]']
    ['[CLS]', '患', '者', '徐', '妹', '仙', '，', '女', '，', '63', '岁', '。', '因', '确', '诊', '直', '肠', '癌', '11', '月', '余', '门', '诊', '拟', '直', '肠', '癌', '收', '入', '院', '。', '入', '院', '查', '体', '：', 't36.', '8℃', '，', 'p67', '次', '/', '分', '，', 'r19', '次', '/', '分', '，', 'bp126', '/', '64mmhg', '[SEP]']
    
    ['[CLS]', '谷', '草', '转', '氨', '酶', '(', 'ast', ')', '16.', '6iu', '/', 'l,', '钾', '(', 'k', '+', ')', '3.', '64mmol', '/', 'l,', '钠', '(', 'na', '+', ')', '142.', '6mmol', '/', 'l,', '磷', '(', 'phos', ')', '1.', '24mmol', '/', 'l,', '[SEP]']
    ['[CLS]', '谷', '草', '转', '氨', '酶', '(', '[UNK]', ')', '16.', '[UNK]', '/', '[UNK],', '钾', '(', '[UNK]', '+', ')', '3.', '64mmol', '/', '[UNK],', '钠', '(', '[UNK]', '+', ')', '142.', '6mmol', '/', '[UNK],', '磷', '(', '[UNK]', ')', '1.', '24mmol', '/', '[UNK],', '[SEP]']
    ['[CLS]', '谷', '草', '转', '氨', '酶', '(', 'AST', ')', '16.', '6IU', '/', 'L,', '钾', '(', 'K', '+', ')', '3.', '64mmol', '/', 'L,', '钠', '(', 'Na', '+', ')', '142.', '6mmol', '/', 'L,', '磷', '(', 'PHOS', ')', '1.', '24mmol', '/', 'L,', '[SEP]']
    ['[CLS]', '谷', '草', '转', '氨', '酶', '(', 'ast', ')', '16.', '6iu', '/', 'l,', '钾', '(', 'k', '+', ')', '3.', '64mmol', '/', 'l,', '钠', '(', 'na', '+', ')', '142.', '6mmol', '/', 'l,', '磷', '(', 'phos', ')', '1.', '24mmol', '/', 'l,', '[SEP]']

分析不难看出，最差的是bert-base，对于英文的处理几乎没有，稍微有一点点字母就会把连带的一些都设置成unk

然后是新版本的这些bert，加入了一些对英文字母的处理

还能接受，但是不够好

    t30mg
    [101, 11291, 13079, 8181, 102]
    ['[CLS]', 't30mg', '[SEP]']
    拆解出来是t3 ##0m ##g这样的子词形式，这样也就能够解释，为什么我们对T37度进行提问的时候会返回T3了

    [101, 162, 8114, 9404, 102]
    ['[CLS]', 't', '30', 'mg', '[SEP]']
    拆解出来是t 30 mg
