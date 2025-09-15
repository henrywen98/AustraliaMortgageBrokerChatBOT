# 澳大利亚房贷AI助手 | Australian Mortgage Broker AI Assistant

面向澳洲房贷咨询的智能 AI 助手。基于 OpenAI GPT-5 mini（内置 Web Search 工具），提供权威来源引用与专业经纪人人设。系统提示使用英文，最终输出统一为简体中文。

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 核心特性

### 🤖 智能对话
- **OpenAI驱动**: 推荐使用 gpt-5-mini（内置 Web Search）
- **上下文记忆**: 多轮对话连贯性
- **专业角色**: 澳洲房贷经纪人人设
- **统一中文输出**: 无论输入语言如何，回答统一简体中文

### 🌐 内置网络搜索
- **实时信息**: 直接使用 GPT-5 mini 的 Web Search 工具
- **来源引用**: 在回答末尾附“参考来源/References”（模型会带链接）
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
   MODEL_NAME = "gpt-5-mini"  # 推荐：内置Web Search
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
   `streamlit run app.py`
   ```
   
5. **访问应用**
浏览器打开：http://localhost:8501

更多部署细节与常见问题，请见下文的“常见问题”章节。

## 📋 环境配置

### 必需配置
- `OPENAI_API_KEY`: OpenAI API 密钥（[获取地址](https://platform.openai.com/api-keys)）

### 可选配置
- `MODEL_NAME`: 模型名称（推荐: `gpt-5-mini`；兼容 `gpt-4o-mini`）

### Streamlit Cloud Secrets 示例
```toml
# 必需
OPENAI_API_KEY = "sk-..."

# 可选
MODEL_NAME = "gpt-5-mini"  # 推荐：内置Web Search
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
│   ├── unified_client.py      # 🤖 OpenAI API 客户端（GPT-5 mini 使用 Responses API + Web Search 工具）
│   └── broker_logic.py        # 🧠 对话逻辑控制器（模型内置搜索）
│
└── prompts/
```

## 🔧 技术栈

- **前端**: Streamlit (Python Web 框架)
- **AI**: OpenAI GPT-5 mini（内置 Web Search）
- **搜索**: 由模型内置 Web Search 工具完成
- **部署**: Streamlit Cloud / GitHub Pages
- **语言**: Python 3.11+

## 🌐 网络搜索说明

使用 GPT-5 mini 时，应用通过 Responses API 调用模型的 Web Search 工具完成在线检索与引用，无需额外搜索依赖或 API Key。关闭搜索开关时，仅使用模型自身知识回答。

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
1. 确认 `MODEL_NAME` 为 `gpt-5-mini` 或支持 Web Search 的同类模型
2. 检查 OpenAI API Key 权限与用量配额
3. 网络连通性与防火墙设置

### 功能相关

**Q: 如何切换模型？**
A: 在 Streamlit Cloud Secrets 中修改 `MODEL_NAME`，支持：
- `gpt-4o-mini` (默认，成本低)
- `gpt-4o` (更强性能)
- `gpt-3.5-turbo` (兼容选项)

**Q: 支持其他语言吗？**
A: 当前支持中文和英文，可在 `prompts/` 目录添加其他语言的系统提示词。

**Q: 是否支持外部知识库（RAG）？**
A: 正式版未内置 RAG；如需检索功能，建议直接依赖模型内置 Web Search 或在后续版本中单独扩展。

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
- [部署到 Streamlit Cloud](https://share.streamlit.io/)

## 📞 支持

如有问题或建议，请：
1. 查看 [常见问题](#-常见问题)
2. 搜索现有 [Issues](https://github.com/henrywen98/AustraliaMortgageBrokerChatBOT/issues)
3. 创建新的 Issue 描述问题

---

**🎉 现在就开始使用吧！点击上方的 "Deploy to Streamlit" 按钮，几分钟内拥有您的专属澳洲房贷AI助手！**
