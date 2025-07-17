#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
齐齐哈尔大学教务系统查询工具
主入口文件 - 重构版本

作者: Education System Team
版本: 2.0.0
描述: 现代化、模块化的教务系统查询工具
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """设置日志系统"""
    # 确保日志目录存在
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 配置日志处理器
    handlers = [
        logging.StreamHandler(sys.stdout),  # 控制台输出
        logging.FileHandler(log_dir / "app.log", encoding='utf-8')  # 文件输出
    ]

    # 设置日志级别
    log_level = logging.DEBUG if os.getenv('DEBUG', '').lower() == 'true' else logging.INFO

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )

    # 设置第三方库的日志级别
    logging.getLogger('kivy').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

def check_dependencies():
    """检查必要的依赖"""
    required_packages = {
        'kivy': 'kivy',
        'requests': 'requests',
        'beautifulsoup4': 'bs4',  # beautifulsoup4包的导入名是bs4
        'pillow': 'PIL'           # pillow包的导入名是PIL
    }

    missing_packages = []

    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print(f"错误: 缺少必要的依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖:")
        print(f"pip install {' '.join(missing_packages)}")
        sys.exit(1)

def setup_environment():
    """设置运行环境"""
    # 设置Kivy配置
    os.environ['KIVY_NO_CONSOLELOG'] = '1'  # 禁用Kivy控制台日志

    # 设置窗口提供者（如果需要）
    if sys.platform.startswith('win'):
        os.environ['KIVY_WINDOW'] = 'sdl2'

    # 设置文本提供者
    os.environ['KIVY_TEXT'] = 'pil'

def print_banner():
    """打印应用横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                齐齐哈尔大学教务系统查询工具                    ║
║                    Education System Query Tool                ║
║                                                              ║
║                        版本: 2.0.0                          ║
║                     重构版 - 模块化设计                       ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """主函数"""
    try:
        # 打印横幅
        print_banner()

        # 设置日志
        setup_logging()
        logger = logging.getLogger(__name__)

        logger.info("=" * 60)
        logger.info("齐齐哈尔大学教务系统查询工具启动")
        logger.info("版本: 2.0.0 (重构版)")
        logger.info("=" * 60)

        # 检查依赖
        logger.info("检查依赖包...")
        check_dependencies()
        logger.info("依赖检查完成")

        # 设置环境
        logger.info("设置运行环境...")
        setup_environment()
        logger.info("环境设置完成")

        # 导入并启动应用
        logger.info("正在启动应用...")
        from src import EducationSystemApp

        app = EducationSystemApp()
        app.run()

        logger.info("应用已退出")

    except KeyboardInterrupt:
        print("\n用户中断，应用退出")
        sys.exit(0)
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请检查依赖包是否正确安装")
        sys.exit(1)
    except Exception as e:
        print(f"启动应用时发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()