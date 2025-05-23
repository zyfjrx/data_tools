import json
import os
import sys

# SET PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
os.environ['PATH'] += os.pathsep + current_dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from llm.prompts.answer import get_answer_prompt
from llm.prompts.optimizeCot import optimize_cot_prompt
from llm.core.main import LLMClient
import logging

logger = logging.getLogger(__name__)
def optimize_cot(original_question, answer, original_cot, llm_client):
    try:

        prompt = optimize_cot_prompt(original_question, answer, original_cot)
        response = llm_client.get_response_with_cot(prompt)
        optimize_cot = response.get('answer')
        cot = response.get('cot')
        optimized_answer = optimize_cot or cot
        optimized_answer.replace('优化后的思维链', '')
        result = {
            "original_cot" : original_cot,
            "question": original_question,
            "answer": answer,
            "cot": optimized_answer,
        }
        logging.info(f"成功优化思维链: {original_question}, ID: {id}")
        return result
    except Exception as error:
        logging.error(f"优化思维链失败: {str(error)}")
        raise

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
        original_cot = cot_result.get("cot")
        # 优化cot
        result = optimize_cot(gen_question["questions"][0], answer, original_cot, llm_client)
        return result
    except Exception as error:
        logger.error(f"生成数据集失败: {str(error)}")
        raise


if __name__ == '__main__':
    with open('/home/bmh/data_tools/data/question.json', 'r', encoding='utf-8') as f:
        gen_question = json.load(f)
    print(gen_question["questions"][0])

    datasets = generate_dataset_for_question(gen_question)
    print(datasets)
