"""
Markdown文档分割模块
"""

import re
from typing import List, Dict, Any

def split_long_section(section: Dict[str, Any], max_split_length: int) -> List[str]:
    """
    分割超长段落
    :param section: 段落对象
    :param max_split_length: 最大分割字数
    :return: 分割后的段落数组
    """
    content = section["content"]
    paragraphs = re.split(r'\n\n+', content)
    result = []
    current_chunk = ''

    for paragraph in paragraphs:
        # 如果当前段落本身超过最大长度，可能需要进一步拆分
        if len(paragraph) > max_split_length:
            # 如果当前块不为空，先加入结果
            if len(current_chunk) > 0:
                result.append(current_chunk)
                current_chunk = ''
            # 对超长段落进行分割（例如，按句子或固定长度）
            sentence_split = re.findall(r'[^.!?。！？]+[.!?。！？]+', paragraph) or [paragraph]
            sentence_chunk = ''
            for sentence in sentence_split:
                if len(sentence_chunk + sentence) <= max_split_length:
                    sentence_chunk += sentence
                else:
                    if len(sentence_chunk) > 0:
                        result.append(sentence_chunk)
                    # 如果单个句子超过最大长度，可能需要进一步拆分
                    if len(sentence) > max_split_length:
                        for i in range(0, len(sentence), max_split_length):
                            result.append(sentence[i:i+max_split_length])
                        sentence_chunk = ''
                    else:
                        sentence_chunk = sentence
            if len(sentence_chunk) > 0:
                current_chunk = sentence_chunk
        elif len(current_chunk + '\n\n' + paragraph) <= max_split_length:
            current_chunk = current_chunk + '\n\n' + paragraph if current_chunk else paragraph
        else:
            result.append(current_chunk)
            current_chunk = paragraph

    if len(current_chunk) > 0:
        result.append(current_chunk)

    return result

def process_sections(
    sections: List[Dict[str, Any]],
    outline: List[Dict[str, Any]],
    min_split_length: int,
    max_split_length: int,
    summary_func=None
) -> List[Dict[str, Any]]:
    """
    处理段落，根据最小和最大分割字数进行分割
    :param sections: 段落数组
    :param outline: 目录大纲
    :param min_split_length: 最小分割字数
    :param max_split_length: 最大分割字数
    :param summary_func: 摘要生成函数，需传入(section, outline, part_idx=None, total_parts=None)
    :return: 处理后的段落数组
    """
    # 预处理：将相邻的小段落合并
    preprocessed_sections = []
    current_section = None

    for section in sections:
        content_length = len(section["content"].strip())
        if content_length < min_split_length and current_section:
            merged_content = (
                current_section['content']
                + "\n\n"
                + (('#' * section['level'] + ' ' + section['heading'] + '\n') if section.get('heading') else '')
                + section['content']
            )
            if len(merged_content) <= max_split_length:
                current_section['content'] = merged_content
                if section.get('heading'):
                    current_section.setdefault('headings', []).append({
                        "heading": section['heading'],
                        "level": section['level'],
                        "position": section['position']
                    })
                continue
        if current_section:
            preprocessed_sections.append(current_section)
        current_section = {
            **section,
            "headings": [ { "heading": section['heading'], "level": section['level'], "position": section['position'] } ] if section.get('heading') else []
        }
    if current_section:
        preprocessed_sections.append(current_section)

    result = []
    accumulated_section = None

    for section in preprocessed_sections:
        content_length = len(section["content"].strip())
        if content_length < min_split_length:
            if not accumulated_section:
                accumulated_section = {
                    "heading": section.get("heading"),
                    "level": section.get("level"),
                    "content": section["content"],
                    "position": section["position"],
                    "headings": [ { "heading": section.get("heading"), "level": section.get("level"), "position": section.get("position") } ] if section.get("heading") else []
                }
            else:
                accumulated_section["content"] += (
                    "\n\n"
                    + (('#' * section['level'] + ' ' + section['heading'] + '\n') if section.get('heading') else '')
                    + section['content']
                )
                if section.get('heading'):
                    accumulated_section["headings"].append({
                        "heading": section['heading'],
                        "level": section['level'],
                        "position": section['position']
                    })
            accumulated_length = len(accumulated_section["content"].strip())
            if accumulated_length >= min_split_length:
                summary = summary_func(accumulated_section, outline) if summary_func else ""
                if accumulated_length > max_split_length:
                    sub_sections = split_long_section(accumulated_section, max_split_length)
                    for j, sub in enumerate(sub_sections):
                        result.append({
                            "summary": f"{summary} - Part {j+1}/{len(sub_sections)}" if summary else "",
                            "content": sub
                        })
                else:
                    result.append({
                        "summary": summary,
                        "content": accumulated_section["content"]
                    })
                accumulated_section = None
            continue

        if accumulated_section:
            summary = summary_func(accumulated_section, outline) if summary_func else ""
            accumulated_length = len(accumulated_section["content"].strip())
            if accumulated_length > max_split_length:
                sub_sections = split_long_section(accumulated_section, max_split_length)
                for j, sub in enumerate(sub_sections):
                    result.append({
                        "summary": f"{summary} - Part {j+1}/{len(sub_sections)}" if summary else "",
                        "content": sub
                    })
            else:
                result.append({
                    "summary": summary,
                    "content": accumulated_section["content"]
                })
            accumulated_section = None

        if content_length > max_split_length:
            sub_sections = split_long_section(section, max_split_length)
            if not section.get("headings") and section.get("heading"):
                section["headings"] = [ { "heading": section["heading"], "level": section["level"], "position": section["position"] } ]
            for i, sub in enumerate(sub_sections):
                summary = summary_func(section, outline, i+1, len(sub_sections)) if summary_func else ""
                result.append({
                    "summary": summary,
                    "content": sub
                })
        else:
            if not section.get("headings") and section.get("heading"):
                section["headings"] = [ { "heading": section["heading"], "level": section["level"], "position": section["position"] } ]
            summary = summary_func(section, outline) if summary_func else ""
            content = (('#' * section['level'] + ' ' + section['heading'] + '\n') if section.get('heading') else '') + section['content']
            result.append({
                "summary": summary,
                "content": content
            })

    if accumulated_section:
        if result:
            last_result = result[-1]
            merged_content = last_result['content'] + "\n\n" + accumulated_section['content']
            if len(merged_content) <= max_split_length:
                summary = summary_func({ **accumulated_section, "content": merged_content }, outline) if summary_func else ""
                result[-1] = {
                    "summary": summary,
                    "content": merged_content
                }
            else:
                summary = summary_func(accumulated_section, outline) if summary_func else ""
                content = (
                    (('#' * accumulated_section['level'] + ' ' + accumulated_section['heading'] + '\n') if accumulated_section.get('heading') else '')
                    + accumulated_section['content']
                )
                result.append({
                    "summary": summary,
                    "content": content
                })
        else:
            summary = summary_func(accumulated_section, outline) if summary_func else ""
            content = (
                (('#' * accumulated_section['level'] + ' ' + accumulated_section['heading'] + '\n') if accumulated_section.get('heading') else '')
                + accumulated_section['content']
            )
            result.append({
                "summary": summary,
                "content": content
            })

    return result