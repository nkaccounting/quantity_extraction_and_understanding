# quantity_extraction_and_understanding
A project to extract the meaningful quantity in medical area and understand the reference of quantity


基于bert的无微调结果（肯定不行，bert先验不能回答问题，相当于纯蒙）--没必要放上去，但是可以对比,作为无监督的base起点
***** eval metrics *****
  eval_P           = 1.8565
  eval_R           = 5.4526
  eval_exact_match =    0.0
  eval_f1          = 2.3776
  eval_samples     =    559

基于共指（只选择了预指和回指）的无微调结果：（共指消解），数据集是ontonotes-release-5.0共指的理解还是太单一了
该数据集可能涉及到版权问题，北大是否有版权使用？（后续还需要进一步验证该过程，prompt不一致）
***** eval metrics *****
  eval_P           = 54.5677
  eval_R           = 55.2119
  eval_exact_match = 37.8723
  eval_f1          = 50.9436
  eval_samples     =     560


……不断加大MRC的数据集（//换用不同的MRC来做，等效于我换了不同的数据集--具体数据体量在github上搜一下）

Roberta_base（较少mrc）--不及共指的效果
***** eval metrics *****
  eval_P           =  36.186
  eval_R           = 33.7209
  eval_exact_match = 22.9787
  eval_f1          = 33.4211
  eval_samples     =     559

（MRC的终点）
基于MRC的无微调结果（带重复数值解决方案-

roberta_wwm（最多的mrc
***** eval metrics *****
  eval_P           = 71.4912
  eval_R           = 80.3706
  eval_exact_match = 56.5957
  eval_f1          = 71.5788
  eval_samples     =     560
（注意：在1.1的评价体系下不要带为空的list）

macbert_large（这两个都是比较多的，是相同的数据体量，不同的架构）最后还是保留roberta_wwm
***** eval metrics *****
  eval_P           = 72.3288
  eval_R           = 80.4419
  eval_exact_match =  53.617
  eval_f1          =  71.503
  eval_samples     =     559


(小bug，不能把无监督的时候no answer放进来，无监督的时候no answer特别多，我们还是要它尽可能输出)
当时设置成[] in answer，无答案直接标成1的f值了，导致虚高，没有的事

说明，基于MRC的方法，无监督就能够把数值的指向说得大差不差了，只是一些表述可能不全面
往往是：比如说患高血压4年，然后抽取出高血压，患字抽不出来，但是我准备的标准答案是带有患字的


评估MRC好不好，就拿上次讨论班习近平那个例子来测试，初始测试+对抗测试（自己的小想法）

prompt选取，T5 trick(选取一下)

目前只能人造

重复数值解决：
4种方案，在所有工作调优，调整到最优以后，对比4种方案

划分好的eval太难了，简单的都拿去训练了，后面看看怎么调一下
注意公平比较，我后半段选取的eval是比较难的数据集？？？
那怎么样才能公平比较呢？
国新那边能否提供1~2条数据作为我的evaluation
本身还是很难的

fair comparison的微调起点，选的样本相对平均水平更难一些
***** eval metrics *****
  eval_P           =  59.171(平均的PR算出来不是平均的F一致的)
  eval_R           = 59.4417
  eval_exact_match = 41.3793
  eval_f1          = 56.4711
  eval_samples     =      50

fine-tune一下
目前先选定robert_wwm

因为是两个核，batch相当于是乘2的

batch size=4 epoch=1
***** eval metrics *****
  epoch            =     1.0
  eval_P           = 83.5617
  eval_R           = 91.2931
  eval_exact_match = 72.4138
  eval_f1          = 84.7048
  eval_samples     =      50

batch size=8 epoch=1
***** eval metrics *****
  epoch            =     1.0
  eval_P           = 84.0805
  eval_R           =  89.569
  eval_exact_match = 68.9655
  eval_f1          = 84.9343
  eval_samples     =      50

batch size=4 epoch=2
***** eval metrics *****
  epoch            =     2.0
  eval_P           = 84.9138
  eval_R           = 85.0123
  eval_exact_match = 68.9655
  eval_f1          = 83.8218
  eval_samples     =      50

batch size=8 epoch=2
***** eval metrics *****
  epoch            =     2.0
  eval_P           = 77.8448
  eval_R           = 80.8251
  eval_exact_match =  62.069
  eval_f1          = 77.2701
  eval_samples     =      50

batch size=4 epoch=3
***** eval metrics *****
  epoch            =     3.0
  eval_P           = 77.4904
  eval_R           = 79.7783
  eval_exact_match = 68.9655
  eval_f1          = 77.8803
  eval_samples     =      50

batch size=8 epoch=3
***** eval metrics *****
  epoch            =     3.0
  eval_P           = 78.3621
  eval_R           = 82.3276
  eval_exact_match = 65.5172
  eval_f1          = 79.5115
  eval_samples     =      50

batch size=8 epoch=10
***** eval metrics *****
  epoch            =    10.0
  eval_P           = 77.2686
  eval_R           = 82.6355
  eval_exact_match = 68.9655
  eval_f1          = 78.2393
  eval_samples     =      50


由于自己的训练样本真的太少了，自己的训练策略也比较一般，如果单一的数据训练多了，就容易导致过拟合/数据遗忘之前的知识，导致随着轮数的增加，效果反而不行了


几件事情：
目前的条件还不允许做，不可回答问题，去理解无效数值（可以写成一些思想，如果有更多的数据集，或者在fine-tune结束以后再看看支持2.0的情况
基线base差不多了，拿base去造大量的数据（虽然有错的部分，但是错的只是小部分），大量数据作为hasAns，混和上人工添加的一部分no answer（难以用规则覆盖上游 不抽取）

如果做1.1版本的话
run_qa里面的metric修改为squad，改import；修改2.0-1.1（也许不用）

前面的无监督的结果，是拿2.0做的，就会导致
原本尽力说答案会说出来，但是强行转no answer了，从而使得准确率大幅度下降


拿fine-tune过一轮的结果去重新跑之前的项目
