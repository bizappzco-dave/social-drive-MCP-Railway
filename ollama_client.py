"""
Ollama客户端模块
用于与本地Ollama服务交互，调用gemma3:12b模型进行图片分析
"""

import os
import base64
import requests
import logging
import traceback
from typing import Optional, Dict, Any
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables (but don't override Railway env vars)
if os.path.exists('.env') and not os.getenv('RAILWAY_ENVIRONMENT'):
    load_dotenv()

# 获取日志记录器
logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama客户端类"""
    
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        初始化Ollama客户端
        
        Args:
            base_url: Ollama服务基础URL
            model: 使用的模型名称
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma3:12b")
        self.timeout = int(os.getenv("OLLAMA_REQUEST_TIMEOUT", "180"))
        self.session = requests.Session()
        
        logger.info(f"初始化Ollama客户端")
        logger.info(f"  - 基础URL: {self.base_url}")
        logger.info(f"  - 模型: {self.model}")
        logger.info(f"  - 请求超时: {self.timeout}秒")
        
    def health_check(self) -> bool:
        """
        检查Ollama服务是否健康
        
        Returns:
            bool: 服务是否可用
        """
        logger.debug(f"检查Ollama服务健康状态: {self.base_url}/api/tags")
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.debug("Ollama服务健康检查通过")
                return True
            else:
                logger.warning(f"Ollama服务健康检查失败，状态码: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"Ollama服务健康检查异常: {e}")
            logger.debug(f"异常详情: {traceback.format_exc()}")
            return False
    
    def list_models(self) -> Dict[str, Any]:
        """
        获取可用模型列表
        
        Returns:
            Dict: 模型列表信息
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"获取模型列表失败: {e}")
    
    def encode_image(self, image_path: str) -> str:
        """
        将图片编码为base64字符串
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            str: base64编码的图片数据
        """
        try:
            with Image.open(image_path) as img:
                # 转换为RGB格式（如果需要）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 调整图片大小以减少token消耗
                max_size = 1024
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # 保存到字节流
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=85)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return img_str
        except Exception as e:
            raise Exception(f"图片编码失败: {e}")
    
    def analyze_image(self, image_path: str, prompt: str = "请详细描述这张图片的内容") -> Dict[str, Any]:
        """
        使用gemma3:12b模型分析图片
        
        Args:
            image_path: 图片文件路径
            prompt: 分析提示词
            
        Returns:
            Dict: 分析结果
        """
        logger.info(f"开始分析图片: {image_path}")
        logger.debug(f"使用模型: {self.model}")
        logger.debug(f"提示词长度: {len(prompt)} 字符")
        
        try:
            # 检查服务健康状态
            logger.debug("检查Ollama服务健康状态...")
            if not self.health_check():
                logger.error("Ollama服务不可用，请确保服务正在运行")
                raise Exception("Ollama服务不可用，请确保服务正在运行")
            
            logger.info("Ollama服务健康检查通过")
            
            # 编码图片
            logger.debug("开始编码图片...")
            image_data = self.encode_image(image_path)
            logger.debug(f"图片编码完成，base64数据长度: {len(image_data)}")
            
            # 构建请求
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }
            logger.debug(f"构建请求负载，模型: {self.model}")
            logger.debug(f"请求URL: {self.base_url}/api/generate")
            
            # 发送请求
            logger.info("发送图片分析请求到Ollama服务...")
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout  # 使用环境变量配置的超时时间
            )
            
            logger.debug(f"收到响应，状态码: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            logger.info("图片分析请求成功完成")
            logger.debug(f"响应数据键: {list(result.keys())}")
            logger.debug(f"分析完成状态: {result.get('done', False)}")
            logger.debug(f"总耗时: {result.get('total_duration', 0)}ms")
            logger.debug(f"提示词评估数量: {result.get('prompt_eval_count', 0)}")
            logger.debug(f"生成数量: {result.get('eval_count', 0)}")
            
            return {
                "success": True,
                "model": self.model,
                "response": result.get("response", ""),
                "done": result.get("done", False),
                "total_duration": result.get("total_duration", 0),
                "prompt_eval_count": result.get("prompt_eval_count", 0),
                "eval_count": result.get("eval_count", 0)
            }
            
        except requests.RequestException as e:
            logger.error(f"请求Ollama服务失败: {e}")
            logger.debug(f"请求异常详情: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"请求Ollama服务失败: {e}"
            }
        except Exception as e:
            logger.error(f"图片分析过程中发生异常: {e}")
            logger.error(f"异常堆栈: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_image_with_categories(self, image_path: str, categories: list = None) -> Dict[str, Any]:
        """
        按指定类别分析图片
        
        Args:
            image_path: 图片文件路径
            categories: 分析类别列表
            
        Returns:
            Dict: 分类分析结果
        """
        if categories is None:
            categories = ["物体识别", "场景描述", "颜色分析", "文字内容", "情感氛围"]
        
        prompt = f"""请从以下几个方面分析这张图片：
{chr(10).join([f"{i+1}. {cat}" for i, cat in enumerate(categories)])}

请为每个方面提供详细的分析结果。"""
        
        return self.analyze_image(image_path, prompt)
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        从图片中提取文字内容
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Dict: 文字提取结果
        """
        prompt = """请仔细观察这张图片，提取其中的所有文字内容。
包括：
1. 图片中可见的文字
2. 标题、标签、说明文字
3. 如果有表格或列表，请完整提取
4. 注意文字的语言和格式

如果没有发现文字，请明确说明。"""
        
        return self.analyze_image(image_path, prompt)


# 便捷函数
def create_client() -> OllamaClient:
    """创建Ollama客户端实例"""
    return OllamaClient()


if __name__ == "__main__":
    # 测试代码
    client = OllamaClient()
    
    # 检查服务状态
    if client.health_check():
        print("✅ Ollama服务运行正常")
        
        # 列出可用模型
        models = client.list_models()
        print(f"📋 可用模型: {models}")
        
        # 如果有测试图片，可以测试分析功能
        # result = client.analyze_image("test.jpg")
        # print(f"🔍 分析结果: {result}")
    else:
        print("❌ Ollama服务不可用，请检查服务是否启动")
