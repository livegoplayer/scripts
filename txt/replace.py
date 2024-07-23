import os
import argparse
import re

def batch_replace_text(directory, find_text, replace_text):
    """
    递归地在指定目录及其子文件夹中的所有文本文件中搜索并替换文本。

    :param directory: 要搜索的根目录路径。
    :param find_text: 需要被替换的文本。
    :param replace_text: 用于替换的文本。
    """
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # 确保只处理文本文件
            if filename.endswith(".txt"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # 使用正则表达式替换文本，考虑可能的换行符
                pattern = re.compile(re.escape(find_text), re.MULTILINE)
                new_content = pattern.sub(replace_text, content)

                # 只有在内容发生改变时才写回文件
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    print(f"Updated file: {file_path}")
                else:
                    print(f"No changes made to file: {file_path}")

def main():
    parser = argparse.ArgumentParser(description='Batch replace text in text files.')
    parser.add_argument('directory', type=str, help='The directory to search in.')
    parser.add_argument('find_text', type=str, help='The text to find and replace.')
    parser.add_argument('replace_text', type=str, help='The text to replace with.')
    args = parser.parse_args()

    batch_replace_text(args.directory, args.find_text, args.replace_text)

if __name__ == "__main__":
    main()