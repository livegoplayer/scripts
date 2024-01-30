#!/bin/bash
bash /mnt/workspace/trojan/run.sh
service privoxy restart

export http_proxy=http://127.0.0.1:8893
export https_proxy=http://127.0.0.1:8893
export no_proxy="localhost, 127.0.0.1, ::1, ip.cn, chinaz.com, 192.168.0.0/16"

# tagger script by @milk
# Train data path
model_dir="/ext/CogVLM/models/cogagent-vqa-hf" # model dir path | 本地模型文件夹路�?

tokenizer="lmsys/vicuna-7b-v1.5" # huggingface模型repoID || 本地缓存目录,本地没缓存就不用�?

image_folder="/ext/train/train11" #  input images path | 图片输入路径

output_folder="/ext/train/train11" # 输出目录 | 如果不指定输出目录，则输出到图片目录

with_sub_dir=1

xl_prompt="Describe this image in a very detailed manner."

query_prompt="$xl_prompt"

raw_text=1

nouns_tag=1

# nouns_word_tag=0

print_raw_text=1

print_nouns_tag=1

# print_nouns_word_tag=0

# Activate python venv
if [ -d "venv/bin/" ];then
  source "venv/bin/activate"
fi

export HF_HOME="huggingface"

if [[ $image_folder == "" ]]; then
  echo "img folder is must $image_folder";
  exit ;
fi


if [[ $model_dir == "" ]]; then
  echo "model folder is must $model_dir";
  exit ;
fi

# if not specify 
if [[ $output_folder == ""  ]]; then
  $output_folder=$image_folder
fi

# default value
if [[ $query_prompt == "" ]]; then
  $query_prompt="Describe this image in a very detailed manner"
fi

# run tagger

echo """accelerate launch --num_cpu_threads_per_process=8 "./tagger.py" \
  --from_pretrained=$model_dir \
  --local_tokenizer=$tokenizer \
  --image_folder=$image_folder \
  --output_folder=$output_folder \
  --nouns_tag=$nouns_tag \
  --raw_text=$raw_text \
  --print_raw_text=$print_raw_text \
  --print_nouns_tag=$print_nouns_tag \
  --query_prompt="$query_prompt" \ 
  --with_sub_dir=$with_sub_dir"""

accelerate launch --num_cpu_threads_per_process=8 "./tagger.py" \
  --from_pretrained="$model_dir" \
  --local_tokenizer=$tokenizer \
  --image_folder="$image_folder" \
  --output_folder="$output_folder" \
  --nouns_tag=$nouns_tag \
  --raw_text=$raw_text \
  --print_raw_text=$print_raw_text \
  --print_nouns_tag=$print_nouns_tag \
  --query_prompt="$query_prompt" \
  --with_sub_dir=$with_sub_dir

echo "Tagger finished "
