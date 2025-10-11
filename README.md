# Image Analyzer MCP Server

基于本地 Ollama 服务的图片分析 MCP 工具，可直接在 Claude Desktop 等支持 MCP 的应用中使用，无需 API 密钥。

## 🎯 主要功能

- 🖼️ **图片分析** - 智能分析图片内容，支持多种格式
- 📄 **文字提取** - 从图片中提取文字内容（OCR）
- 🎨 **UI 分析** - 专门针对界面设计的分析功能
- 📦 **批量处理** - 一次分析多张图片
- 🔒 **隐私保护** - 完全本地运行，数据不上传

## 🚀 一分钟配置

### 第一步：安装 Ollama

```bash
# Windows: 从官网下载安装包
# https://ollama.ai/download

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

### 第二步：下载模型

```bash
# 启动 Ollama 服务
ollama serve

# 下载图片分析模型（约 7GB）
ollama pull gemma3:12b
```

### 第三步：配置 MCP 客户端

以 **Claude Desktop** 为例，编辑配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "image-analyzer": {
      "command": "python",
      "args": ["你的项目路径/image_analyzer_server.py"],
      "env": {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "gemma3:12b"
      }
    }
  }
}
```

**重要**: 将 `你的项目路径` 替换为实际的项目文件夹路径，例如：
- Windows: `F:/loen_space/img_mcp/image_analyzer_server.py`
- macOS: `/Users/username/img_mcp/image_analyzer_server.py`

### 第四步：重启 Claude Desktop

重启 Claude Desktop，即可开始使用图片分析功能！

## 📋 使用方法

配置完成后，在 Claude 中可以直接使用：

### 基础图片分析
```
请分析这张图片：[上传图片]
```

### UI 界面分析
```
请分析这个界面的设计布局和组件
```

### 提取图片文字
```
请提取这张图片中的所有文字
```

### 批量分析
```
请分析这几张图片：[上传多张图片]
```

## 🔧 可用工具

| 工具名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `analyze_image` | 基础图片分析 | 日常图片内容分析 |
| `analyze_image_categories` | 分类分析 | UI/UX 设计分析 |
| `extract_text_from_image` | 文字提取 | OCR 识别 |
| `batch_analyze_images` | 批量分析 | 处理多张图片 |
| `check_ollama_status` | 状态检查 | 检查服务状态 |
| `list_supported_formats` | 格式列表 | 查看支持格式 |

## ⚙️ 高级配置（可选）

如需自定义配置，可创建 `.env` 文件：

```env
# Ollama 服务地址（默认本地）
OLLAMA_BASE_URL=http://localhost:11434

# 使用模型（默认 gemma3:12b）
OLLAMA_MODEL=gemma3:12b

# 请求超时时间（秒）
OLLAMA_REQUEST_TIMEOUT=180

# 日志级别
LOG_LEVEL=INFO
```

## 🚨 常见问题

### Q: Claude 中找不到图片分析工具？
**A**: 检查以下几点：
1. Ollama 服务是否正在运行
2. 配置文件路径是否正确
3. 是否已重启 Claude Desktop
4. 查看 `logs/` 目录中的日志文件

### Q: 分析失败或报错？
**A**: 
1. 确保 `gemma3:12b` 模型已下载完成
2. 检查图片格式是否支持
3. 确认 Ollama 服务端口 11434 未被占用

### Q: 如何更换其他模型？
**A**: 
1. 下载新模型：`ollama pull 模型名`
2. 修改配置文件中的 `OLLAMA_MODEL`
3. 重启 Claude Desktop

### Q: 支持哪些图片格式？
**A**: 支持 JPEG、PNG、BMP、TIFF、GIF、WebP 等主流格式

## 📁 项目文件说明

```
img_mcp/
├── image_analyzer_server.py  # 主服务器文件（MCP 核心文件）
├── ollama_client.py          # Ollama 通信模块
├── requirements.txt          # Python 依赖包
├── .env.example             # 配置文件模板
└── README.md                # 使用说明
```

## 🔒 隐私说明

- ✅ 完全本地运行，图片数据不会离开您的设备
- ✅ 无需注册账号或 API 密钥
- ✅ 支持离线使用
- ✅ 无数据收集或上传

## 📞 获取帮助

如果遇到问题：

1. 查看 `logs/` 目录中的日志文件
2. 检查 Ollama 服务状态：`ollama list`
3. 确认模型是否正确下载：`ollama show gemma3:12b`

---

🎉 **配置完成后，您就可以在 Claude 中直接使用强大的图片分析功能了！**
