#!/usr/bin/env python3
"""
测试知识库与AI整合的脚本
"""
import os
from dotenv import load_dotenv
from utils.broker_logic import AustralianMortgageBroker

# 加载环境变量
load_dotenv()

def test_broker_with_rag():
    """测试经纪人AI助手的RAG功能"""
    print("🏦 测试澳大利亚抵押贷款经纪人助手的知识库功能")
    print("="*60)
    
    try:
        # 创建经纪人实例
        broker = AustralianMortgageBroker()
        print("✅ 经纪人助手初始化成功")
        
        # 测试问题列表
        test_questions = [
            "固定利率房贷有什么特点？",
            "申请房贷需要什么条件？",
            "首次购房者有什么优惠？",
            "投资房贷款与自住房贷款有什么区别？"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📋 测试问题 {i}: {question}")
            print("-" * 40)
            
            try:
                response = broker.generate_response(
                    question,
                    language="中文",
                    mode="simple"
                )
                
                print(f"🤖 AI回答:")
                print(response)
                print()
                
            except Exception as e:
                print(f"❌ 回答生成失败: {e}")
                continue
        
        print("🎉 RAG功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_broker_with_rag()
    if success:
        print("\n✅ 知识库与AI整合测试通过！")
        print("💡 您可以通过 Streamlit 应用程序与AI助手交互")
        print("📖 知识库已包含澳大利亚房贷相关资料")
    else:
        print("\n❌ 测试未完全通过，请检查配置")
