from .core import parser, splitter, summary, toc
from .output import formatter, file_writer
"""
Markdown文本分割工具主模块
"""
def split_markdown(markdown_text, min_split_length, max_split_length):
    """
    拆分Markdown文档
    :param markdown_text: Markdown文本
    :param min_split_length: 最小分割字数
    :param max_split_length: 最大分割字数
    :return: 分割结果数组
    """
    # 解析文档结构
    outline = parser.extract_outline(markdown_text)

    # 按标题分割文档
    sections = parser.split_by_headings(markdown_text, outline)

    # 处理段落，确保满足分割条件
    res = splitter.process_sections(sections, outline, min_split_length, max_split_length, summary.generate_enhanced_summary)

    return [
        {
            "result": f"> **📑 Summarization：** *{r['summary']}*\n\n---\n\n{r['content']}",
            **r
        }
        for r in res
    ]

# 导出模块功能
__all__ = [
    "split_markdown",
    "formatter",
    "file_writer",
    "toc",
    "parser",
    "splitter",
    "summary"
]

# # 目录提取功能
# extract_table_of_contents = toc.extract_table_of_contents
# toc_to_markdown = toc.toc_to_markdown
#
# # 其他功能直接通过模块引用
# combine_markdown = formatter.combine_markdown
# save_to_separate_files = file_writer.save_to_separate_files

if __name__ == '__main__':
    with open('/split/data/宠物方案框架.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    result = split_markdown(md_content, min_split_length=1500, max_split_length=2000)
    print(result)