import os
import json
import re
import shutil
import argparse
import time

from tencentcloud.common.credential import Credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

# 你的API密钥（需要替换为实际的密钥）
secret_id = "1"
secret_key = "2"

# ANSI escape sequence for red text and reset
RED = "\033[91m"
RESET = "\033[0m"

# 翻译函数
def translate_text(text, source='en', target='zh'):
    try:
        cred = Credential(secret_id, secret_key)
        client = tmt_client.TmtClient(cred, "ap-guangzhou")
        req = models.TextTranslateRequest()
        params = {
            "SourceText": text,
            "Source": source,
            "Target": target,
            "ProjectId": 0
        }
        req.from_json_string(json.dumps(params))
        resp = client.TextTranslate(req)
        return resp.TargetText
    except TencentCloudSDKException as err:
        print(f"{RED}Translation failed: {err}{RESET}")
        return None

# 替换原文中的逗号为英文逗号，并确保逗号后有一个且仅有一个空格
def replace_commas(text):
    text = text.replace('，', ',')
    text = re.sub(r',(\s+)', ',', text)
    return text.strip()

def ensure_unique_output_dir(base_path, dir_name):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = os.path.join(base_path, f"{dir_name}_{timestamp}")
    if os.path.exists(output_dir):
        counter = 1
        while os.path.exists(output_dir):
            output_dir = os.path.join(base_path, f"{dir_name}_{timestamp}_{counter}")
            counter += 1
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def should_ignore_directory(dirname):
    return dirname.startswith("success") or dirname.startswith("error")

def process_directory(root, base_path, success_dir, error_dir):
    for entry in os.listdir(root):
        full_path = os.path.join(root, entry)
        if os.path.isdir(full_path):
            if should_ignore_directory(entry):
                print(f"{RED}Skipping directory: {full_path}{RESET}")
                continue
            else:
                process_directory(full_path, base_path, success_dir, error_dir)  # Recursively process subdirectories
        elif os.path.isfile(full_path) and full_path.endswith(".txt"):
            process_file(full_path, base_path, success_dir, error_dir)

def process_file(file_path, base_path, success_dir, error_dir):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        time.sleep(0.2)  # Wait for 0.2 seconds before making the next request
        translated_content = translate_text(content)
        if translated_content is None:
            raise Exception("Translation failed")
        restored_content = replace_commas(translated_content)
        success_subdir = os.path.relpath(os.path.dirname(file_path), base_path).strip(os.sep)
        success_path = os.path.join(success_dir, success_subdir)
        os.makedirs(success_path, exist_ok=True)
        success_file_path = os.path.join(success_path, os.path.basename(file_path))
        with open(success_file_path, 'w', encoding='utf-8') as file:
            file.write(restored_content)
        print(f"Translated {file_path} successfully.")
    except Exception as e:
        errors.append(file_path)
        error_subdir = os.path.relpath(os.path.dirname(file_path), base_path).strip(os.sep)
        error_path = os.path.join(error_dir, error_subdir)
        os.makedirs(error_path, exist_ok=True)
        error_file_path = os.path.join(error_path, os.path.basename(file_path))
        shutil.copy(file_path, error_file_path)
        print(f"{RED}Error processing {file_path}: {e}{RESET}")

# 批量处理txt文件
def batch_translate(directory):
    global errors  # Declare errors as global to keep track of files that couldn't be translated
    errors = []
    base_path = os.path.abspath(directory)

    success_dir = ensure_unique_output_dir(base_path, "success")
    error_dir = ensure_unique_output_dir(base_path, "error")
    process_directory(base_path, base_path, success_dir, error_dir)  # Start processing from the root directory

    if errors:
        error_list_path = os.path.join(base_path, "error_list.txt")
        with open(error_list_path, 'w', encoding='utf-8') as error_file:
            for error in errors:
                error_file.write(f"{error}\n")
        print(f"{RED}Error list has been saved to {error_list_path}{RESET}")

# 使用示例
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Translate TXT files in a directory.')
    parser.add_argument('directory', type=str, help='The directory containing TXT files to translate.')
    args = parser.parse_args()

    batch_translate(args.directory)