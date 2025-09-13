#!/usr/bin/env python3
"""
测试知识库功能的脚本
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_knowledge_base():
    """测试知识库的基本功能"""
    print("🔍 开始测试知识库功能...")
    
    try:
        # 检查环境变量
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ 错误：未找到 OPENAI_API_KEY 环境变量")
            return False
        
        print("✅ OPENAI_API_KEY 已设置")
        
        # 尝试导入知识库模块
        try:
            from utils.knowledge_base import KnowledgeBase
            print("✅ 知识库模块导入成功")
        except ImportError as e:
            print(f"❌ 错误：无法导入知识库模块 - {e}")
            return False
        
        # 尝试创建知识库实例
        try:
            kb = KnowledgeBase()
            print("✅ 知识库实例创建成功")
            print(f"   📁 数据存储路径: {kb.persist_dir}")
            print(f"   🤖 嵌入模型: {kb.embedding_model}")
        except Exception as e:
            print(f"❌ 错误：无法创建知识库实例 - {e}")
            return False
        
        # 测试搜索功能（空查询）
        try:
            results = kb.search("测试查询", top_k=1)
            print(f"✅ 搜索功能正常，返回 {len(results)} 个结果")
        except Exception as e:
            print(f"❌ 错误：搜索功能异常 - {e}")
            return False
        
        # 检查是否有现有文档
        try:
            collection_count = kb.col.count()
            print(f"📊 当前知识库中有 {collection_count} 个文档块")
            if collection_count == 0:
                print("💡 提示：知识库为空，可以通过上传PDF文件来添加内容")
        except Exception as e:
            print(f"⚠️ 警告：无法获取集合计数 - {e}")
        
        print("\n🎉 知识库基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生未预期错误: {e}")
        return False

def test_rag_integration():
    """测试RAG集成功能"""
    print("\n🔍 开始测试RAG集成功能...")
    
    try:
        from utils.broker_logic import SimpleRAG
        from config import RAG_ENABLED, RAG_TOP_K
        
        print(f"⚙️ RAG 启用状态: {RAG_ENABLED}")
        print(f"⚙️ RAG Top-K: {RAG_TOP_K}")
        
        # 创建RAG实例
        rag = SimpleRAG(enabled=True, top_k=3)
        print("✅ RAG实例创建成功")
        
        # 测试检索
        results = rag.retrieve("澳大利亚房贷")
        print(f"✅ RAG检索功能正常，返回 {len(results)} 个结果")
        
        # 测试格式化
        context = rag.format_context(results)
        print(f"✅ 上下文格式化完成，长度: {len(context)} 字符")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG集成测试失败: {e}")
        return False

def test_pdf_utils():
    """测试PDF处理工具"""
    print("\n🔍 开始测试PDF处理工具...")
    
    try:
        from utils.pdf_utils import extract_pdf_text_with_pages
        print("✅ PDF工具模块导入成功")
        
        # 这里不测试实际文件，只是确保模块可以导入
        print("💡 PDF处理功能可用，可以处理PDF文件")
        return True
        
    except ImportError as e:
        print(f"❌ 错误：无法导入PDF工具 - {e}")
        return False

if __name__ == "__main__":
    print("🏦 澳大利亚抵押贷款经纪人助手 - 知识库功能测试\n")
    
    # 运行所有测试
    tests = [
        ("知识库基础功能", test_knowledge_base),
        ("RAG集成功能", test_rag_integration),
        ("PDF处理工具", test_pdf_utils),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"测试: {name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {name} - 通过")
        else:
            print(f"❌ {name} - 失败")
    
    print(f"\n{'='*50}")
    print(f"📊 测试结果: {passed}/{total} 通过")
    print('='*50)
    
    if passed == total:
        print("🎉 所有测试通过！知识库功能正常可用。")
        sys.exit(0)
    else:
        print("⚠️ 部分测试失败，请检查相关配置。")
        sys.exit(1)
