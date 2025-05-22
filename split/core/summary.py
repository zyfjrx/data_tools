"""
摘要生成模块
"""

from typing import List, Dict, Any, Optional

def generate_enhanced_summary(
    section: Dict[str, Any],
    outline: List[Dict[str, Any]],
    part_index: Optional[int] = None,
    total_parts: Optional[int] = None
) -> str:
    """
    生成段落增强摘要，包含该段落中的所有标题
    :param section: 段落对象
    :param outline: 目录大纲
    :param part_index: 子段落索引（可选）
    :param total_parts: 子段落总数（可选）
    :return: 生成的增强摘要
    """
    # 如果是文档前言
    if (not section.get("heading") and section.get("level", 0) == 0) or (not section.get("headings") and not section.get("heading")):
        doc_title = outline[0]["title"] if outline and outline[0].get("level") == 1 else "文档"
        return f"{doc_title} 前言"

    # 如果有headings数组，使用它
    if section.get("headings") and len(section["headings"]) > 0:
        sorted_headings = sorted(
            section["headings"],
            key=lambda x: (x.get("level", 0), x.get("position", 0))
        )
        headings_map = {}

        for heading in sorted_headings:
            if not heading.get("heading"):
                continue
            heading_index = next(
                (i for i, item in enumerate(outline)
                 if item.get("title") == heading["heading"] and item.get("level") == heading["level"]),
                -1
            )
            if heading_index == -1:
                headings_map[heading["heading"]] = heading["heading"]
                continue
            path_parts = []
            parent_level = heading["level"] - 1
            for i in range(heading_index - 1, -1, -1):
                if parent_level <= 0:
                    break
                if outline[i].get("level") == parent_level:
                    path_parts.insert(0, outline[i].get("title"))
                    parent_level -= 1
            path_parts.append(heading["heading"])
            full_path = " > ".join(path_parts)
            headings_map[full_path] = full_path

        paths = sorted(
            list(headings_map.values()),
            key=lambda a: ((a.count(">")), a)
        )

        if len(paths) == 0:
            return section.get("heading") or "未命名段落"
        if len(paths) == 1:
            summary = paths[0]
            if part_index is not None and total_parts and total_parts > 1:
                summary += f" - Part {part_index}/{total_parts}"
            return summary

        summary = ""
        first_path = paths[0]
        segments = first_path.split(" > ")
        for i in range(len(segments) - 1):
            prefix = " > ".join(segments[:i + 1])
            is_common_prefix = all(
                p.startswith(prefix + " > ") for p in paths[1:]
            )
            if is_common_prefix:
                summary = prefix + " > ["
                for j, p in enumerate(paths):
                    unique_part = p[len(prefix) + 3:]
                    summary += (", " if j > 0 else "") + unique_part
                summary += "]"
                break
        if not summary:
            summary = ", ".join(paths)
        if part_index is not None and total_parts and total_parts > 1:
            summary += f" - Part {part_index}/{total_parts}"
        return summary

    # 兼容旧逻辑，当没有headings数组时
    if not section.get("heading") and section.get("level", 0) == 0:
        return "文档前言"

    current_heading_index = next(
        (i for i, item in enumerate(outline)
         if item.get("title") == section.get("heading") and item.get("level") == section.get("level")),
        -1
    )
    if current_heading_index == -1:
        return section.get("heading") or "未命名段落"

    parent_headings = []
    parent_level = section.get("level", 0) - 1
    for i in range(current_heading_index - 1, -1, -1):
        if parent_level <= 0:
            break
        if outline[i].get("level") == parent_level:
            parent_headings.insert(0, outline[i].get("title"))
            parent_level -= 1

    summary = ""
    if parent_headings:
        summary = " > ".join(parent_headings) + " > "
    summary += section.get("heading", "")
    if part_index is not None and total_parts and total_parts > 1:
        summary += f" - Part {part_index}/{total_parts}"
    return summary

def generate_summary(
    section: Dict[str, Any],
    outline: List[Dict[str, Any]],
    part_index: Optional[int] = None,
    total_parts: Optional[int] = None
) -> str:
    """
    旧的摘要生成函数，保留供兼容性使用
    :param section: 段落对象
    :param outline: 目录大纲
    :param part_index: 子段落索引（可选）
    :param total_parts: 子段落总数（可选）
    :return: 生成的摘要
    """
    return generate_enhanced_summary(section, outline, part_index, total_parts)