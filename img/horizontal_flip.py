from PIL import Image
import os
import re
import shutil
import argparse

def get_max_number(dir_path):
    existing_numbers = set()
    existing_files = os.listdir(dir_path)
    for file_name in existing_files:
        match = re.match(r'(\d+)\.(jpg|png|jpeg|bmp)', file_name)
        if match:
            existing_numbers.add(int(match.group(1)))
    existing_numbers = sorted(existing_numbers)
    return existing_numbers[-1] + 1 if existing_numbers else 1

def sorted_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def flip_images(input_dir, output_dir=None):
    if not output_dir:
        output_dir = input_dir

    os.makedirs(output_dir, exist_ok=True)

    max_number_input = get_max_number(input_dir)
    max_number_output = get_max_number(output_dir)
    start_number = max(max_number_input, max_number_output)

    files = os.listdir(input_dir)
    files = sorted_nicely(files)

    for file_name in files:
        image_path = os.path.join(input_dir, file_name)
        if os.path.isfile(image_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            try:
                image = Image.open(image_path)
            except Exception as e:
                print(f"Failed to read image: {image_path} - {e}")
                continue

            flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)

            image_name, image_ext = os.path.splitext(file_name)
            new_image_number = start_number
            new_image_name = f"{new_image_number}{image_ext}"
            new_image_path = os.path.join(output_dir, new_image_name)
            
            flipped_image.save(new_image_path)

            txt_file = os.path.join(input_dir, f"{image_name}.txt")
            if os.path.exists(txt_file):
                new_txt_file = os.path.join(output_dir, f"{new_image_number}.txt")
                shutil.copyfile(txt_file, new_txt_file)

            print(f"Flipped image saved at: {new_image_path}")
            start_number += 1


# 使用 argparse 解析输入参数
def non_empty_string(s):
    if s.strip() == "":
        raise argparse.ArgumentTypeError("Argument must be a non-empty string")
    return s

parser = argparse.ArgumentParser(description='Process some images.')
parser.add_argument('input_dir', type=str, help='input directory path')
parser.add_argument('output_dir', nargs='?', type=non_empty_string, default=None, help='output directory path (default: same as input directory)')
args = parser.parse_args()

output_dir = args.output_dir if args.output_dir else args.input_dir

print(f"Input directory: {args.input_dir}")
print(f"Output directory: {output_dir}")
# 调用函数处理图片
flip_images(args.input_dir, args.output_dir)
