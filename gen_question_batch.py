import os
import sys
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from llm.core.providers.openai import OpenAIClient
from llm.prompts.question import get_question_prompt
from llm.common.utils import extract_json_from_llm_output
from split.split_md import split_markdown

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 全局配置
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


def random_remove_question_mark(questions, prob):
    """随机移除问题末尾的问号（线程安全）"""
    import random
    return [
        q[:-1] if (random.random() * 100 < prob and q.rstrip()[-1] in {'?', '？'}) else q
        for q in questions
    ]


def process_single_chunk(args):
    """处理单个文本分块的核心函数"""
    split_md, config, number, q_len, prob = args
    try:
        llm_client = OpenAIClient(config)
        prompt = get_question_prompt({
            "text": split_md["content"],
            "number": number or (len(split_md["content"]) // q_len)
        })

        response = llm_client.chat(prompt)
        questions = extract_json_from_llm_output(response["text"])
        questions = random_remove_question_mark(questions, prob)

        if not questions or not isinstance(questions, list):
            raise ValueError("Invalid questions format")

        return {
            "content": split_md["content"],
            "questions": questions,
            "total": len(questions),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"处理分块出错: {str(e)}")
        return {
            "content": split_md["content"],
            "error": str(e),
            "status": "failed"
        }


def generate_questions_concurrently(
        split_mds,
        max_workers=4,
        number=None,
        question_generation_length=240,
        question_mask_removing_probability=60
):
    """多线程并发生成问题"""
    # 加载配置
    config_path = os.path.join(current_dir, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 准备任务参数
    task_args = [
        (chunk, config, number, question_generation_length, question_mask_removing_probability)
        for chunk in split_mds
    ]

    # 使用线程池处理
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_chunk = {
            executor.submit(process_single_chunk, args): idx
            for idx, args in enumerate(task_args)
        }

        # 实时获取完成的任务
        for future in as_completed(future_to_chunk):
            chunk_idx = future_to_chunk[future]
            try:
                result = future.result()
                results.append(result)
                status = result["status"]
                content_preview = result["content"][:30] + "..."

                if status == "success":
                    logger.info(f"完成分块 {chunk_idx}: 生成{result['total']}问题 | {content_preview}")
                else:
                    logger.error(f"失败分块 {chunk_idx}: {result['error']} | {content_preview}")
            except Exception as e:
                logger.error(f"分块 {chunk_idx} 结果处理异常: {str(e)}")

    # 按原始顺序排序结果（如果需要）
    return sorted(results, key=lambda x: split_mds.index(next(
        m for m in split_mds if m["content"] == x["content"]
    )))


if __name__ == '__main__':
    # 示例用法
    with open('/home/bmh/data_tools/data/宠物方案框架.md', 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 分割文本
    split_results = split_markdown(
        md_content,
        min_split_length=1500,
        max_split_length=2000
    )

    # 并发生成问题
    results = generate_questions_concurrently(
        split_results,
        max_workers=4,  # 根据API限制调整
        number=3,  # 每个分块生成3个问题
        question_mask_removing_probability=60
    )

    # 输出统计信息
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n处理完成: {success_count}/{len(results)} 成功")
    print(f"共生成 {sum(r['total'] for r in results if r['status'] == 'success')} 个问题")
