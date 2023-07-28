import os
import itertools
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


# Function to move files to a subfolder
def move_files_to_subfolder(file_list, folder_path, report):
    # Create subfolder with the current date as the name
    subfolder_name = datetime.now().strftime("%Y%m%d")
    subfolder_path = os.path.join(folder_path, subfolder_name)
    # if subfolder_path exists, make variation
    if os.path.exists(subfolder_path):
        subfolder_name = datetime.now().strftime("%Y%m%d-%H%M%S")
        subfolder_path = os.path.join(folder_path, subfolder_name)

    os.makedirs(subfolder_path, exist_ok=True)

    # Move files to the subfolder
    for file_name in file_list:
        source_path = os.path.join(folder_path, file_name)
        destination_path = os.path.join(subfolder_path, file_name)
        os.rename(source_path, destination_path)

    # make report a txt file and move to the subfolder
    with open(os.path.join(subfolder_path, "report.txt"), "w") as f:
        f.write(report)
        f.close()


filename_amount = {}


# combo is a list of file, filter the pdf files, and split filename using '-', the second part should be float, do the sum of all them
def sum_combination(combo):
    sum = 0
    for file in combo:
        if file in filename_amount:
            sum += filename_amount[file]
        else:
            sum += filename_amount.setdefault(
                file, float(file.split("-")[1].replace(".pdf", "").strip())
            )
    return sum


# Function to find the combination of files with the closest total to the target amount
def find_closest_combination(file_list, target_amount):
    closest_combination = None
    min_difference = float("inf")

    # Generate all possible combinations of files
    for r in range(1, len(file_list) + 1):
        combinations = itertools.combinations(file_list, r)
        # Iterate through each combination
        for combination in combinations:
            total = sum_combination(combination)
            difference = abs(total - target_amount)
            # print(combination, total, difference)

            # Update the closest combination if the difference is smaller
            if difference < min_difference:
                closest_combination = combination
                min_difference = difference
                # 提供最小差值范围，避免过度查找
                if difference / target_amount < 0.01:
                    return closest_combination
    return closest_combination


root = tk.Tk()
root.withdraw()

# 创建GUI窗口并让用户选择文件夹
file_dir = filedialog.askdirectory()

# 如果用户选择了文件夹，则继续处理
if file_dir:
    files = os.listdir(file_dir)
    # filter only pdf file
    files = [file for file in files if file.endswith(".pdf")]

    # Prompt the user for the target amount
    target_amount = float(input("Enter the target amount: "))
    combination = find_closest_combination(files, target_amount)
    # print each file in combination
    for file in combination:
        print(file)
    print(sum_combination(combination))

    # 定义字典，用于存储每个项目类型对应的浮点数之和
    total_dict = {}

    # 遍历文件列表
    for file_name in combination:
        name_parts = file_name.split("-")  # 将文件名按照"-"分割
        if len(name_parts) == 2:  # 如果成功分割成两部分
            proj_type = name_parts[0].strip()  # 第一部分是项目类型
            try:
                float_num = float(name_parts[1].replace(".pdf", "").strip())  # 第二部分是浮点数
            except ValueError:  # 如果无法将第二部分转换为浮点数，则跳过
                continue
            if proj_type in total_dict:  # 如果这个项目类型已经在字典中
                # 将这个浮点数加到之前的值上
                total_dict[proj_type]["total"] += float_num
                total_dict[proj_type]["count"] += 1  # 文件数量加1
            else:
                # 如果这个项目类型还没有出现过，则将其加入字典
                total_dict[proj_type] = {"total": float_num, "count": 1}
    report = []

    # 输出每个项目类型对应的浮点数之和和文件数量
    for proj_type, data in total_dict.items():
        line = f"{proj_type}: {round(data['total'], 2)} ({data['count']} files)"
        report.append(line)
        print(line)

    # 输出总计
    total = sum(data["total"] for data in total_dict.values())
    # format total to 2 decimal using half even number
    total = round(total, 2)

    # 将数字转换为大写汉字形式
    total_ch = (
        str(total)
        .replace("0", "零")
        .replace("1", "壹")
        .replace("2", "贰")
        .replace("3", "叁")
        .replace("4", "肆")
        .replace("5", "伍")
        .replace("6", "陆")
        .replace("7", "柒")
        .replace("8", "捌")
        .replace("9", "玖")
    )

    file_count = sum(data["count"] for data in total_dict.values())
    line = f"Total: {total} ({file_count} files)"
    report.append(line)
    print(line)
    line = f"Total ch: {total_ch}"
    report.append(line)
    print(line)

    # ask whether to move files to subfolder
    answer = input("Move files to subfolder? (y/n): ")
    if answer == "y":
        move_files_to_subfolder(combination, file_dir, ("\n").join(report))
