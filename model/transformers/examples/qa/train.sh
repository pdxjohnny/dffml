dffml train \
  -model qa_model \
  -model-model_type bert \
  -model-save_steps 3 \
  -model-model_name_or_path bert-base-cased \
  -model-directory qamodel/checkpoints \
  -model-cache_dir qamodel/cache \
  -model-log_dir qamodel/log \
  -sources s=op \
  -source-opimp dffml_model_transformers.qa.utils:parser \
  -source-args train.json True \
  -log debug