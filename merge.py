import json
import os
from pathlib import Path


def merge_json_files(input_dir, output_file):
    """
    合并目录下所有JSON文件为一个JSON文件

    参数:
        input_dir: 包含JSON文件的目录路径
        output_file: 合并后的输出文件路径
    """
    merged_data = []

    # 遍历目录下所有.json文件
    for json_file in Path(input_dir).glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 检查数据格式是否符合要求
                if isinstance(data, list):
                    merged_data.extend(data)
                else:
                    print(f"警告: {json_file} 不是数组格式，跳过")

        except Exception as e:
            print(f"错误: 处理文件 {json_file} 时出错 - {str(e)}")
            continue

    # 将合并后的数据写入输出文件

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print(f"成功合并 {len(merged_data)} 条数据到 {output_file}")


if __name__ == '__main__':
    # 使用示例
    input_directory = '/Users/zhangyf/Documents/宠物数据/datasets'  # 存放JSON文件的目录
    output_filename = 'merged_output.json'  # 合并后的输出文件名

    # 确保输入目录存在
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)
        print(f"创建了输入目录: {input_directory}")
        print("请将JSON文件放入此目录后重新运行程序")
        exit()

    # 执行合并
    merge_json_files(input_directory, output_filename)