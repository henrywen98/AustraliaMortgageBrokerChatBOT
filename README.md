# 澳大利亚房贷AI助手 | Australian Mortgage Broker AI Assistant

面向澳洲房贷咨询的智能 Streamlit 助手。提供网络搜索增强与专业经纪人人设。内部统一使用英文系统提示，但最终输出为简体中文；若输入为中文，将在内部先译为英文再进行搜索与推理（不展示翻译）。

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 核心特性

### 🤖 智能对话
- **OpenAI驱动**: 基于 gpt-4o-mini 的专业房贷咨询
- **上下文记忆**: 多轮对话连贯性
- **专业角色**: 澳洲房贷经纪人人设

### 🌐 网络搜索增强
- **实时信息**: 搜索最新的利率、政策、市场动态
- **来源引用**: 自动显示信息来源和链接
- **DuckDuckGo驱动**: 默认使用免费的DuckDuckGo搜索（无需API密钥）
- **智能降级**: Serper API可选，DuckDuckGo保底，Mock数据兜底
- **一键开关**: 侧边栏中随时启用/关闭

### 🎨 用户体验
- **现代化界面**: 响应式 Streamlit 设计
- **便捷操作**: 对话历史管理、一键清除/撤销
- **数据导出**: JSON 格式对话记录下载
- **移动友好**: 适配手机和平板设备

## 🚀 快速部署

### 方式一：Streamlit Cloud 部署（推荐）

1. **Fork 此项目到您的 GitHub**
   ```bash
   # 点击页面右上角的 "Fork" 按钮
   ```

2. **获取 OpenAI API 密钥**
   - 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
   - 创建新的 API 密钥

3. **部署到 Streamlit Cloud**
   - 访问 [Streamlit Cloud](https://share.streamlit.io/)
   - 点击 "New app"
   - 选择您 fork 的仓库
   - 设置：
     - **Main file path**: `app.py`
     - **Python version**: 3.11

4. **配置 Secrets**
   在 Streamlit Cloud 应用设置中的 "Secrets" 部分添加：
   ```toml
   OPENAI_API_KEY = "your_actual_openai_api_key_here"
   
   # 可选配置
   MODEL_NAME = "gpt-4o-mini"
   # SERPER_API_KEY = "your_serper_api_key_here"  # 网络搜索增强
   ```

5. **保存并部署**
   - 保存 Secrets 配置
   - 应用将自动重新部署
   - 几分钟后即可访问您的专属房贷AI助手

### 方式二：本地开发

1. **克隆项目**
   ```bash
   git clone https://github.com/henrywen98/AustraliaMortgageBrokerChatBOT.git
   cd AustraliaMortgageBrokerChatBOT
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加您的 OPENAI_API_KEY
   ```

4. **启动应用**
   ```bash
   streamlit run app.py
   ```
   
5. **访问应用**
浏览器打开：http://localhost:8501

更多部署细节与常见问题，请参见 `DEPLOYMENT.md`。

## 📋 环境配置

### 必需配置
- `OPENAI_API_KEY`: OpenAI API 密钥（[获取地址](https://platform.openai.com/api-keys)）

### 可选配置
- `MODEL_NAME`: 模型名称（默认: `gpt-4o-mini`）
- `SERPER_API_KEY`: Google 搜索 API（可选，未设置时自动使用免费的DuckDuckGo）
- `RAG_ENABLED`: 启用知识库功能（默认: `false`）

### Streamlit Cloud Secrets 示例
```toml
# 必需
OPENAI_API_KEY = "sk-..."

# 可选
MODEL_NAME = "gpt-4o-mini"
# SERPER_API_KEY = "your-serper-key"  # 可选：高质量Google搜索
```

## 💡 使用指南

### 界面功能

**侧边栏控制**：
- 🌐 **网络搜索**: 启用后获取最新房贷信息（附来源）
- 🧠 **推理模式**: 开启时显示“推理过程”和“结论”；默认仅“结论”
- 🔍 **测试连接**: 验证 API 密钥有效性
- 🗑️ **对话管理**: 清除历史/撤销上一轮
- 📥 **数据导出**: 下载 JSON 格式对话记录
- 💬 **智能对话**: 主界面聊天输入框用于发起提问

### 常见使用场景

1. **房贷利率查询**
   - 启用网络搜索获取最新利率
   - 自动提供银行对比和来源链接

2. **政策解读**
   - 首次购房者补助政策
   - 印花税减免条件
   - 负扣税相关规定

3. **贷款申请指导**
   - 贷款流程步骤
   - 所需文件清单
   - 审批时间预估

## 🏗️ 项目结构

```
├── app.py                      # 🎨 Streamlit 主应用
├── config.py                   # ⚙️ 配置管理
├── requirements.txt            # 📦 依赖包列表
├── .env.example               # 🔧 环境变量模板
├── .gitignore                 # 🚫 Git 忽略规则
│
├── .streamlit/
│   └── secrets.toml.example   # 🔐 Streamlit Cloud 配置示例
│
├── .github/
│   └── workflows/
│       └── test.yml           # 🧪 GitHub Actions 测试
│
├── prompts/
│   └── broker_system.en.md    # 🇺🇸 英文系统提示词（统一使用；输出为简体中文）
│
├── utils/
│   ├── unified_client.py      # 🤖 OpenAI API 客户端
│   ├── broker_logic.py        # 🧠 对话逻辑控制器
│   └── web_search.py          # 🔍 网络搜索功能
│
└── archive/
    └── rag/                   # 📚 RAG 功能归档（可选）
```

## 🔧 技术栈

- **前端**: Streamlit (Python Web 框架)
- **AI**: OpenAI GPT-4o-mini
- **搜索**: DuckDuckGo (默认免费) / Google Serper API (可选)
- **部署**: Streamlit Cloud / GitHub Pages
- **语言**: Python 3.11+

## 🌐 网络搜索说明

### 为什么需要网络搜索？
OpenAI API本身**不提供实时网络搜索功能**：
- 📅 **知识截止**: GPT模型训练数据有时间限制，无法获取最新信息
- 🏦 **实时性需求**: 房贷利率、政策变化需要最新数据
- 🔍 **信息验证**: 提供来源链接，增强答案可信度

### 🆓 默认方案：DuckDuckGo（推荐）
- ✅ **完全免费**: 无需任何API密钥
- ✅ **隐私友好**: 不追踪用户搜索
- ✅ **澳洲优化**: 自动使用澳洲地区搜索
- ✅ **开箱即用**: 安装依赖即可使用
- ⚡ **智能查询**: 自动添加澳洲房贷相关关键词

### 💰 升级选项：Google Serper（可选）
- ✅ **更高质量**: 基于Google搜索结果
- ✅ **更快速度**: API响应更稳定
- 💰 **按量付费**: 1000次搜索约$5 USD
- 🔧 **简单配置**: 只需添加`SERPER_API_KEY`

### 🔄 智能降级机制
系统会按以下优先级自动选择：
1. **Google Serper** (如果配置了`SERPER_API_KEY`)
2. **DuckDuckGo** (始终可用，无需配置)
3. **Mock数据** (网络不可用时的备用方案)

## ⚡ 性能优化

- **懒加载**: 非必需组件按需初始化
- **缓存**: Streamlit 原生缓存优化
- **错误处理**: 智能重试和降级机制
- **响应式**: 移动端适配

## 🧪 测试

```bash
# 运行基础测试
python -c "from config import validate_environment; print(validate_environment())"

# 测试启动性能
python test_startup_performance.py

# 测试基础功能
python test_multi_provider.py
```

## ❓ 常见问题

### 部署相关

**Q: Streamlit Cloud 部署失败？**
A: 检查以下项目：
1. 确保 `requirements.txt` 包含所有依赖
2. 在 Secrets 中正确配置 `OPENAI_API_KEY`
3. 确认 GitHub 仓库是公开的
4. 检查 Python 版本兼容性（推荐 3.11）

**Q: API 调用失败？**
A: 
1. 验证 OpenAI API 密钥有效性
2. 检查账户余额是否充足
3. 确认网络连接正常
4. 查看 Streamlit Cloud 日志

**Q: 网络搜索不工作？**
A:
1. **默认使用DuckDuckGo**: 无需任何配置，自动启用免费搜索
2. **网络连接问题**: 检查网络是否正常，防火墙设置
3. **依赖包问题**: 确保`ddgs`已正确安装（已在 requirements.txt 中）
4. **备用方案**: 即使网络搜索失败，也会显示内置的Mock数据
5. **升级选项**: 可配置`SERPER_API_KEY`获得更高质量的Google搜索结果

### 功能相关

**Q: 如何切换模型？**
A: 在 Streamlit Cloud Secrets 中修改 `MODEL_NAME`，支持：
- `gpt-4o-mini` (默认，成本低)
- `gpt-4o` (更强性能)
- `gpt-3.5-turbo` (兼容选项)

**Q: 支持其他语言吗？**
A: 当前支持中文和英文，可在 `prompts/` 目录添加其他语言的系统提示词。

**Q: 如何添加知识库功能？**
A: RAG 功能已归档到 `archive/rag/`，如需启用请参考归档文档。

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献方式
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发建议
- 遵循现有代码风格
- 添加必要的注释和文档
- 测试新功能的兼容性
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Streamlit 文档](https://docs.streamlit.io/)
- [Serper API 文档](https://serper.dev/api-documentation)
- [部署到 Streamlit Cloud](https://share.streamlit.io/)

## 📞 支持

如有问题或建议，请：
1. 查看 [常见问题](#-常见问题)
2. 搜索现有 [Issues](https://github.com/henrywen98/AustraliaMortgageBrokerChatBOT/issues)
3. 创建新的 Issue 描述问题

---

**🎉 现在就开始使用吧！点击上方的 "Deploy to Streamlit" 按钮，几分钟内拥有您的专属澳洲房贷AI助手！**
