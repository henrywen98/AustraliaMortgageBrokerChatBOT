#!/usr/bin/env python3
"""
部署前检查脚本
确保所有配置正确，适合在 GitHub Actions 中运行
"""

import os
import sys
from pathlib import Path

def check_files():
    """检查必要文件是否存在"""
    required_files = [
        "app.py",
        "config.py", 
        "requirements.txt",
        ".env.example",
        ".streamlit/secrets.toml.example",
        "README.md",
        "LICENSE"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ 所有必要文件都存在")
    return True

def check_imports():
    """检查关键模块导入"""
    try:
        import streamlit
        import openai
        from utils.unified_client import UnifiedAIClient
        from utils.broker_logic import AustralianMortgageBroker
        from config import MODEL_NAME, validate_environment
        
        print("✅ 所有关键模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def check_config():
    """检查配置完整性"""
    try:
        from config import validate_environment, MODEL_NAME
        print(f"✅ 默认模型: {MODEL_NAME}")
        # 打印环境检查结果（密钥缺失在CI里属正常）
        msg = validate_environment()
        print(f"ℹ️  环境检查: {msg}")
        return True
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

def check_gitignore():
    """检查 .gitignore 配置"""
    if not Path(".gitignore").exists():
        print("❌ 缺少 .gitignore 文件")
        return False
    
    with open(".gitignore", "r") as f:
        content = f.read()
    
    required_ignores = [".env", "__pycache__", "*.pyc"]
    missing_ignores = []
    
    for ignore in required_ignores:
        if ignore not in content:
            missing_ignores.append(ignore)
    
    if missing_ignores:
        print(f"⚠️  .gitignore 可能缺少: {', '.join(missing_ignores)}")
    else:
        print("✅ .gitignore 配置正确")
    
    return True

def main():
    """主检查函数"""
    print("🔍 开始部署前检查...\n")
    
    checks = [
        ("文件完整性", check_files),
        ("模块导入", check_imports), 
        ("配置检查", check_config),
        ("Git配置", check_gitignore)
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        print(f"📋 检查 {name}...")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 所有检查通过！项目已准备好部署到 GitHub 和 Streamlit Cloud。")
        print("\n📝 下一步:")
        print("1. git add . && git commit -m 'Ready for deployment'")
        print("2. git push origin main") 
        print("3. 在 Streamlit Cloud 中部署")
        print("4. 配置 Secrets: OPENAI_API_KEY")
        return 0
    else:
        print("❌ 部分检查失败，请修复后重试。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
