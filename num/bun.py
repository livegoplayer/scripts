import pyperclip

def generate_lists(input_list, positions, start, end, step):
    generated_lists = []
    positions.sort()  # 确保位置按照从小到大的顺序排列
    num_positions = len(positions)
    current_values = [start] * num_positions  # 记录当前位置的值
    while True:
        # 生成新的列表
        new_list = input_list.copy()
        for i in range(num_positions):
            new_list[positions[i]] = current_values[i]
        generated_lists.append(new_list)

        # 更新当前位置的值
        j = num_positions - 1
        while j >= 0:
            current_values[j] += step
            if current_values[j] <= end:
                break
            current_values[j] = start
            j -= 1
        if j < 0:
            break  # 所有位置的值都已达到最大值，结束循环

    return generated_lists

# 输入列表
input_str = input("请输入列表，用逗号分隔：")
input_list = [float(x) for x in input_str.split(",")]

# 选择改变的位置
positions_str = input("请选择要改变的位置（从0开始，多个位置用逗号分隔）：")
positions = [int(x) for x in positions_str.split(",")]

# 选择改变的范围
start = float(input("请输入改变的起始值："))
end = float(input("请输入改变的结束值："))
step = float(input("请输入改变的步长："))

# 生成所有可能的列表
generated_lists = generate_lists(input_list, positions, start, end, step)

# 输出所有可能的列表
output_str = ""
for i, lst in enumerate(generated_lists):
    formatted_list = []
    for j, x in enumerate(lst):
        if j in positions:
            formatted_list.append(f"{x:.1f}")
        elif x == int(x):
            formatted_list.append(str(int(x)))
        else:
            formatted_list.append(str(x))
    output_str += f"{','.join(formatted_list)}\n"
    print(f"{','.join(formatted_list)}")

# 将结果复制到剪切板
pyperclip.copy(output_str)
print("已复制到剪切板！")
