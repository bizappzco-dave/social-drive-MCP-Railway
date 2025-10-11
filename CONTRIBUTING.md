# 贡献指南

感谢您对 Image Analyzer MCP Server 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请：

1. 检查 [Issues](https://github.com/your-username/img_mcp/issues) 是否已有相关问题
2. 如果没有，请创建新的 Issue
3. 提供详细的信息：
   - 问题描述
   - 复现步骤
   - 环境信息（操作系统、Python 版本、Ollama 版本等）
   - 错误日志（如有）

### 提交代码

1. **Fork** 本项目
2. **创建特性分支**：
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **提交更改**：
   ```bash
   git commit -m 'Add some feature: description'
   ```
4. **推送到分支**：
   ```bash
   git push origin feature/your-feature-name
   ```
5. **创建 Pull Request**

## 📝 开发规范

### 代码风格

- 使用 Python 3.8+ 语法
- 遵循 PEP 8 代码风格
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串

### 提交信息格式

使用约定式提交格式：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(analysis): add support for WebP image format

- Add WebP format detection
- Update image processing pipeline
- Add format conversion tests

Closes #123
```

### 测试

在提交代码前，请确保：

1. 代码能正常运行
2. 没有语法错误
3. 功能按预期工作
4. 添加了相应的测试（如需要）

## 🏗️ 项目结构

```
img_mcp/
├── image_analyzer_server.py  # 主服务器文件
├── ollama_client.py          # Ollama 客户端封装
├── requirements.txt          # Python 依赖
├── setup.py                 # 安装配置
├── .env.example             # 环境变量示例
├── .gitignore               # Git 忽略文件
├── README.md                # 项目文档
├── LICENSE                  # 许可证
├── CONTRIBUTING.md          # 贡献指南
└── examples/                # 使用示例
    ├── README.md
    └── basic_usage.py
```

## 🔧 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/your-username/img_mcp.git
cd img_mcp
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置您的环境
```

### 5. 启动开发服务器

```bash
python image_analyzer_server.py
```

## 📋 贡献类型

我们欢迎以下类型的贡献：

### 🐛 Bug 修复
- 修复现有功能的问题
- 改进错误处理
- 优化性能

### ✨ 新功能
- 添加新的图片分析功能
- 支持新的图片格式
- 增强现有工具的功能

### 📚 文档改进
- 改进 README.md
- 添加使用示例
- 完善 API 文档
- 翻译文档

### 🧪 测试
- 添加单元测试
- 改进测试覆盖率
- 添加集成测试

### 🎨 用户体验
- 改进错误信息
- 优化日志输出
- 改进配置选项

## 🚀 Pull Request 流程

### 1. 准备工作

- 确保您的分支是最新的：
  ```bash
  git checkout main
  git pull upstream main
  git checkout your-branch
  git rebase main
  ```

- 运行测试确保没有回归

### 2. 提交 PR

- 使用清晰的标题描述更改
- 在描述中详细说明：
  - 更改的目的
  - 实现的方法
  - 如何测试
  - 相关 Issue

### 3. 代码审查

- 响应审查意见
- 进行必要的修改
- 保持专业和友好的沟通

### 4. 合并

- 维护者会审查并合并 PR
- 合并后会删除特性分支

## 🏆 贡献者认可

所有贡献者都会在项目中得到认可：

- 在 README.md 中列出主要贡献者
- 在发布说明中感谢贡献者
- 在代码提交历史中保留贡献记录

## 📞 联系方式

如有疑问，请通过以下方式联系：

- 创建 [Issue](https://github.com/your-username/img_mcp/issues)
- 发起 [Discussion](https://github.com/your-username/img_mcp/discussions)
- 邮件：your-email@example.com

## 📄 许可证

通过贡献代码，您同意您的贡献将在 [MIT 许可证](LICENSE) 下发布。

---

感谢您的贡献！🎉
