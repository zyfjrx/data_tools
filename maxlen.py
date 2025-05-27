from transformers import AutoTokenizer
import json
# 初始化tokenizer（例如GPT-2的）
tokenizer = AutoTokenizer.from_pretrained("/root/sft/Qwen3-4B")

def calculate_token_length(text):
    return len(tokenizer.encode(text))

# 如果数据来自文件，使用以下代码
with open('/root/LLaMA-Factory/data/pet_diseases-all-alpaca.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 计算每个output的token长度
max_length = 0
result = []
for item in data:
    output = item.get('output', '')
    token_length = calculate_token_length(output)
    result.append(token_length)
    max_length = max(max_length, token_length)

avg = sum(result)/len(result)
print(avg)
print(max_length)