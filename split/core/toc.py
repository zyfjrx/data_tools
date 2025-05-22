import re

def generate_anchor_id(title):
    anchor = title.lower()
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = re.sub(r'[^\w\-]', '', anchor)
    anchor = re.sub(r'\-+', '-', anchor)
    anchor = anchor.strip('-')
    return anchor

def build_nested_toc(items, include_links=True):
    result = []
    stack = [{'level': 0, 'children': result}]
    for item in items:
        toc_item = {
            'title': item['title'],
            'level': item['level'],
            'position': item['position'],
            'children': []
        }
        if include_links:
            toc_item['link'] = f"#{item['anchor_id']}"
        while stack[-1]['level'] >= item['level']:
            stack.pop()
        stack[-1]['children'].append(toc_item)
        stack.append(toc_item)
    return result

def extract_table_of_contents(text, max_level=6, include_links=True, flat_list=False):
    heading_regex = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*\{#[\w-]+\})?\s*$', re.MULTILINE)
    toc_items = []
    for match in heading_regex.finditer(text):
        level = len(match.group(1))
        if level > max_level:
            continue
        title = match.group(2).strip()
        position = match.start()
        anchor_id = generate_anchor_id(title)
        toc_items.append({
            'level': level,
            'title': title,
            'position': position,
            'anchor_id': anchor_id,
            'children': []
        })
    if flat_list:
        result = []
        for item in toc_items:
            entry = {
                'level': item['level'],
                'title': item['title'],
                'position': item['position']
            }
            if include_links:
                entry['link'] = f"#{item['anchor_id']}"
            result.append(entry)
        return result
    return build_nested_toc(toc_items, include_links)

def nested_toc_to_markdown(items, indent=0, include_links=True):
    result = ''
    indent_str = '  ' * indent
    if not isinstance(items, list):
        print('Warning: items is not a list in nested_toc_to_markdown')
        return result
    for item in items:
        title_text = f"[{item['title']}]({item['link']})" if include_links and 'link' in item else item['title']
        result += f"{indent_str}- {title_text}\n"
        if item.get('children'):
            result += nested_toc_to_markdown(item['children'], indent + 1, include_links)
    return result

def flat_toc_to_markdown(items, include_links=True):
    result = ''
    for item in items:
        indent = '  ' * (item['level'] - 1)
        title_text = f"[{item['title']}]({item['link']})" if include_links and 'link' in item else item['title']
        result += f"{indent}- {title_text}\n"
    return result

def toc_to_markdown(toc, is_nested=True, include_links=True):
    if is_nested:
        return nested_toc_to_markdown(toc, 0, include_links)
    else:
        return flat_toc_to_markdown(toc, include_links)