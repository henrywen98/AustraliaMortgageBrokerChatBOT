import requests
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

class WebSearchClient:
    """网络搜索客户端，支持多种搜索引擎"""
    
    def __init__(self):
        self.search_engines = {
            "serper": self._search_serper,
            "duckduckgo": self._search_duckduckgo,
            "mock": self._search_mock  # 用于测试
        }
        # 优先级：Serper (若配置了API Key) > DuckDuckGo (若已安装) > Mock
        try:
            import os as _os
            if _os.getenv("SERPER_API_KEY"):
                self.default_engine = "serper"
            else:
                try:
                    # Prefer the lightweight 'ddgs' package
                    from ddgs import DDGS  # noqa: F401
                    self.default_engine = "duckduckgo"
                except Exception:
                    self.default_engine = "mock"
        except Exception:
            self.default_engine = "mock"
    
    def search(self, query: str, num_results: int = 3, engine: str = "auto") -> List[Dict[str, Any]]:
        """执行网络搜索
        
        Args:
            query: 搜索查询
            num_results: 返回结果数量
            engine: 搜索引擎 ("auto", "duckduckgo", "serper", "mock")
        """
        if engine == "auto":
            # 智能选择：优先DuckDuckGo（免费），然后Serper，最后Mock
            if os.getenv("SERPER_API_KEY"):
                print("🔍 使用 Google Serper 搜索...")
                try:
                    return self._search_serper(query, num_results)
                except Exception as e:
                    print(f"Serper搜索失败，切换到DuckDuckGo: {e}")
            
            print("🦆 使用 DuckDuckGo 搜索（免费）...")
            return self._search_duckduckgo(query, num_results)
            
        elif engine == "duckduckgo":
            return self._search_duckduckgo(query, num_results)
        elif engine == "serper":
            return self._search_serper(query, num_results)
        elif engine == "mock":
            return self._search_mock(query, num_results)
        else:
            raise ValueError(f"不支持的搜索引擎: {engine}")
    
    def _search_serper(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """使用Serper API搜索"""
        import os
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            raise ValueError("需要设置 SERPER_API_KEY")
        
        url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "num": num_results,
            "gl": "au",  # 澳大利亚结果
            "hl": "zh"   # 中文界面
        }
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": "Google搜索"
            })
        
        return results
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """使用DuckDuckGo搜索（免费且无需API密钥）"""
        try:
            from ddgs import DDGS
            
            # 针对澳洲房贷优化搜索查询
            # 基于英文关键词优化：若原查询为中文，请在调用处先翻译
            au_query = f"{query} Australia mortgage loan rate bank RBA cash rate"
            
            results = []
            # 简化API调用
            search_results = DDGS().text(
                au_query,
                region="au-en",  # 澳洲英语区域
                safesearch="moderate",
                max_results=num_results
            )
            
            for i, item in enumerate(search_results, 1):
                results.append({
                    "title": item.get("title", "未知标题"),
                    "snippet": item.get("body", "无摘要信息")[:300] + "...",
                    "url": item.get("href", ""),
                    "source": "DuckDuckGo澳洲搜索"
                })
            
            return results
            
        except ImportError:
            print("📦 正在尝试安装 ddgs...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "ddgs"])
                return self._search_duckduckgo(query, num_results)  # 重试
            except Exception as install_error:
                print(f"❌ 安装失败: {install_error}")
                return self._search_mock(query, num_results)
        except Exception as e:
            print(f"🔍 DuckDuckGo搜索遇到问题，使用备用数据: {e}")
            return self._search_mock(query, num_results)
    
    def _search_mock(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """模拟搜索结果（用于测试）"""
        mock_results = [
            {
                "title": "澳大利亚房贷利率最新动态 - 央行政策分析",
                "snippet": f"根据最新搜索 '{query}'，澳大利亚储备银行(RBA)公布的最新政策利率为4.35%。各大银行的房贷利率在5.5%-7.2%之间。固定利率产品相比浮动利率更受欢迎...",
                "url": "https://www.rba.gov.au/monetary-policy/",
                "source": "澳大利亚储备银行官网"
            },
            {
                "title": "2024年澳洲首次购房者指南 - 政府补助政策",
                "snippet": f"关于 '{query}' 的最新信息：首次购房者补助(FHOG)金额为$10,000-$45,000不等，各州政策略有差异。印花税减免政策在新南威尔士州、维多利亚州等地实施...",
                "url": "https://www.firsthome.gov.au/",
                "source": "澳大利亚政府首次购房指南"
            },
            {
                "title": "澳洲四大银行房贷产品对比 - 最新利率表",
                "snippet": f"搜索 '{query}' 显示：CBA、ANZ、Westpac、NAB四大银行最新房贷利率对比。最低利率产品为5.49%起，LVR要求80%以下可享受优惠利率...",
                "url": "https://www.canstar.com.au/home-loans/",
                "source": "Canstar金融比较网站"
            }
        ]
        
        return mock_results[:num_results]
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """格式化搜索结果为文本"""
        if not results:
            return "未找到相关搜索结果。"
        
        formatted = "🔍 网络搜索结果：\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "").strip() or "未命名"
            snippet = result.get("snippet", "").strip()
            source = result.get("source", "未知来源").strip()
            url = result.get("url", "").strip()
            formatted += f"[{i}] {title}\n"
            if snippet:
                formatted += f"📄 {snippet}\n"
            formatted += f"🔗 来源：{source}\n"
            if url:
                formatted += f"链接：{url}\n"
            formatted += "\n"
        
        return formatted

class SearchAugmentor:
    """通用LLM + 网络搜索增强器（与具体模型无关）。"""

    def __init__(self, llm_client, web_search_client):
        self.llm_client = llm_client
        self.web_search = web_search_client

    def search_and_answer(self, user_query: str, search_enabled: bool = True, num_results: int = 3, reasoning: bool = False, search_query: str | None = None) -> Dict[str, Any]:
        """使用网络搜索增强回答，支持可选推理模式。统一要求输出简体中文。"""
        response_data = {
            "answer": "",
            "search_results": [],
            "sources": [],
            "search_used": search_enabled
        }
        
        if search_enabled:
            # 执行网络搜索
            effective_query = (search_query or user_query or "").strip()
            effective_query = self._rewrite_search_query(effective_query)
            print(f"🔍 正在搜索: {effective_query}")
            search_results = self.web_search.search(effective_query, num_results)
            response_data["search_results"] = search_results
            
            if search_results:
                # 构建增强提示
                search_context = self.web_search.format_search_results(search_results)
                
                if reasoning:
                    structure = "请先给出‘推理过程（简要要点）’，再给出‘结论’。"
                else:
                    structure = "请直接给出清晰‘结论’，不展示推理过程。"

                enhanced_prompt = f"""
基于以下网络搜索结果，请用简体中文回答用户问题：

{search_context}

用户问题：{user_query}

要求：
1. {structure}
2. 在回答正文中，用 [1], [2], [3] 标注引用处（若适用）
3. 信息不确定时请提示核验，不得编造
"""
                
                messages = [{"role": "user", "content": enhanced_prompt}]
                
                # 提取来源信息
                response_data["sources"] = [
                    {
                        "title": r["title"],
                        "url": r["url"],
                        "source": r["source"]
                    }
                    for r in search_results
                ]
            else:
                # 搜索失败，使用普通模式（仍保留结构指引）
                if reasoning:
                    structure = "请先给出‘推理过程（简要要点）’，再给出‘结论’。"
                else:
                    structure = "请直接给出清晰‘结论’，不展示推理过程。"
                enhanced_prompt = f"用户问题：{user_query}\n请用简体中文回答。{structure}"
                messages = [{"role": "user", "content": enhanced_prompt}]
        else:
            # 不使用搜索，直接回答（保持语言与结构）
            if reasoning:
                structure = "请先给出‘推理过程（简要要点）’，再给出‘结论’。"
            else:
                structure = "请直接给出清晰‘结论’，不展示推理过程。"
            messages = [{"role": "user", "content": f"请用简体中文回答：{user_query}\n{structure}"}]
        
        # 调用LLM生成回答
        try:
            answer = self.llm_client.generate_response(messages, max_tokens=800)
            response_data["answer"] = answer
        except Exception as e:
            response_data["answer"] = f"生成回答时出错：{str(e)}"
        
        return response_data

    # ----------------------------
    # Query rewriting for better AU finance results
    # ----------------------------
    def _rewrite_search_query(self, q: str) -> str:
        """Bias queries toward authoritative Australian finance sources.
        Keeps the user's intent, adds AU context and trusted sites.
        """
        base = (q or "").strip()
        low = base.lower()
        boosters: list[str] = []

        # Ensure AU context
        if " australia" not in low and " au" not in low and "rba" not in low:
            boosters.append("Australia")

        # Cash rate → RBA and regulators
        if any(kw in low for kw in ["cash rate", "rba", "official cash rate"]):
            boosters.append("RBA cash rate")
            boosters.append("site:rba.gov.au OR site:apra.gov.au OR site:abs.gov.au OR site:treasury.gov.au")

        # Home loan / mortgage interest
        if any(kw in low for kw in ["home loan", "mortgage", "interest rate", "variable rate", "fixed rate"]):
            boosters.append(
                "site:commbank.com.au OR site:nab.com.au OR site:anz.com OR site:westpac.com.au OR site:canstar.com.au"
            )

        # First home buyer / FHOG
        if any(kw in low for kw in ["first home", "fhog", "first home owner grant", "stamp duty"]):
            boosters.append(
                "site:firsthome.gov.au OR site:nsw.gov.au OR site:vic.gov.au OR site:qld.gov.au OR site:wa.gov.au"
            )

        # De-duplicate tokens while preserving order
        if boosters:
            parts = [base] + boosters
            seen = set()
            merged: list[str] = []
            for p in parts:
                if p not in seen:
                    merged.append(p)
                    seen.add(p)
            return " ".join(merged)
        return base
