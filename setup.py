"""
Image Analyzer MCP Server 安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="image-analyzer-mcp",
    version="1.0.0",
    author="Image Analyzer MCP Team",
    author_email="your-email@example.com",
    description="一个基于本地 Ollama 服务的图片分析 MCP 服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/img_mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.example"],
    },
    keywords="mcp, ollama, image-analysis, ai, vision, ui-ux",
    project_urls={
        "Bug Reports": "https://github.com/your-username/img_mcp/issues",
        "Source": "https://github.com/your-username/img_mcp",
        "Documentation": "https://github.com/your-username/img_mcp/wiki",
    },
)
