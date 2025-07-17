#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主应用类
齐齐哈尔大学教务系统查询工具的主应用程序
"""

import os
import sys
import logging
from typing import Optional
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 导入模块
from .core.config import ensure_directories, get_config
from .utils.font_manager import init_fonts
from .utils.memory_manager import get_memory_manager, optimize_memory
from .utils.helpers import clean_history_files
from .ui.screens import MainScreen, LoginScreen, QueryScoresScreen, SwitchAccountScreen, NetworkScreen, ConfigScreen
from .ui.themes import set_theme, get_device_type

class EducationSystemApp(App):
    """齐齐哈尔大学教务系统查询工具主应用"""
    
    def __init__(self, **kwargs):
        super(EducationSystemApp, self).__init__(**kwargs)
        
        # 应用信息
        self.title = '齐齐哈尔大学教务系统查询工具'
        self.icon = 'assets/icons/app_icon.png' if os.path.exists('assets/icons/app_icon.png') else None
        
        # 屏幕实例
        self.main_screen: Optional[MainScreen] = None
        self.login_screen: Optional[LoginScreen] = None
        self.query_scores_screen: Optional[QueryScoresScreen] = None
        self.switch_account_screen: Optional[SwitchAccountScreen] = None
        self.network_screen: Optional[NetworkScreen] = None
        self.config_screen: Optional[ConfigScreen] = None
        
        # 内存管理器
        self.memory_manager = get_memory_manager()
        
        # 初始化标志
        self._initialized = False
    
    def build(self):
        """构建应用界面"""
        try:
            # 初始化应用
            self._initialize_app()
            
            # 创建根布局
            self.root = BoxLayout()
            
            # 显示主界面
            self.show_main_screen()
            
            return self.root
            
        except Exception as e:
            logger.error(f"构建应用界面时出错: {e}")
            # 显示错误界面
            error_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
            error_label = Label(
                text=f"应用初始化失败:\n{str(e)}\n\n请检查配置并重启应用",
                color=[1, 0, 0, 1],
                halign='center',
                valign='middle'
            )
            error_label.bind(size=error_label.setter('text_size'))
            error_layout.add_widget(error_label)
            return error_layout
    
    def _initialize_app(self):
        """初始化应用"""
        if self._initialized:
            return
        
        logger.info("正在初始化应用...")
        
        try:
            # 确保必要目录存在
            ensure_directories()
            
            # 清理历史文件
            clean_history_files()
            
            # 初始化字体
            font_success = init_fonts()
            if font_success:
                logger.info("字体初始化成功")
            else:
                logger.warning("字体初始化失败，可能影响中文显示")
            
            # 设置窗口属性
            self._setup_window()
            
            # 设置主题
            device_type = get_device_type()
            logger.info(f"检测到设备类型: {device_type}")
            
            # 根据设备类型设置主题（可以根据需要调整）
            set_theme(dark_mode=False)  # 默认使用亮色主题
            
            # 优化内存设置
            optimize_memory()
            
            self._initialized = True
            logger.info("应用初始化完成")
            
        except Exception as e:
            logger.error(f"应用初始化失败: {e}")
            raise
    
    def _setup_window(self):
        """设置窗口属性"""
        try:
            # 设置窗口大小
            window_width = get_config("WINDOW_WIDTH", 400)
            window_height = get_config("WINDOW_HEIGHT", 600)
            min_width = get_config("MIN_WINDOW_WIDTH", 350)
            min_height = get_config("MIN_WINDOW_HEIGHT", 500)
            
            # 根据设备类型调整窗口大小
            device_type = get_device_type()
            if device_type == 'desktop':
                # 桌面端适当放大窗口
                window_width = int(window_width * 1.2)
                window_height = int(window_height * 1.2)
            
            Window.size = (window_width, window_height)
            Window.minimum_width = min_width
            Window.minimum_height = min_height
            
            # 设置窗口居中
            Window.left = (Window.system_size[0] - window_width) // 2
            Window.top = (Window.system_size[1] - window_height) // 2
            
            logger.info(f"窗口大小设置为: {window_width}x{window_height}")
            
        except Exception as e:
            logger.warning(f"设置窗口属性时出错: {e}")
    
    def _ensure_screen(self, screen_name: str):
        """确保指定界面已创建"""
        try:
            if screen_name == 'main' and self.main_screen is None:
                self.main_screen = MainScreen(self)
                logger.debug("主界面已创建")
            elif screen_name == 'login' and self.login_screen is None:
                self.login_screen = LoginScreen(self)
                logger.debug("登录界面已创建")
            elif screen_name == 'switch' and self.switch_account_screen is None:
                self.switch_account_screen = SwitchAccountScreen(self)
                logger.debug("账号切换界面已创建")
            elif screen_name == 'query' and self.query_scores_screen is None:
                self.query_scores_screen = QueryScoresScreen(self)
                logger.debug("成绩查询界面已创建")
            elif screen_name == 'network' and self.network_screen is None:
                self.network_screen = NetworkScreen(self)
                logger.debug("网络设置界面已创建")
            elif screen_name == 'config' and self.config_screen is None:
                self.config_screen = ConfigScreen(self)
                logger.debug("配置管理界面已创建")
        except Exception as e:
            logger.error(f"创建界面 {screen_name} 时出错: {e}")
            raise
    
    def show_main_screen(self):
        """显示主界面"""
        try:
            self._ensure_screen('main')
            self.main_screen.update_account_info()
            self.root.clear_widgets()
            self.root.add_widget(self.main_screen)
            
            # 清理内存
            self.memory_manager.cleanup_textures()
            logger.debug("已显示主界面")
            
        except Exception as e:
            logger.error(f"显示主界面时出错: {e}")
            self._show_error_screen(f"显示主界面失败: {str(e)}")
    
    def show_login_screen(self):
        """显示登录界面"""
        try:
            self._ensure_screen('login')
            self.root.clear_widgets()
            self.root.add_widget(self.login_screen)
            logger.debug("已显示登录界面")
            
        except Exception as e:
            logger.error(f"显示登录界面时出错: {e}")
            self._show_error_screen(f"显示登录界面失败: {str(e)}")
    
    def show_switch_account_screen(self):
        """显示切换账号界面"""
        try:
            self._ensure_screen('switch')
            self.switch_account_screen.refresh_accounts()
            self.root.clear_widgets()
            self.root.add_widget(self.switch_account_screen)
            logger.debug("已显示账号切换界面")
            
        except Exception as e:
            logger.error(f"显示账号切换界面时出错: {e}")
            self._show_error_screen(f"显示账号切换界面失败: {str(e)}")
    
    def show_query_scores_screen(self):
        """显示成绩查询界面"""
        try:
            self._ensure_screen('query')
            self.root.clear_widgets()
            self.root.add_widget(self.query_scores_screen)
            logger.debug("已显示成绩查询界面")

        except Exception as e:
            logger.error(f"显示成绩查询界面时出错: {e}")
            self._show_error_screen(f"显示成绩查询界面失败: {str(e)}")

    def show_network_screen(self):
        """显示网络设置界面"""
        try:
            self._ensure_screen('network')
            self.root.clear_widgets()
            self.root.add_widget(self.network_screen)
            logger.debug("已显示网络设置界面")

        except Exception as e:
            logger.error(f"显示网络设置界面时出错: {e}")
            self._show_error_screen(f"显示网络设置界面失败: {str(e)}")

    def show_config_screen(self):
        """显示配置管理界面"""
        try:
            self._ensure_screen('config')
            self.root.clear_widgets()
            self.root.add_widget(self.config_screen)
            logger.debug("已显示配置管理界面")

        except Exception as e:
            logger.error(f"显示配置管理界面时出错: {e}")
            self._show_error_screen(f"显示配置管理界面失败: {str(e)}")
    
    def _show_error_screen(self, error_message: str):
        """显示错误界面"""
        try:
            self.root.clear_widgets()
            error_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
            
            error_label = Label(
                text=f"错误:\n{error_message}\n\n请重启应用或联系技术支持",
                color=[1, 0, 0, 1],
                halign='center',
                valign='middle'
            )
            error_label.bind(size=error_label.setter('text_size'))
            
            error_layout.add_widget(error_label)
            self.root.add_widget(error_layout)
            
        except Exception as e:
            logger.critical(f"显示错误界面时也出错了: {e}")
    
    def on_stop(self):
        """应用退出时的清理工作"""
        try:
            logger.info("正在清理应用资源...")
            
            # 清理内存管理器
            if hasattr(self, 'memory_manager'):
                self.memory_manager.cleanup()
            
            # 清理临时文件
            clean_history_files()
            
            logger.info("应用资源清理完成")
            
        except Exception as e:
            logger.error(f"清理应用资源时出错: {e}")
    
    def on_pause(self):
        """应用暂停时的处理"""
        logger.info("应用已暂停")
        return True
    
    def on_resume(self):
        """应用恢复时的处理"""
        logger.info("应用已恢复")
        # 可以在这里添加恢复时的逻辑，比如刷新数据等
