import os
import subprocess
import random
import string
import argparse
import shutil
import re

def run_ffmpeg_command(cmd_parts):
    # Print several empty lines for spacing
    print("\n\n\n")
    
    # Print the FFmpeg command
    print("FFmpeg command:")
    print(" ".join(cmd_parts))
    
    # Execute the FFmpeg command
    subprocess.run(cmd_parts, shell=True)
    
    # Print several empty lines for spacing
    print("\n\n\n")

def validate_time_format(time_str, allow_milliseconds=True):
    if time_str is None:
        return None
    try:
        if allow_milliseconds:
            # Check if time_str matches the format HH:MM:SS.MMM or HH:MM:SS
            if not re.match(r'^\d{1,2}:\d{2}:\d{2}(\.\d{3})?$', time_str):
                raise ValueError()
        else:
            # Check if time_str matches the format HH:MM:SS
            if not re.match(r'^\d{1,2}:\d{2}:\d{2}$', time_str):
                raise ValueError()
        return time_str
    except ValueError:
        print('Error: Invalid time format. Time format should be "H:MM:SS.MMM" or "H:MM:SS" (without milliseconds).')
        exit(1)

def validate_time_if_provided(time_str):
    if time_str is not None:
        return validate_time_format(time_str)


parser = argparse.ArgumentParser(description='Process video files.')
parser.add_argument('--input_folder', type=str, default='input', help='Path to the input folder containing video files.')
parser.add_argument('--output_folder', type=str, default=None, help='Path to the output folder for processed video files. If not provided, an "output" folder will be created in the immediate subdirectory of the input folder.')
parser.add_argument('--start_time', type=str, default=None, help='Start time for trimming in the format "HH:MM:SS:MMM". If not provided, no trimming will be performed.')
parser.add_argument('--end_time', type=str, default=None, help='End time for trimming in the format "HH:MM:SS:MMM". If not provided, no trimming will be performed.')
args = parser.parse_args()

input_folder = args.input_folder
if input_folder is None or not os.path.exists(input_folder):
    print('Error: Input folder does not exist.')
    parser.print_help()
    exit(1)

if args.output_folder is None:
    output_folder = os.path.join(input_folder, 'output')
else:
    output_folder = args.output_folder

start_time = validate_time_if_provided(args.start_time)
end_time = validate_time_if_provided(args.end_time)

def rename_video_files(folder_path):
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']
    for root, _, files in os.walk(folder_path):
        for file in sorted(files):
            if os.path.splitext(file)[1].lower() in video_extensions:
                old_file_path = os.path.join(root, file)
                filename, extension = os.path.splitext(file)
                new_filename = re.sub(r'[^\w\s.-]', '', filename)  # Remove unsupported characters
                new_file_path = os.path.join(root, new_filename)
                index = 1
                while os.path.exists(new_file_path + extension):
                    new_filename = f"{filename}_{index}"
                    new_file_path = os.path.join(root, new_filename)
                    index += 1
                os.rename(old_file_path, new_file_path + extension)

def get_video_duration(filename):
    result = subprocess.run(["ffmpeg", "-i", filename],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output = result.stderr.decode()
    lines = output.splitlines()
    for line in lines:
        if "Duration" in line:
            parts = line.split(",")
            for part in parts:
                if "Duration" in part:
                    duration = part.split()[1].split(".")[0]
                    hours, minutes, seconds = duration.split(":")
                    total_seconds = int(hours) * 3600 + int(
                        minutes) * 60 + int(seconds)
                    return total_seconds
    return None

def ffmpeg_1():
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']
    for root, _, files in os.walk(input_folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in video_extensions:
                input_path = os.path.join(root, file)
                output_root = os.path.relpath(root, input_folder)
                output_path = os.path.join(output_folder, output_root, file)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure output folder exists
                cmd_parts = ['ffmpeg', '-i', input_path, '-c', 'copy']
                if start_time is not None:
                    cmd_parts.extend(['-ss', start_time])
                if end_time is not None:
                    # cmd_parts.extend(['-to', convert_seconds(get_video_duration(input_path) - 20)])
                    cmd_parts.extend(['-to', end_time])
                cmd_parts.extend([output_path, '-y'])
                run_ffmpeg_command(cmd_parts)


if start_time is None and end_time is None:
    print('Warning: Both start_time and end_time are not provided. No trimming will be performed.')

rename_video_files(input_folder)
ffmpeg_1()
