import os
import json
import time
import requests
from typing import List, Dict, Any, Optional
from config import (
    OPENAI_API_KEY_VAR,
    OPENAI_CHAT_URL,
    MODEL_NAME,
)
from dotenv import load_dotenv

load_dotenv()


class UnifiedAIClient:
    """统一的AI客户端（仅 OpenAI）。"""

    def __init__(self, model: str = MODEL_NAME, provider: str = "openai", timeout: int = 60, max_retries: int = 3):
        self.model = model or "gpt-4o-mini"
        self.provider = "openai"  # 固定为 OpenAI
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

        self.api_key = os.getenv(OPENAI_API_KEY_VAR)
        self.api_url = OPENAI_CHAT_URL
        self.responses_api_url = "https://api.openai.com/v1/responses"
        if not self.api_key:
            print("⚠️ OPENAI_API_KEY 未设置")

        # 预探测模型是否存在（忽略失败）
        self.model_available = self._probe_model(self.model)
        # 模型能力探测（启用 Responses API & 工具）
        self.use_responses = str(self.model).lower().startswith("gpt-5")

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _probe_model(self, model: str) -> bool:
        try:
            url = "https://api.openai.com/v1/models"
            resp = self.session.get(url, headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                ids = {m.get("id") for m in data.get("data", [])}
                return model in ids
        except Exception:
            return False
        return False

    def _request_with_retry(self, payload: Dict[str, Any], *, url: Optional[str] = None) -> requests.Response:
        last_error: Optional[str] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                resp = self.session.post(
                    url or self.api_url,
                    headers=self._headers(),
                    data=json.dumps(payload),
                    timeout=self.timeout,
                )
                latency = (time.time() - start) * 1000
                if resp.status_code == 200:
                    resp.latency_ms = latency  # type: ignore
                    return resp
                if resp.status_code in (408, 429, 500, 502, 503, 504):
                    last_error = f"HTTP {resp.status_code} {resp.text[:120]}"
                    time.sleep(1 + attempt * 0.5)
                    continue
                raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")
            except requests.exceptions.SSLError as e:
                last_error = f"SSL Error: {str(e)}"
                time.sleep(1 + attempt * 0.5)
                continue
            except requests.exceptions.RequestException as e:
                last_error = f"Network Error: {str(e)}"
                time.sleep(1 + attempt * 0.5)
                continue
        raise Exception(last_error or "Unknown network error")

    def generate_response(self, messages: List[dict], max_tokens: int = 1500, use_web_search: bool = False) -> str:
        if not self.model_available:
            print(
                f"⚠️ 模型 {self.model} 未在 /v1/models 列表中发现，仍尝试直接调用；请确认名称是否正确。"
            )

        try:
            if self.use_responses:
                # Responses API 路径，支持工具（web_search）
                payload: Dict[str, Any] = {
                    "model": self.model,
                    "input": messages,
                }
                # 最大输出（responses API 字段名不同）
                payload["max_output_tokens"] = max_tokens
                if use_web_search:
                    payload["tools"] = [{"type": "web_search"}]
                resp = self._request_with_retry(payload, url=self.responses_api_url)
                data = resp.json()
                # Responses API：尝试提取 output_text 或 content 文本
                content = (
                    data.get("output_text")
                    or ("\n".join([c.get("text", "") for c in data.get("output", []) if isinstance(c, dict)]) or None)
                )
                if not content:
                    # 兼容某些返回形态
                    content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if not content:
                    raise Exception(f"Empty response: {data}")
                latency = getattr(resp, "latency_ms", 0)
                return content.strip() + f"\n\n(延迟 {latency:.0f}ms | OpenAI {self.model})"
            else:
                # 兼容 Chat Completions 路径
                payload: Dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                }
                if self.model.startswith("gpt-4") or self.model.startswith("gpt-5"):
                    payload["max_completion_tokens"] = max_tokens
                else:
                    payload["max_tokens"] = max_tokens
                resp = self._request_with_retry(payload)
                data = resp.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if not content:
                    raise Exception(f"Empty response: {data}")
                latency = getattr(resp, "latency_ms", 0)
                return content.strip() + f"\n\n(延迟 {latency:.0f}ms | OpenAI {self.model})"
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")

    def test_connection(self) -> bool:
        try:
            _ = self.generate_response([{"role": "user", "content": "ping"}], max_tokens=5)
            return True
        except Exception:
            return False


# 别名保持兼容
OpenAIClient = UnifiedAIClient
