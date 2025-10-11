"""
图片分析MCP服务器
使用FastMCP框架构建，提供图片分析工具
"""

import os
import json
import logging
import sys
import traceback
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from fastmcp import FastMCP, Context
from ollama_client import OllamaClient, create_client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志系统
def setup_logging():
    """设置详细的日志配置"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 设置日志文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"image_analyzer_mcp_{timestamp}.log"
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logging.info(f"日志系统初始化完成，日志文件: {log_file}")
    logging.info(f"日志级别: {log_level}")
    
    return log_file

# 初始化日志系统
log_file = setup_logging()
logger = logging.getLogger(__name__)

# 记录服务器启动信息
logger.info("=" * 50)
logger.info("图片分析MCP服务器正在初始化...")
logger.info(f"Python版本: {sys.version}")
logger.info(f"当前工作目录: {os.getcwd()}")
logger.info(f"环境变量:")
for key, value in os.environ.items():
    if key.startswith(('OLLAMA_', 'MCP_', 'LOG_')):
        logger.info(f"  {key}: {value}")

# 创建MCP服务器实例
try:
    mcp = FastMCP(
        name=os.getenv("MCP_SERVER_NAME", "Image Analyzer MCP"),
        version=os.getenv("MCP_SERVER_VERSION", "1.0.0")
    )
    logger.info("MCP服务器实例创建成功")
except Exception as e:
    logger.error(f"创建MCP服务器实例失败: {e}")
    logger.error(f"详细错误: {traceback.format_exc()}")
    raise

# 全局Ollama客户端
ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """获取Ollama客户端实例"""
    global ollama_client
    try:
        if ollama_client is None:
            logger.info("正在创建Ollama客户端...")
            ollama_client = create_client()
            logger.info(f"Ollama客户端创建成功 - URL: {ollama_client.base_url}, Model: {ollama_client.model}")
        return ollama_client
    except Exception as e:
        logger.error(f"创建Ollama客户端失败: {e}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        raise


@mcp.tool()
def analyze_image(image_path: str, prompt: str = "请详细描述这张图片的内容") -> Dict[str, Any]:
    """
    分析图片内容
    
    Args:
        image_path: 图片文件的路径（支持jpg, jpeg, png, bmp, tiff等格式）
        prompt: 分析提示词，用于指导模型分析的重点
    
    Returns:
        Dict: 包含分析结果和元数据的字典
    """
    logger.info(f"开始分析图片: {image_path}")
    logger.debug(f"分析提示词: {prompt}")
    
    try:
        # 验证图片文件存在
        if not os.path.exists(image_path):
            logger.error(f"图片文件不存在: {image_path}")
            return {
                "success": False,
                "error": f"图片文件不存在: {image_path}"
            }
        
        logger.info(f"图片文件验证通过: {image_path}")
        
        # 获取Ollama客户端
        logger.debug("获取Ollama客户端...")
        client = get_ollama_client()
        
        # 分析图片
        logger.info("开始调用Ollama分析图片...")
        result = client.analyze_image(image_path, prompt)
        
        if result.get("success", False):
            logger.info(f"图片分析成功完成: {image_path}")
            logger.debug(f"分析结果长度: {len(result.get('response', ''))}")
        else:
            logger.error(f"图片分析失败: {result.get('error', '未知错误')}")
        
        return result
        
    except Exception as e:
        logger.error(f"分析图片时发生异常: {e}")
        logger.error(f"异常堆栈: {traceback.format_exc()}")
        return {
            "success": False,
            "error": f"分析图片时发生错误: {str(e)}"
        }


@mcp.tool()
def analyze_image_categories(image_path: str, categories: List[str] = None) -> Dict[str, Any]:
    """
    按指定类别分析图片（专为UI/UX设计优化）
    
    Args:
        image_path: 图片文件的路径
        categories: 分析类别列表，如["布局结构", "组件识别", "色彩方案", "文字内容", "交互元素"]
    
    Returns:
        Dict: 分类分析结果
    """
    try:
        if categories is None:
            categories = ["布局结构", "组件识别", "色彩方案", "文字内容", "交互元素", "设计风格"]
        
        client = get_ollama_client()
        result = client.analyze_image_with_categories(image_path, categories)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"分类分析图片时发生错误: {str(e)}"
        }


@mcp.tool()
def extract_text_from_image(image_path: str) -> Dict[str, Any]:
    """
    从图片中提取文字内容（OCR功能）
    
    Args:
        image_path: 图片文件的路径
    
    Returns:
        Dict: 提取的文字内容
    """
    try:
        client = get_ollama_client()
        result = client.extract_text_from_image(image_path)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"提取图片文字时发生错误: {str(e)}"
        }


@mcp.tool()
def check_ollama_status() -> Dict[str, Any]:
    """
    检查Ollama服务状态
    
    Returns:
        Dict: 服务状态信息
    """
    try:
        client = get_ollama_client()
        
        # 检查健康状态
        is_healthy = client.health_check()
        
        if is_healthy:
            # 获取模型列表
            models = client.list_models()
            return {
                "success": True,
                "status": "healthy",
                "base_url": client.base_url,
                "current_model": client.model,
                "available_models": models.get("models", [])
            }
        else:
            return {
                "success": False,
                "status": "unhealthy",
                "error": "Ollama服务不可用，请检查服务是否启动"
            }
            
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": f"检查服务状态时发生错误: {str(e)}"
        }


@mcp.tool()
def list_supported_formats() -> Dict[str, Any]:
    """
    列出支持的图片格式
    
    Returns:
        Dict: 支持的图片格式列表
    """
    return {
        "success": True,
        "supported_formats": [
            "JPEG (.jpg, .jpeg)",
            "PNG (.png)",
            "BMP (.bmp)",
            "TIFF (.tiff, .tif)",
            "GIF (.gif)",
            "WebP (.webp)"
        ],
        "note": "所有格式都会自动转换为JPEG进行分析以优化性能"
    }


@mcp.resource("config://ollama")
def get_ollama_config() -> str:
    """
    获取Ollama配置信息
    
    Returns:
        str: JSON格式的配置信息
    """
    config = {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "model": os.getenv("OLLAMA_MODEL", "gemma3:12b"),
        "server_name": os.getenv("MCP_SERVER_NAME", "Image Analyzer MCP"),
        "version": os.getenv("MCP_SERVER_VERSION", "1.0.0")
    }
    return json.dumps(config, indent=2, ensure_ascii=False)


@mcp.prompt()
def image_analysis_prompt(image_path: str, analysis_type: str = "ui_overview") -> str:
    """
    生成图片分析提示词（专门用于UI/UX开发辅助）
    
    Args:
        image_path: 图片路径
        analysis_type: 分析类型 (ui_overview, layout_analysis, component_analysis, 
                       design_system, accessibility, responsive_design, code_generation)
    
    Returns:
        str: 分析提示词
    """
    prompts = {
        "ui_overview": """请分析这个APP/网站界面的整体设计。重点关注：
1. 界面类型和用途（移动端APP、网页、桌面应用等）
2. 主要功能区域和导航结构
3. 整体设计风格和视觉层次
4. 用户体验和交互特点
5. 技术实现可能涉及的前端框架或组件库""",
        
        "layout_analysis": """请详细分析这个界面的布局设计。重点关注：
1. 布局结构（网格系统、Flexbox、绝对定位等）
2. 响应式设计考虑和断点
3. 组件间的间距和对齐方式
4. 信息架构和内容层次
5. 可复用的布局模式""",
        
        "component_analysis": """请识别并分析这个界面中的UI组件。重点关注：
1. 可识别的UI组件（按钮、输入框、卡片、导航等）
2. 组件的样式特征（颜色、字体、圆角、阴影等）
3. 组件的交互状态（默认、悬停、激活、禁用等）
4. 组件的变体和尺寸规格
5. 可以抽象为设计系统组件的元素""",
        
        "design_system": """请从这个界面中提取设计系统规范。重点关注：
1. 色彩方案（主色、辅助色、状态色、中性色）
2. 字体系统（字号、行高、字重、字体族）
3. 间距系统（内外边距的规律和比例）
4. 圆角、阴影、边框等装饰元素规范
5. 图标系统和插画风格""",
        
        "accessibility": """请分析这个界面的无障碍设计。重点关注：
1. 颜色对比度和可读性
2. 文字大小和行高的合理性
3. 交互元素的可达性和可识别性
4. 可能存在的无障碍问题和改进建议
5. 符合WCAG标准的程度评估""",
        
        "responsive_design": """请分析这个界面的响应式设计策略。重点关注：
1. 当前显示尺寸的适配情况
2. 元素在不同屏幕尺寸下的可能变化
3. 断点设计和布局切换策略
4. 图片和媒体的自适应处理
5. 移动端和桌面端的差异化设计""",
        
        "code_generation": """请为这个界面生成前端代码实现建议。重点关注：
1. HTML结构建议和语义化标签
2. CSS布局方案和样式实现
3. JavaScript交互逻辑和事件处理
4. 适合的前端框架选择（React、Vue、Angular等）
5. 组件拆分和代码组织建议"""
    }
    
    base_prompt = prompts.get(analysis_type, prompts["ui_overview"])
    return f"""请分析图片路径: {image_path}

这是一个UI/UX界面分析任务，主要用于辅助前端开发工作。

{base_prompt}

请提供结构化、详细的分析结果，尽可能包含具体的技术实现建议和代码示例。"""


@mcp.tool()
def batch_analyze_images(image_paths: List[str], prompt: str = "请简要描述每张图片的内容") -> Dict[str, Any]:
    """
    批量分析多张图片
    
    Args:
        image_paths: 图片文件路径列表
        prompt: 分析提示词
    
    Returns:
        Dict: 批量分析结果
    """
    try:
        results = []
        client = get_ollama_client()
        
        for i, image_path in enumerate(image_paths):
            try:
                if not os.path.exists(image_path):
                    results.append({
                        "index": i,
                        "path": image_path,
                        "success": False,
                        "error": "文件不存在"
                    })
                    continue
                
                result = client.analyze_image(image_path, prompt)
                result["index"] = i
                result["path"] = image_path
                results.append(result)
                
            except Exception as e:
                results.append({
                    "index": i,
                    "path": image_path,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_images": len(image_paths),
            "successful_analyses": sum(1 for r in results if r.get("success", False)),
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"批量分析时发生错误: {str(e)}"
        }


if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("图片分析MCP服务器启动中...")
        
        # 设置控制台输出编码
        if sys.platform == "win32":
            import locale
            try:
                # 尝试设置UTF-8编码
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            except:
                # 如果失败，使用ASCII字符
                pass
        
        print("启动图片分析MCP服务器...")
        print("可用工具:")
        print("  - analyze_image: 分析图片内容")
        print("  - analyze_image_categories: 按类别分析图片")
        print("  - extract_text_from_image: 提取图片文字")
        print("  - check_ollama_status: 检查服务状态")
        print("  - list_supported_formats: 列出支持格式")
        print("  - batch_analyze_images: 批量分析图片")
        print("可用资源:")
        print("  - config://ollama: 获取配置信息")
        print("可用提示:")
        print("  - image_analysis_prompt: 生成分析提示词")
        print(f"日志文件: {log_file}")
        print()
        
        logger.info("所有组件初始化完成，准备启动MCP服务器...")
        
        # 启动服务器
        logger.info("正在启动MCP服务器...")
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
        print("\n服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        print(f"服务器启动失败: {e}")
        print(f"详细日志请查看: {log_file}")
        sys.exit(1)
