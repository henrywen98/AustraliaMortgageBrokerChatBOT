#!/usr/bin/env python3
"""
测试 OpenAI 客户端与 Broker 集成
"""
import os
from dotenv import load_dotenv
from utils.unified_client import UnifiedAIClient
from utils.broker_logic import AustralianMortgageBroker

# 加载环境变量
load_dotenv()

def test_openai_client():
    """测试 OpenAI 客户端"""
    print("🤖 测试 OpenAI 客户端")
    print("="*50)
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            print("⚠️ OPENAI_API_KEY 未配置，跳过测试")
            return
        client = UnifiedAIClient(model=os.getenv("MODEL_NAME", "gpt-5-mini"))
        print("✅ 客户端创建成功")
        print(f"   模型: {client.model}")
        print("🔍 Responses API + Web Search 测试...")
        test_messages = [
            {"role": "system", "content": "Answer in Simplified Chinese."},
            {"role": "user", "content": "当前澳大利亚的官方现金利率是多少？请给出参考来源。"},
        ]
        response = client.generate_response(test_messages, max_tokens=800, use_web_search=True)
        print("✅ API调用成功")
        print(f"📤 回答预览: {response[:100]}...")
    except Exception as e:
        print(f"❌ OpenAI 客户端测试失败: {e}")

def test_broker_basic():
    """测试经纪人助手基本问答"""
    print("\n\n🏦 测试经纪人助手基本问答")
    print("="*50)
    try:
        broker = AustralianMortgageBroker()
        print("✅ 经纪人助手初始化成功")
        response = broker.generate_response(
            "固定利率房贷有什么特点？",
            reasoning=False,
            use_web_search=False,
        )
        print(f"📤 回答: {response[:200]}...")
    except Exception as e:
        print(f"❌ 经纪人助手测试失败: {e}")

if __name__ == "__main__":
    test_openai_client()
    test_broker_basic()
    
    print("\n" + "="*50)
    print("💡 配置说明:")
    print("1. 在 .env 文件中配置 OPENAI_API_KEY")
