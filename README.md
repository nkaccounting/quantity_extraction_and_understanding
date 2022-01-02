# quantity_extraction_and_understanding
A project to extract the meaningful quantity in medical area and understand the reference of quantity


基于bert的无微调结果（肯定不行，bert先验不能回答问题，相当于纯蒙）--没必要放上去，但是可以对比
***** eval metrics *****
  eval_HasAns_exact      =    0.0
  eval_HasAns_f1         = 2.4187
  eval_HasAns_total      =    235
  eval_NoAns_exact       =    0.0
  eval_NoAns_f1          =    0.0
  eval_NoAns_total       =      6
  eval_best_exact        = 2.4896
  eval_best_exact_thresh =    0.0
  eval_best_f1           = 2.8257
  eval_best_f1_thresh    =    0.0
  eval_exact             =    0.0
  eval_f1                = 2.3585
  eval_samples           =    568
  eval_total             =    241

基于共指（只选择了预指和回指）的无微调结果：（共指消解），数据集是ontonotes-release-5.0共指的理解还是太单一了
该数据集可能涉及到版权问题，北大是否有版权使用？
***** eval metrics *****
  eval_HasAns_exact      =  8.5106
  eval_HasAns_f1         =  8.8298
  eval_HasAns_total      =     235
  eval_NoAns_exact       =   100.0
  eval_NoAns_f1          =   100.0
  eval_NoAns_total       =       6
  eval_best_exact        = 10.7884
  eval_best_exact_thresh =     0.0
  eval_best_f1           = 11.0996
  eval_best_f1_thresh    =     0.0
  eval_exact             = 10.7884
  eval_f1                = 11.0996
  eval_samples           =     569
  eval_total             =     241


……不断加大MRC的数据集（//换用不同的MRC来做，等效于我换了不同的数据集--具体数据体量在github上搜一下）

Roberta_base（较少mrc）--等效共指的效果
***** eval metrics *****
  eval_HasAns_exact      =   6.383
  eval_HasAns_f1         =  8.3267
  eval_HasAns_total      =     235
  eval_NoAns_exact       = 83.3333
  eval_NoAns_f1          = 83.3333
  eval_NoAns_total       =       6
  eval_best_exact        =  8.2988
  eval_best_exact_thresh =     0.0
  eval_best_f1           = 10.1941
  eval_best_f1_thresh    =     0.0
  eval_exact             =  8.2988
  eval_f1                = 10.1941
  eval_samples           =     568
  eval_total             =     24

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

macbert_large（这两个都是比较多的，是相同的数据体量，不同的架构，
***** eval metrics *****
  eval_HasAns_exact      = 49.7872
  eval_HasAns_f1         = 60.9253
  eval_HasAns_total      =     235
  eval_NoAns_exact       = 83.3333
  eval_NoAns_f1          = 83.3333
  eval_NoAns_total       =       6
  eval_best_exact        = 50.6224
  eval_best_exact_thresh =     0.0
  eval_best_f1           = 61.4832
  eval_best_f1_thresh    =     0.0
  eval_exact             = 50.6224
  eval_f1                = 61.4832
  eval_samples           =     568
  eval_total             =     241


(小bug，不能把无监督的时候no answer放进来，无监督的时候no answer特别多，我们还是要它尽可能输出)
当时设置成[] in answer，无答案直接标成1的f值了，导致虚高，没有的事
说明P值十分高：

说明，基于MRC的方法，无监督就能够把数值的指向说得大差不差了，只是一些表述可能不全面
往往是：比如说患高血压4年，然后抽取出高血压，患字抽不出来，但是我准备的标准答案是带有患字的


不想对比-重复数值解决，但一定是更好的

评估MRC好不好，就拿上次讨论班习近平那个例子来测试，初始测试+对抗测试

prompt选取，T5 trick(选取一下)

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
***** eval metrics *****
  epoch                  =     1.0
  eval_HasAns_exact      =  62.069（理论上比这个还要更高）
  eval_HasAns_f1         = 85.7759（可能是bug，重新看一看）
  eval_HasAns_total      =      29
  eval_best_exact        =  62.069
  eval_best_exact_thresh =     0.0
  eval_best_f1           = 85.7759
  eval_best_f1_thresh    =     0.0
  eval_exact             =  62.069
  eval_f1                = 85.7759
  eval_samples           =      50
  eval_total             =      29


***** eval metrics *****
  epoch                  =     2.0
  eval_HasAns_exact      =  62.069
  eval_HasAns_f1         = 77.5862
  eval_HasAns_total      =      29
  eval_best_exact        =  62.069
  eval_best_exact_thresh =     0.0
  eval_best_f1           = 77.5862
  eval_best_f1_thresh    =     0.0
  eval_exact             =  62.069
  eval_f1                = 77.5862
  eval_samples           =      50
  eval_total             =      29





为啥我自己电脑上的无监督效果比在实验室服务器上的更好？（拷贝

PRF,不用想都是P值特别高，R比较小，整体的F一般


几件事情：
目前的条件还不允许做，不可回答问题，去理解无效数值（可以写成一些思想，如果有更多的数据集，或者在fine-tune结束以后再看看支持2.0的情况

如果做1.1版本的话
run_qa里面的metric修改为squad，改import；修改2.0-1.1（也许不用）
eval里面，空格分隔转list ch分隔


前面的无监督的结果，是拿2.0做的，就会导致
原本尽力说答案会说出来，但是强行转no answer了



