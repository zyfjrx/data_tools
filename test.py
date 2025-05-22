import json
import os
import sys

# SET PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] += os.pathsep + current_dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from llm.prompts.answer import get_answer_prompt
from llm.core.main import LLMClient
import logging

logger = logging.getLogger(__name__)


def generate_dataset_for_question(gen_question):
    try:
        config_path = os.path.join(current_dir, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        llm_client = LLMClient(config)
        prompt = get_answer_prompt(
            gen_question["content"],
            gen_question["questions"][0],
        )
        cot_result = llm_client.get_response_with_cot(prompt)
        answer = cot_result.get("answer")
        cot = cot_result.get("cot")

        datasets = {
            "question": gen_question["questions"][0],
            "answer": answer,
            "cot": cot,
        }
        return datasets
    except Exception as error:
        logger.error(f"生成数据集失败: {str(error)}")
        raise


if __name__ == '__main__':
    with open('/home/bmh/data_tools/data/question.json', 'r', encoding='utf-8') as f:
        gen_question = json.load(f)
    print(gen_question["questions"][0])

    datasets = generate_dataset_for_question(gen_question)
    print(datasets)
