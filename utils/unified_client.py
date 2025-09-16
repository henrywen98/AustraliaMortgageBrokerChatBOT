import os
import json
import time
import requests
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import (
    OPENAI_API_KEY_VAR,
    OPENAI_CHAT_URL,
    MODEL_NAME,
    MODEL_PROVIDER,
    AZURE_OPENAI_API_KEY_VAR,
    AZURE_OPENAI_ENDPOINT_VAR,
    AZURE_OPENAI_DEPLOYMENT_VAR,
)
from dotenv import load_dotenv

load_dotenv()


class UnifiedAIClient:
    """统一的AI客户端（支持 OpenAI 与 Azure OpenAI）。"""

    def __init__(
        self,
        model: str = MODEL_NAME,
        provider: str = MODEL_PROVIDER,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        self.model = model or "gpt-4o-mini"
        self.provider = (provider or "openai").strip().lower()
        self.timeout = timeout
        self.max_retries = max_retries

        self.api_url = OPENAI_CHAT_URL
        self.responses_api_url = "https://api.openai.com/v1/responses"

        if self.provider == "azure":
            self.session = None
            self.api_key = os.getenv(AZURE_OPENAI_API_KEY_VAR)
            self.azure_endpoint = os.getenv(AZURE_OPENAI_ENDPOINT_VAR, "").strip()
            self.azure_deployment = os.getenv(AZURE_OPENAI_DEPLOYMENT_VAR) or self.model
            if not self.api_key:
                print("⚠️ AZURE_OPENAI_API_KEY 未设置")
            if not self.azure_endpoint:
                raise ValueError("Missing AZURE_OPENAI_ENDPOINT")

            self.azure_client = OpenAI(
                api_key=self.api_key,
                base_url=self.azure_endpoint,
            )
            # Azure 部署不提供 /v1/models 探测接口，直接假定可用
            self.model_available = True
            # Azure Responses API 尚未全面开放，关闭 Responses 模式
            self.use_responses = False
        else:
            self.session = requests.Session()
            self.api_key = os.getenv(OPENAI_API_KEY_VAR)
            if not self.api_key:
                print("⚠️ OPENAI_API_KEY 未设置")

            # 预探测模型是否存在（忽略失败）
            self.model_available = self._probe_model(self.model)
            # 模型能力探测（启用 Responses API & 工具）
            self.use_responses = str(self.model).lower().startswith("gpt-5")

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            if self.provider == "azure":
                raise ValueError("Missing AZURE_OPENAI_API_KEY")
            raise ValueError("Missing OPENAI_API_KEY")
        if self.provider == "azure":
            return {
                "api-key": self.api_key,
                "Content-Type": "application/json",
            }
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

    def _sanitize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Strip unsupported fields (e.g., custom 'ts') and normalise structure.
        - Keep only 'role' and 'content' keys for each message item.
        - Coerce content to string if needed.
        """
        sanitized: List[Dict[str, Any]] = []
        for m in messages:
            if not isinstance(m, dict):
                # Fallback: convert to user text
                sanitized.append({"role": "user", "content": str(m)})
                continue
            role = m.get("role") or "user"
            content = m.get("content")
            if isinstance(content, (list, tuple)):
                # Join simple text parts if provided as list
                try:
                    content = "".join(
                        [
                            (seg.get("text") if isinstance(seg, dict) else str(seg))
                            for seg in content
                        ]
                    )
                except Exception:
                    content = " ".join([str(x) for x in content])
            if content is None:
                content = ""
            sanitized.append({"role": role, "content": str(content)})
        return sanitized

    def _generate_via_azure(self, messages: List[Dict[str, Any]], max_tokens: int, use_web_search: bool) -> str:
        if use_web_search:
            print("ℹ️ Azure OpenAI 当前不支持模型内置 Web Search 工具，已忽略 use_web_search 参数。")

        sanitized_messages = self._sanitize_messages(messages)
        try:
            completion = self.azure_client.chat.completions.create(  # type: ignore[attr-defined]
                model=self.azure_deployment,
                messages=sanitized_messages,
                max_completion_tokens=max_tokens,
            )
        except Exception as exc:
            raise Exception(f"Azure OpenAI call failed: {exc}")

        message = completion.choices[0].message
        text = getattr(message, "content", None)
        if isinstance(message, dict):
            text = message.get("content")
        if not text:
            raise Exception(f"Empty response: {completion}")
        return str(text).strip()

    def generate_response(self, messages: List[dict], max_tokens: int = 1500, use_web_search: bool = False) -> str:
        if self.provider == "azure":
            return self._generate_via_azure(messages, max_tokens, use_web_search)

        if not self.model_available:
            print(
                f"⚠️ 模型 {self.model} 未在 /v1/models 列表中发现，仍尝试直接调用；请确认名称是否正确。"
            )

        try:
            if self.use_responses:
                # Responses API 路径，支持工具（web_search）
                payload: Dict[str, Any] = {
                    "model": self.model,
                    "input": self._sanitize_messages(messages),
                }
                # 最大输出（responses API 字段名不同）
                payload["max_output_tokens"] = max_tokens
                # 限制推理开销，提升产出速度
                payload["reasoning"] = {"effort": "low"}
                if use_web_search:
                    payload["tools"] = [{"type": "web_search"}]
                resp = self._request_with_retry(payload, url=self.responses_api_url)
                data = resp.json()
                # Responses API：优先从 message 输出中收集文本
                content = None
                if isinstance(data.get("output"), list):
                    texts: list[str] = []
                    for item in data["output"]:
                        if not isinstance(item, dict):
                            continue
                        if item.get("type") == "message" and item.get("role") in (None, "assistant"):
                            for seg in item.get("content", []) or []:
                                if isinstance(seg, dict):
                                    t = seg.get("text") or ""
                                    if t:
                                        texts.append(t)
                        elif item.get("type") in ("output_text",):
                            t = item.get("text") or ""
                            if t:
                                texts.append(t)
                    if texts:
                        content = "\n".join(texts).strip()
                if not content:
                    # 次优：尝试聚合 output_text 或兼容 Chat Completions 字段
                    content = data.get("output_text") or data.get("choices", [{}])[0].get("message", {}).get("content")
                if not content:
                    raise Exception(f"Empty response: {data}")
                latency = getattr(resp, "latency_ms", 0)
                return content.strip() + f"\n\n(延迟 {latency:.0f}ms | OpenAI {self.model})"
            else:
                # 兼容 Chat Completions 路径
                payload: Dict[str, Any] = {
                    "model": self.model,
                    "messages": self._sanitize_messages(messages),
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
            if self.provider == "azure":
                completion = self.azure_client.chat.completions.create(  # type: ignore[attr-defined]
                    model=self.azure_deployment,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "ping"},
                    ],
                    max_completion_tokens=10,
                )
                return bool(getattr(completion.choices[0], "message", None))
            _ = self.generate_response(
                [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "ping"},
                ],
                max_tokens=10,
                use_web_search=False,
            )
            return True
        except Exception as exc:
            print(f"测试连接失败: {exc}")
            return False


# 别名保持兼容
OpenAIClient = UnifiedAIClient
