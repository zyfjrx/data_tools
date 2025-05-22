# LLM API 统一调用工具类
# 支持多种模型提供商：OpenAI、Ollama、智谱AI等
# 支持普通输出和流式输出

from typing import Any, Dict, Optional
from .providers.openai import OpenAIClient

# 你需要实现这些工具函数
# from ...constant.model import DEFAULT_MODEL_SETTINGS
from ..common.utils import extract_think_chain, extract_answer

DEFAULT_MODEL_SETTINGS = {
    "temperature": 0.7,
    "maxTokens": 8192
}


class LLMClient:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        self.config = {
            "provider": config.get("providerId", "openai"),
            "endpoint": self._handle_endpoint(config.get("providerId", "openai"), config.get("endpoint", "")) or "",
            "api_key": config.get("api_key", ""),
            "model": config.get("model", ""),
            "temperature": config.get("temperature", DEFAULT_MODEL_SETTINGS["temperature"]),
            "maxTokens": config.get("maxTokens", DEFAULT_MODEL_SETTINGS["maxTokens"]),
            "max_tokens": config.get("maxTokens", DEFAULT_MODEL_SETTINGS["maxTokens"])
        }
        if config.get("topP", None) not in (None, 0):
            self.config["topP"] = config["topP"]
        if config.get("topK", None) not in (None, 0):
            self.config["topK"] = config["topK"]

        self.client = self._create_client(self.config["provider"], self.config)

    def _handle_endpoint(self, provider, endpoint):
        if not provider or not endpoint:
            return endpoint
        if provider.lower() == "ollama":
            if endpoint.endswith("v1/") or endpoint.endswith("v1"):
                return endpoint.replace("v1", "api")
        if "/chat/completions" in endpoint:
            return endpoint.replace("/chat/completions", "")
        return endpoint

    def _create_client(self, provider, config):
        client_map = {
            "openai": OpenAIClient,
            "siliconflow": OpenAIClient,
            "deepseek": OpenAIClient,
        }
        ClientClass = client_map.get(provider.lower(), OpenAIClient)
        return ClientClass(config)

    def _call_client_method(self, method, *args):
        try:
            func = getattr(self.client, method)
            return func(*args)
        except Exception as error:
            print(f"{self.config['provider']} API 调用出错:", error)
            raise

    def chat(self, prompt, options=None):
        options = options or {}
        messages = prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
        # merged_options = {**options, **self.config}
        # return await self._call_client_method("chat", messages, merged_options)
        return self._call_client_method("chat", messages)

    def chat_stream(self, prompt, options=None):
        options = options or {}
        messages = prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
        # merged_options = {**options, **self.config}
        # return await self._call_client_method("chat_stream", messages, merged_options)
        return self._call_client_method("chat_stream", messages)

    def get_response(self, prompt, options=None):
        # llm_res = await self.chat(prompt, options)
        llm_res = self.chat(prompt)
        # 兼容不同返回结构
        return getattr(llm_res, "text", None) or getattr(getattr(llm_res, "response", None), "messages", "") or ""

    def get_response_with_cot(self, prompt, options=None):
        llm_res = self.chat(prompt, options)
        answer = getattr(llm_res, "text", "") or ""
        cot = ""
        if (answer and answer.startswith("<think>")) or answer.startswith("<thinking>"):
            cot = extract_think_chain(answer)
            answer = extract_answer(answer)
        elif (
                len(llm_res.response.choices) > 0
                and getattr(llm_res.response.body.choices[0].message, "reasoning_content", None)
        ):
            cot = llm_res.response.choices[0].message.reasoning_content or ""
            answer = llm_res.response.choices[0].message.content or ""
        if answer.startswith("\n\n"):
            answer = answer[2:]
        if cot.endswith("\n\n"):
            cot = cot[:-2]
        return {"answer": answer, "cot": cot}
