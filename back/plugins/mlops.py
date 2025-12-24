import requests
import json
from typing import List, Dict, Optional, Iterator

from common.get_config_from_yaml import get_config


class ChatClient:
    def __init__(
        self, base_url: str = "http://ai-service.tal.com/openai-compatible/v1"
    ):
        """
        初始化聊天客户端

        Args:
            app_id: 应用ID
            app_key: 应用密钥
            base_url: API基础URL
        """
        config = get_config()

        self.app_id = config["mlops"]["app_id"]
        self.app_key = config["mlops"]["app_key"]
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.app_id}:{self.app_key}",
            "Content-Type": "application/json",
        }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        # model: str = "claude-sonnet-4.5",
        model: str = "qwen3-32b",
        stream: bool = True,
        **kwargs,
    ) -> Iterator[Dict]:
        """
        发送聊天请求并返回响应

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "你好"}]
            model: 使用的模型名称
            stream: 是否使用流式响应
            **kwargs: 其他可选参数

        Yields:
            Dict: 流式响应数据
        """
        url = f"{self.base_url}/chat/completions"
        data = {"messages": messages, "model": model, "stream": stream, **kwargs}

        response = requests.post(url, headers=self.headers, json=data, stream=stream)

        if stream:
            for line in response.iter_lines():
                if line:
                    if line.startswith(b"data: "):
                        line = line[6:]
                        if line == b"[DONE]":
                            break
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
        else:
            yield response.json()

    def simple_chat(self, messages: list, model: str = "qwen3-32b") -> str:
        """
        简单的单次对话接口

        Args:
            message: 用户消息
            model: 使用的模型名称

        Returns:
            str: AI的回复
        """
        response = next(self.chat_completion(messages, model, stream=False))
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")


# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = ChatClient()

    prompt = """"""
    messages = [
        {
            "role": "user",
            "content": "专线信息: 京南TBN1_2-腾讯云-中金-犀思云-10G专线\nflap_log: 2025:11:05 06:59:09 Down",
        },
    ]

    # 示例1：使用简单对话接口
    response = client.simple_chat(messages)
    print("简单对话回复:", response)

    # 示例2：使用流式对话接口
    # print("\n流式对话回复:")
    # for chunk in client.chat_completion(messages):
    #     if chunk.get("choices"):
    #         content = chunk["choices"][0].get("delta", {}).get("content", "")
    #         if content:
    #             print(content, end="", flush=True)
    # print()
