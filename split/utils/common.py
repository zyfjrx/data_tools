"""
通用工具函数模块
"""

import os

def ensure_directory_exists(directory):
    """
    检查并创建目录
    :param directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def get_filename_without_ext(file_path):
    """
    从文件路径获取不带扩展名的文件名
    :param file_path: 文件路径
    :return: 不带扩展名的文件名
    """
    return os.path.splitext(os.path.basename(file_path))[0]