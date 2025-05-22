"""
文件输出模块
"""

import os

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def get_filename_without_ext(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]

def save_to_separate_files(split_result, base_filename, callback=None):
    """
    将分割结果保存到单独的文件
    :param split_result: 分割结果数组，每个元素应为{'summary': ..., 'content': ...}
    :param base_filename: 基础文件名（不包含扩展名）
    :param callback: 可选回调函数，参数为(error, output_dir, count)
    """
    base_path = os.path.dirname(base_filename)
    filename_without_ext = get_filename_without_ext(base_filename)
    output_dir = os.path.join(base_path, f"{filename_without_ext}_parts")
    ensure_directory_exists(output_dir)

    error = None
    try:
        for idx, part in enumerate(split_result):
            padded_index = str(idx + 1).zfill(3)
            output_file = os.path.join(output_dir, f"{filename_without_ext}_part{padded_index}.md")
            content = f"> **📑 Summarization：** *{part['summary']}*\n\n---\n\n{part['content']}"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
    except Exception as e:
        error = e

    if callback:
        callback(error, output_dir, len(split_result))