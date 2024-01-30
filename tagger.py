# img2cap for cogagent-vqa

import os
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, LlamaTokenizer
import argparse
from tqdm import tqdm

# 设置 argparse 参数
parser = argparse.ArgumentParser()
parser.add_argument("--from_pretrained", type=str, default="/exte/CogVLM/models/cogagent-vqa-hf", help='pretrained ckpt')
parser.add_argument("--local_tokenizer", type=str, default="lmsys/vicuna-7b-v1.5", help='tokenizer path')
parser.add_argument("--image_folder", type=str, default="/exte/train/train45/20_ghost_blade", help='Image folder path')
parser.add_argument("--output_folder", type=str, default="/exte/train/train45/output", help='Output folder path')
parser.add_argument("--query_prompt", type=str, default="Describe this image in a very detailed manner", help='')
parser.add_argument("--with_sub_dir", type=bool, default=True, help='sub_dir, output with folder under output_folder')

parser.add_argument("--nouns_tag", type=bool, default=False, help='') # 词组
# parser.add_argument("--nouns_word_tag", type=bool, default=False, help='') # 单词
parser.add_argument("--raw_text", type=bool, default=False, help='') # 句子
parser.add_argument("--print_raw_text", type=bool, default=False, help='') 
parser.add_argument("--print_nouns_tag", type=bool, default=False, help='')
# parser.add_argument("--print_nouns_word_tag", type=bool, default=False, help='')

args = parser.parse_args()
MODEL_PATH =  args.from_pretrained
TOKENIZER_PATH = args.local_tokenizer
IMAGE_FOLDER = args.image_folder
OUTPUT_FOLDER = args.output_folder
with_sub_dir = args.with_sub_dir
query = args.query_prompt
nouns_tag = args.nouns_tag 
raw_text = args.raw_text 
# nouns_word_tag = args.nouns_word_tag

print_raw_text = args.print_raw_text 
print_nouns_tag = args.print_nouns_tag 
# print_nouns_word_tag = args.print_nouns_word_tag

# 检查输出文件夹是否存在，如果不存在则创�??
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
torch_type = torch.bfloat16

# 加载模型和分词器
tokenizer = LlamaTokenizer.from_pretrained(TOKENIZER_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    load_in_4bit=True,
    trust_remote_code=True
).eval()

# 支持的图像格
image_extensions = ['.png', '.jpg', '.jpeg', '.webp']

# 扫描文件夹并筛选图像文件
if not with_sub_dir: 
    image_files = [os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if os.path.splitext(f)[1].lower() in image_extensions]
else: 
    image_files = []
    for root, _, files in os.walk(IMAGE_FOLDER):
        for f in files:
            if os.path.splitext(f)[1].lower() in image_extensions:
                image_files.append(os.path.join(root, f))

remove_tags = [
        'The image portrays ',
        'The image depicts ',
        'The image showcases ', 
        'The overall ambiance of the image is ',
        'and the overall ambiance of the image is ',
        'the overall ambiance of the image suggests ',
        'The overall ambiance of the image suggests ',
        'the overall ambiance of the image is ',
        'A digital artwork of ',
        'a digital artwork of '
]

first_single_spliter = [
    'and',
    'that',
    'which',
    'with',
    'in'
]

# 常见连词的开�?
noun_prefix = [
    'a ',
    'an ',
    'red',
    'pink',
    'purple',
    'green',
    'orange',
    'yellow',
    'blue',
    'black',
    'white',
    'brown',
]

# 名词词库结尾
noun_suffix = [
    'hair',
    'eyes',
    'eye',
    'nose',
    'ear',
    'ears',
    'hands',
    'hand',
    'tied',
    'skirt',
    'shirt',
    'objects',
    'object',
    'tree',
    'trees',
    'cat',
    'dog',
    'fllowers',
    'fllower',
    'sky',
    'star',
    'moon',
    'ribbon',
    'petals',
    'socks',
    'kimono',
    'blouse',
    'colors',
    'bed',
    'uniform',
    'collar',
    'outfit',
    'dress',
    'bra',
    'plants',
    'bikini',
    'hat',
    'bubbles',
    'birds',
    'bird',
    'thong',
    'stockings', 
    'ribbons',
    'ribbon',
    'shoes',
    'creatures',
    'ponytail',
    'couch',
    'belt',
    'helmet',
    'guards',
    'motorcycle', 
    'sword',
    'wings',
    'ring'
]

for image_path in tqdm(image_files, desc="Processing images"):
    image = Image.open(image_path).convert('RGB')
    history = []
    # 构建模型输入
    input_by_model = model.build_conversation_input_ids(tokenizer, query=query, history=history, images=[image])
    inputs = {
        'input_ids': input_by_model['input_ids'].unsqueeze(0).to(DEVICE),
        'token_type_ids': input_by_model['token_type_ids'].unsqueeze(0).to(DEVICE),
        'attention_mask': input_by_model['attention_mask'].unsqueeze(0).to(DEVICE),
        'images': [[input_by_model['images'][0].to(DEVICE).to(torch_type)]],
    }
    if 'cross_images' in input_by_model and input_by_model['cross_images']:
        inputs['cross_images'] = [[input_by_model['cross_images'][0].to(DEVICE).to(torch_type)]]

    # 设置生成参数
    gen_kwargs = {"max_length": 2048, "temperature": 1, "do_sample": False}

    # 生成响应
    res = ""
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        raw_text_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        raw_text_response = raw_text_response.replace("<EOI>Question: " + query + " Answer: ", "")
        raw_text_response = raw_text_response.replace("[INST] " + query + " [/INST]  ", "")
            
        replace_tags = {
            ', possibly ': ' possibly ',
            ', casting ': ' casting ',
            ', including ': ' including ',
            '.':','
        }
        if raw_text:
            # 这里解决，词组，词组，and 词组的做法，这里的词组我们假设最多两个单�?
            response_raw_tagger_arr = raw_text_response.strip().split(", ")
            # print(str(len(response_raw_tagger_arr)))
            # print(response_raw_tagger_arr)

            for single_tagger in response_raw_tagger_arr:
                
                # 判断是不是一个句�?, 超过两个单词就判断它是个句子
                # 如果�? and 开头，直接街上
                ttt = False
                if single_tagger.startswith('and'):
                    replace_tags.update({", and": " and"}) 
                    continue

                single_tagger = single_tagger.split('. ')[0]
                # 只提取第一�?, that which and 等之前的�?
                for i in first_single_spliter:
                    single_1 = single_tagger.split(' ' + i + ' ')[0]
                    if len(single_1) < len(single_tagger):
                        single_tagger = single_1
                    # 开头就是连词的情况，可以合�?
                    if len(single_tagger) == 0:
                        ttt = True

                first_word = single_tagger.split(' ')[0]
                    
                # 排除一些单独的词组成的句子副词和方向词
                if first_word.endswith("ly") or first_word.startswith("in "):
                    continue

                if not ttt:
                    if len(single_tagger.strip(' ').split(' ')) <= 3:
                        ttt = True

                if not ttt:
                    for pre in noun_prefix:
                        if single_tagger.startswith(pre) and len(single_tagger.strip(' ').split(' ')) <= 4:
                            ttt = True
                
                if not ttt:
                    # 名词取法
                    for suf in noun_suffix:
                        # 第一种简�? 比如直接�? xxx hair
                        if single_tagger.endswith(suf) and len(single_tagger.strip(' ').split(' ')) <= 4:
                            ttt = True

                        # 第二种比较难 xxx hair abooed with xxx x这种没过滤出来的
                        # 直接锁定位置
                        if not ttt and single_tagger.find(suf) > -1:
                            single_tagger = single_tagger.strip(' ').split(suf)[0] + suf
                            if len(single_tagger.strip(' ').split(' ')) <= 4:  # 只取简单的长度，防止出�?
                                ttt = True    

                if ttt:
                    re_single_tagger = ' and ' + single_tagger
                    be_single_tagger = ', ' + single_tagger
                    replace_tags.update({f"{be_single_tagger}": re_single_tagger})


            # print(replace_tags)
                
            raw_t = raw_text_response
            for i in remove_tags:
                raw_t = raw_t.replace(i, "")

            for k, v in replace_tags.items():
                raw_t = raw_t.replace(k, v)

            res = raw_t

            if print_raw_text:
                print(f"raw: {raw_t}")

        if nouns_tag and len(res) > 0: 
            # 最多重试三�?
            i = 3
            response_tagger = raw_text_response

            while i > 0:
                if i != 3:
                    print("\n try nouns_tag failed " + str(3-i) +" times, retrying")
                    print(response_tagger.strip().strip("."))
                
                query_text = "Export the noun phrases in the following sentences \n" + response_tagger
    
                input_by_model = model.build_conversation_input_ids(tokenizer, query=query_text, history=history, images=[image])
                inputs = {
                    'input_ids': input_by_model['input_ids'].unsqueeze(0).to(DEVICE),
                    'token_type_ids': input_by_model['token_type_ids'].unsqueeze(0).to(DEVICE),
                    'attention_mask': input_by_model['attention_mask'].unsqueeze(0).to(DEVICE),
                    'images': [[input_by_model['images'][0].to(DEVICE).to(torch_type)]],
                }
                if 'cross_images' in input_by_model and input_by_model['cross_images']:
                    inputs['cross_images'] = [[input_by_model['cross_images'][0].to(DEVICE).to(torch_type)]]
                # 设置生成参数
                gen_kwargs = {"max_length": 2048, "temperature": 1, "do_sample": False}

                with torch.no_grad():
                    outputs = model.generate(**inputs, **gen_kwargs)
                    response_tagger = tokenizer.decode(outputs[0], skip_special_tokens=True)

                    response_tagger = response_tagger.replace("<EOI>Question: " + query_text + " Answer: ", "")
                    response_tagger = response_tagger.replace("[INST] " + query_text + " [/INST]  ", "")

                    response_tagger_arr = response_tagger.split(": ", 1)
                    if len(response_tagger_arr) > 1:
                        response_tagger = response_tagger_arr[1]
                    
                    if print_nouns_tag:
                        print(f"\n nouns tagger: {response_tagger}")

                    # 解决一个bug，如果生成的依旧是句子，重新�?
                    if response_tagger.strip().strip(".").find('.') == -1:
                        i = -10
                        break
                i = i - 1

            if i == -10: 
                # 提取格式 ', '  , 'vast, starry expanse', 'young woman', 'long brown hair', 'black jacket', '76 emblem', 'green drink', 'headphones', 'focused expression', 'convenience store', 'neon sign', 'warning symbol', 'other people walking', and 'urban environment'.
                response_tagger_arr = response_tagger.strip().strip(".").strip("\'").replace("\', and \'", "\', \'").split("\', \'")
                new_response_tagger = ""
                for single_tagger in response_tagger_arr:
                    new_single_tagger = single_tagger.replace(", " , " and ")
                    if len(new_single_tagger) > 0:
                        new_response_tagger = new_response_tagger + ", "  + new_single_tagger
                response_tagger = new_response_tagger.strip(", ")
                
                res = res + ' ' + response_tagger


    # 打印响应
    print(f"\n{image_path}: {res}")

    # 保存响应到指定的输出目录
    output_file_name = os.path.splitext(os.path.basename(image_path))[0] + ".txt"
    tmp_output_file_path = image_path.replace(IMAGE_FOLDER, OUTPUT_FOLDER)
    output_file_dir = os.path.dirname(tmp_output_file_path)
    if not os.path.exists(output_file_dir):
        os.makedirs(output_file_dir)
    
    output_file_path = os.path.join(output_file_dir, output_file_name)
    print(output_file_path)

    with open(output_file_path, "w") as file:
        file.write(res)

    history.append((query, res))
