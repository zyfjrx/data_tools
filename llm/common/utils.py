import json

def extract_json_from_llm_output(output):
    """
    从 LLM 输出中提取 JSON
    """
    # 先尝试直接 parse
    try:
        return json.loads(output)
    except Exception:
        pass
    json_start = output.find('```json')
    json_end = output.rfind('```')
    if json_start != -1 and json_end != -1:
        json_string = output[json_start + 7:json_end]
        try:
            return json.loads(json_string)
        except Exception as error:
            print('解析 JSON 时出错:', {'error': error, 'llmResponse': output})
    else:
        print('模型未按标准格式输出:', output)
        return None

def extract_think_chain(text):
    start_tags = ['<think>', '<thinking>']
    end_tags = ['</think>', '</thinking>']
    start_index = -1
    end_index = -1
    used_start_tag = ''
    used_end_tag = ''
    for i in range(len(start_tags)):
        current_start_index = text.find(start_tags[i])
        if current_start_index != -1:
            start_index = current_start_index
            used_start_tag = start_tags[i]
            used_end_tag = end_tags[i]
            break
    if start_index == -1:
        return ''
    end_index = text.find(used_end_tag, start_index + len(used_start_tag))
    if end_index == -1:
        return ''
    return text[start_index + len(used_start_tag):end_index].strip()

def extract_answer(text):
    start_tags = ['<think>', '<thinking>']
    end_tags = ['</think>', '</thinking>']
    for i in range(len(start_tags)):
        start = start_tags[i]
        end = end_tags[i]
        if start in text and end in text:
            parts_before = text.split(start)
            parts_after = parts_before[1].split(end)
            return (parts_before[0].strip() + ' ' + parts_after[1].strip()).strip()
    return text


def process_questions(datas):
    # 获取第一个对象中的 content 和 questions
    result = []
    for id , data in enumerate(datas):
        content = data['content']
        questions = data['questions']
        # 创建结果列表
        # 为每个问题创建新的对象
        for question in questions:
            new_obj = {
                'contentid': id,
                'content': content,
                'question': question
            }
            result.append(new_obj)
    return result
if __name__ == '__main__':
    with open("/home/bmh/data_tools/data/question.json",'r', encoding='utf-8') as f:
        datas = json.load(f)
    result = process_questions(datas)
    with open('/home/bmh/data_tools/data/processed_questions.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(result)