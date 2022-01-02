python3.8 run_qa.py \
  --model_name_or_path ./chinese_pretrain_mrc_roberta_wwm_ext_large \
  --validation_file ./data/json/VU_squad2.0_all.json \
  --do_eval\
  --max_seq_length 512 \
  --doc_stride 128 \
  --output_dir ./chinese_pretrain_mrc_roberta_wwm_ext_large\
