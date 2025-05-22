import os
import sys
import json
from llm.core.providers.openai import OpenAIClient
from llm.prompts.question import get_question_prompt
from llm.common.utils import extract_json_from_llm_output
from split.split_md import split_markdown
# SET PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] += os.pathsep + current_dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
logger = logging.getLogger(__name__)

def random_remove_question_mark(questions, question_mask_removing_probability):
    import random
    for i in range(len(questions)):
        question = questions[i].rstrip()
        if random.random() * 100 < question_mask_removing_probability and (question.endswith('?') or question.endswith('？')):
            question = question[:-1]
        questions[i] = question
    return questions

def generate_questions_for_chunk(split_md,number=None,question_generation_length=240,question_mask_removing_probability=60):
    try:

        # 创建LLM客户端
        # 从配置文件读取LLM客户端配置
        config_path = os.path.join(current_dir, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        llm_client = OpenAIClient(config)
        # 生成问题的数量，如果未指定，则根据文本长度自动计算
        question_number = number or (len(split_md["content"]) // question_generation_length)

        # 根据语言选择相应的提示词函数
        prompt = get_question_prompt({
            "text": split_md["content"],
            "number": question_number
        })
        response = llm_client.chat(prompt)

        # 从LLM输出中提取JSON格式的问题列表
        original_questions = extract_json_from_llm_output(response["text"])
        questions = random_remove_question_mark(original_questions, question_mask_removing_probability)
        if not questions or not isinstance(questions, list):
            raise ValueError("生成问题失败")



        # 返回生成的问题
        return {
            "content": split_md["content"],
            "questions": questions,
            "total": len(questions)
        }
    except Exception as error:
        logger.error("生成问题时出错: %s", error)
        raise
if __name__ == '__main__':
    # 读取md文件
    with open('/home/bmh/data_tools/split/data/论越剧的剧种风格_高义龙.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    results = split_markdown(md_content, min_split_length=1500, max_split_length=2000)
    split_md = results[3]
    gen_q = generate_questions_for_chunk(split_md)
    print(gen_q)

