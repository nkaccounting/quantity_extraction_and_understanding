# quantity_extraction_and_understanding
A project to extract the meaningful quantity in medical area and understand the reference of quantity


基于bert的无微调结果（肯定不行，bert先验不能回答问题）--没必要放上去，但是可以对比
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

基于共指的无微调结果：（共指消解），数据集是onto，coll，ldc，共指的理解还是太单一了
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

Roberta_base（较少mrc）
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
  eval_HasAns_exact      = 48.0851
  eval_HasAns_f1         = 57.2309
  eval_HasAns_total      =     235
  eval_NoAns_exact       =   100.0
  eval_NoAns_f1          =   100.0
  eval_NoAns_total       =       6
  eval_best_exact        = 49.3776
  eval_best_exact_thresh =     0.0
  eval_best_f1           = 58.2957
  eval_best_f1_thresh    =     0.0
  eval_exact             = 49.3776
  eval_f1                = 58.2957
  eval_samples           =     569
  eval_total             =     241

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

如果设置为部分说出答案就把f值标记位1的话：
roberta_wwm（最多的mrc
***** eval metrics *****
  eval_HasAns_exact      = 48.0851
  eval_HasAns_f1         = 93.9686
  eval_HasAns_total      =     235
  eval_NoAns_exact       =   100.0
  eval_NoAns_f1          =   100.0
  eval_NoAns_total       =       6
  eval_best_exact        = 49.3776
  eval_best_exact_thresh =     0.0
  eval_best_f1           = 94.1188
  eval_best_f1_thresh    =     0.0
  eval_exact             = 49.3776
  eval_f1                = 94.1188
  eval_samples           =     569
  eval_total             =     241

macbert_large
***** eval metrics *****
  eval_HasAns_exact      = 49.7872
  eval_HasAns_f1         = 95.3018
  eval_HasAns_total      =     235
  eval_NoAns_exact       = 83.3333
  eval_NoAns_f1          = 83.3333
  eval_NoAns_total       =       6
  eval_best_exact        = 50.6224
  eval_best_exact_thresh =     0.0
  eval_best_f1           = 95.0038
  eval_best_f1_thresh    =     0.0
  eval_exact             = 50.6224
  eval_f1                = 95.0038
  eval_samples           =     568
  eval_total             =     241
说明，基于MRC的方法，无监督就能够把数值的指向说得大差不差了，只是一些表述可能不全面

不想对比，重复数值解决，但一定是更好的

评估MRC好不好，就拿上次讨论班习近平那个例子来测试，初始测试+对抗测试

prompt选取，T5 trick(选取一下)


fine-tune一下
目前先选定robert_wwm
***** eval metrics *****
  epoch                  =     1.0
  eval_HasAns_exact      =  62.069
  eval_HasAns_f1         = 85.7759
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







