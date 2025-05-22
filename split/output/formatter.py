"""
输出格式化模块
"""

def combine_markdown(split_result):
    """
    将分割后的文本重新组合成Markdown文档
    :param split_result: 分割结果数组，每个元素应为{'summary': ..., 'content': ...}
    :return: 组合后的Markdown文档字符串
    """
    result = ""
    for i, part in enumerate(split_result):
        # 添加分隔线和摘要
        if i > 0:
            result += "\n\n---\n\n"
        result += f"> **📑 Summarization：** *{part['summary']}*\n\n---\n\n{part['content']}"
    return result