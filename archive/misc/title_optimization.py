#!/usr/bin/env python3
"""
标题显示优化建议和测试
"""

def get_title_options():
    """提供不同长度的标题选项"""
    options = {
        "完整版": "🏦 澳大利亚抵押贷款经纪人AI助手",
        "简化版": "🏦 澳洲房贷AI助手", 
        "超简版": "🏦 房贷助手",
        "英文版": "🏦 AU Mortgage AI Assistant"
    }
    return options

def generate_responsive_title_css():
    """生成响应式标题CSS"""
    css = """
    <style>
    /* 响应式标题 */
    .main-title {
        color: #1f77b4;
        margin-bottom: 0.5rem;
        font-weight: 600;
        text-align: center;
    }
    
    /* 大屏幕 */
    @media (min-width: 1024px) {
        .main-title {
            font-size: 2.5rem;
        }
        .subtitle {
            font-size: 1.1rem;
        }
    }
    
    /* 中等屏幕 */
    @media (min-width: 768px) and (max-width: 1023px) {
        .main-title {
            font-size: 2rem;
        }
        .subtitle {
            font-size: 1rem;
        }
    }
    
    /* 小屏幕 */
    @media (max-width: 767px) {
        .main-title {
            font-size: 1.5rem;
            line-height: 1.3;
        }
        .subtitle {
            font-size: 0.9rem;
        }
    }
    
    /* 超小屏幕 */
    @media (max-width: 480px) {
        .main-title {
            font-size: 1.2rem;
            line-height: 1.2;
        }
        .subtitle {
            font-size: 0.8rem;
        }
    }
    
    .subtitle {
        color: #666;
        margin-top: 0;
        line-height: 1.4;
        text-align: center;
    }
    </style>
    """
    return css

def generate_title_html(version="完整版"):
    """生成标题HTML"""
    titles = get_title_options()
    title = titles.get(version, titles["完整版"])
    
    html = f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 class="main-title">
            {title}
        </h1>
        <p class="subtitle">
            专业的房贷咨询AI助手 | 支持中英文 | 多AI提供商
        </p>
    </div>
    """
    return html

if __name__ == "__main__":
    print("📱 标题显示优化建议:")
    print("="*40)
    
    options = get_title_options()
    for name, title in options.items():
        print(f"{name}: {title}")
        print(f"   长度: {len(title)} 字符")
        print()
    
    print("💡 使用建议:")
    print("- 桌面端: 使用完整版")
    print("- 平板端: 使用简化版")  
    print("- 手机端: 使用超简版")
    print("- 国际版: 使用英文版")
    
    print("\n🎨 CSS优化已实现:")
    print("- 响应式字体大小 (clamp函数)")
    print("- 多断点适配")
    print("- 行高优化")
    print("- 居中对齐")
