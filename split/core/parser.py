import re
from typing import List, Dict, Any

def extract_outline(text: str) -> List[Dict[str, Any]]:
    """
    提取文档大纲
    :param text: Markdown文本
    :return: 提取的大纲数组
    """
    outline_regex = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*\{#[\w-]+\})?\s*$', re.MULTILINE)
    outline = []
    for match in outline_regex.finditer(text):
        level = len(match.group(1))
        title = match.group(2).strip()
        outline.append({
            "level": level,
            "title": title,
            "position": match.start()
        })
    return outline

def split_by_headings(text: str, outline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    根据标题分割文档
    :param text: Markdown文本
    :param outline: 文档大纲
    :return: 按标题分割的段落数组
    """
    if not outline:
        return [{
            "heading": None,
            "level": 0,
            "content": text,
            "position": 0
        }]
    sections = []
    # 添加第一个标题前的内容（如果有）
    if outline[0]["position"] > 0:
        front_matter = text[:outline[0]["position"]].strip()
        if front_matter:
            sections.append({
                "heading": None,
                "level": 0,
                "content": front_matter,
                "position": 0
            })
    # 分割每个标题的内容
    for i, current in enumerate(outline):
        next_item = outline[i + 1] if i < len(outline) - 1 else None
        heading_line = text[current["position"]:].split('\n', 1)[0]
        start_pos = current["position"] + len(heading_line) + 1
        end_pos = next_item["position"] if next_item else len(text)
        content = text[start_pos:end_pos].strip()
        sections.append({
            "heading": current["title"],
            "level": current["level"],
            "content": content,
            "position": current["position"]
        })
    return sections

if __name__ == '__main__':
    with open('/split/data/宠物方案框架.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    outline = extract_outline(md_content)
    print(outline)
    sections = split_by_headings(md_content, outline)
    print(sections)