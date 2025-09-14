#!/usr/bin/env python3
"""
测试启动性能优化的脚本
"""
import time
from dotenv import load_dotenv

load_dotenv()

def test_startup_speed():
    """测试不同组件的启动速度"""
    print("⏱️ 测试启动性能")
    print("="*40)
    
    # 测试基础导入
    start = time.time()
    from utils.unified_client import UnifiedAIClient
    from config import MODEL_NAME
    import_time = time.time() - start
    print(f"📦 基础模块导入: {import_time:.3f}s")
    
    # 测试AI客户端创建
    start = time.time()
    client = UnifiedAIClient(model=MODEL_NAME)
    client_time = time.time() - start
    print(f"🤖 AI客户端创建: {client_time:.3f}s")
    
    # 测试broker创建
    start = time.time()
    from utils.broker_logic import AustralianMortgageBroker
    broker = AustralianMortgageBroker()
    broker_time = time.time() - start
    print(f"🏦 Broker助手创建: {broker_time:.3f}s")
    
    total_time = import_time + client_time + broker_time
    print(f"\n⚡ 总启动时间: {total_time:.3f}s")
    
    print(f"\n✅ 性能测试完成")
    
    # 性能建议
    print(f"\n💡 性能优化建议:")
    if total_time > 2:
        print("   ⚠️ 启动时间较长，建议:")
        print("   - 检查网络连接速度")
    else:
        print("   ✅ 启动速度正常")

if __name__ == "__main__":
    test_startup_speed()
