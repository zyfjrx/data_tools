from swift.llm import load_dataset
import json

# dataset = load_dataset(['swift/self-cognition'], model_name=['宠物助手', 'Pet Assistant'],
#                        model_author=['钱湾科技', 'Qianwan Technology '])[0]
# print(dataset)
# print(dataset[0])
# with open("self_cognition.json", "w", encoding="utf-8") as f:
#     converted_items = []
#     for sample in dataset:
#         instruction = sample["messages"][0]["content"]
#         output = sample["messages"][1]["content"]
#         converted_item = {
#             "instruction": instruction,
#             "input": "",  # 始终为空
#             "output": output
#         }
#         converted_items.append(converted_item)
#     json.dump(converted_items,f,indent=2, ensure_ascii=False)

name = ['宠物助手', 'Pet Assistant']
author = ['钱湾科技', 'Qianwan Technology ']
with open("data/self_cognition.jsonl", "r", encoding="utf-8") as f:
    converted_items = []
    for line in f:
        data = json.loads(line)
        response = data['response']
        if data['tag'] == "en":
            response = response.replace("{{NAME}}", name[1]).replace("{{AUTHOR}}", author[1])
        else:
            response = response.replace("{{NAME}}", name[0]).replace("{{AUTHOR}}", author[0])
        data['response'] = response
        converted_item = {
            "instruction": data['query'],
            "input": "",  # 始终为空
            "output": data['response']
        }
        converted_items.append(converted_item)

with open("data/self_cognition_cot.json", "w", encoding="utf-8") as f:
    json.dump(converted_items, f, indent=2, ensure_ascii=False)

