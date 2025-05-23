def distill_questions_prompt(tag_path, current_tag, count=10, existing_questions=None, global_prompt=''):
    if existing_questions is None:
        existing_questions = []
    if existing_questions:
        existing_questions_text = (
            "已有的问题包括：\n"
            + "\n".join(f"- {q}" for q in existing_questions)
            + "\n请不要生成与这些重复的问题。"
        )
    else:
        existing_questions_text = ""

    global_prompt_text = f"你必须遵循这个要求：{global_prompt}" if global_prompt else ""

    return f"""
你是一个专业的知识问题生成助手。我需要你帮我为标签"{current_tag}"生成{count}个高质量的问题。

标签完整链路是：{tag_path}

请遵循以下规则：
{global_prompt_text}
1. 生成的问题应该与"{current_tag}"主题紧密相关
2. 问题应该具有教育价值和实用性，能够帮助人们学习和理解该领域
3. 问题应该清晰、明确，避免模糊或过于宽泛的表述
4. 问题应该有一定的深度和专业性，但不要过于晦涩难懂
5. 问题的形式可以多样化，包括事实性问题、概念性问题、分析性问题等
6. 问题应该是开放性的，能够引发思考和讨论
{existing_questions_text}

请直接以JSON数组格式返回问题，不要有任何额外的解释或说明，格式如下：
["问题1", "问题2", "问题3", ...]
"""