# 使用正确的导入和客户端初始化
from openai import OpenAI


class OpenAIClient:
    def __init__(self, config):
        self.endpoint = config.get("endpoint", "")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "")
        self.model_config = {
            "temperature": config.get("temperature", 0.7),
            "top_p": config.get("top_p", 0.9),
            "max_tokens": config.get("max_tokens", 8192)
        }
        # 创建 OpenAI 客户端实例
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.endpoint if self.endpoint else None
        )

    def _get_model(self):
        return self.model

    def _convert_json(self, data):
        result = []
        for item in data:
            if item.get("role") != "user":
                result.append(item)
                continue

            new_item = {
                "role": "user",
                "content": "",
                "experimental_attachments": [],
                "parts": []
            }

            content = item.get("content")
            if isinstance(content, str):
                new_item["content"] = content
                new_item["parts"].append({
                    "type": "text",
                    "text": content
                })
            elif isinstance(content, list):
                for content_item in content:
                    if content_item.get("type") == "text":
                        new_item["content"] = content_item.get("text", "")
                        new_item["parts"].append({
                            "type": "text",
                            "text": content_item.get("text", "")
                        })
                    elif content_item.get("type") == "image_url":
                        image_url = content_item.get("image_url", {}).get("url", "")
                        file_name = "image.jpg"
                        if image_url.startswith("data:"):
                            import re
                            match = re.match(r"^data:image\/(\w+);base64", image_url)
                            if match:
                                file_name = f"image.{match.group(1)}"
                        new_item["experimental_attachments"].append({
                            "url": image_url,
                            "name": file_name,
                            "contentType": image_url.split(";")[0].replace("data:", "") if image_url.startswith(
                                "data:") else "image/jpeg"
                        })
            result.append(new_item)
        return result

    def chat(self, prompt):
        if isinstance(prompt, list):
            messages =  self._convert_json(prompt)
        else:
            messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self._get_model(),
            messages=messages,
            temperature=self.model_config["temperature"],
            top_p=self.model_config["top_p"],
            max_tokens=self.model_config["max_tokens"]
        )
        return {
            "text": response.choices[0].message.content,  # 使用 .content 替代 ["content"]
            "response": response
        }

    def chat_stream(self, messages, options):
        openai_messages = []
        for msg in self._convert_json(messages):
            openai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        response = self.client.chat.completions.create(
            model=self._get_model(),
            messages=openai_messages,
            temperature=options.get("temperature", self.model_config["temperature"]),
            top_p=options.get("top_p", self.model_config["top_p"]),
            max_tokens=options.get("max_tokens", self.model_config["max_tokens"]),
            stream=True
        )
        return response
