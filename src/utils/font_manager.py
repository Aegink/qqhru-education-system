#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体管理模块
处理中文字体和emoji图标的显示问题
"""

import os
import sys
import logging
from typing import Dict, Optional
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path

logger = logging.getLogger(__name__)

class FontManager:
    """字体管理器"""
    
    def __init__(self):
        self.font_registered = False
        self.emoji_supported = False
        self._icon_cache = {}
        self._button_text_cache = {}
        
    def register_fonts(self) -> bool:
        """注册字体"""
        # 添加字体资源路径
        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
        if os.path.exists(fonts_dir):
            resource_add_path(fonts_dir)
        
        # 尝试注册中文字体
        self._register_chinese_fonts()
        
        # 检查emoji支持
        self._check_emoji_support()
        
        return self.font_registered
    
    def _register_chinese_fonts(self) -> bool:
        """注册中文字体"""
        # 本地字体文件
        local_fonts = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'simhei.ttf'),
            'fonts/simhei.ttf',
            './fonts/simhei.ttf'
        ]
        
        # Windows系统字体
        windows_fonts = [
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/msyhbd.ttc'
        ]
        
        # Linux系统字体
        linux_fonts = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ]
        
        # macOS系统字体
        macos_fonts = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial Unicode MS.ttf'
        ]
        
        # 根据系统选择字体列表
        if sys.platform.startswith('win'):
            font_list = windows_fonts + local_fonts
        elif sys.platform.startswith('linux'):
            font_list = linux_fonts + local_fonts
        elif sys.platform.startswith('darwin'):
            font_list = macos_fonts + local_fonts
        else:
            font_list = local_fonts
        
        # 尝试注册第一个存在的字体
        for font_path in font_list:
            if os.path.exists(font_path):
                try:
                    LabelBase.register(DEFAULT_FONT, font_path)
                    logger.info(f"已加载字体: {font_path}")
                    self.font_registered = True
                    return True
                except Exception as e:
                    logger.warning(f"加载字体 {font_path} 失败: {e}")
        
        if not self.font_registered:
            logger.warning("警告: 未能加载任何中文字体，界面可能无法正确显示中文")
        
        return self.font_registered
    
    def _check_emoji_support(self) -> bool:
        """检查当前字体是否支持emoji"""
        # 这里可以添加emoji支持检测逻辑
        # 暂时设为False，使用文字替代方案
        self.emoji_supported = False
        return self.emoji_supported
    
    def get_icon_text(self, icon_type: str) -> str:
        """获取图标文本（emoji或文字替代）
        
        Args:
            icon_type: 图标类型
            
        Returns:
            图标文本
        """
        if icon_type in self._icon_cache:
            return self._icon_cache[icon_type]
        
        if self.emoji_supported:
            # 如果支持emoji，返回emoji图标
            emoji_map = {
                'refresh': '🔄',
                'login': '👤',
                'switch': '🔄',
                'query': '📊',
                'manage': '⚙️',
                'exit': '🚪',
                'checkbox_empty': '☐',
                'checkbox_checked': '☑',
                'success': '✅',
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️',
                'home': '🏠',
                'back': '⬅️',
                'forward': '➡️',
                'up': '⬆️',
                'down': '⬇️'
            }
            result = emoji_map.get(icon_type, '')
        else:
            # 如果不支持emoji，返回文字替代
            text_map = {
                'refresh': '刷新',
                'login': '登录',
                'switch': '切换',
                'query': '查询',
                'manage': '管理',
                'exit': '退出',
                'checkbox_empty': '□',
                'checkbox_checked': '■',
                'success': '成功',
                'error': '错误',
                'warning': '警告',
                'info': '信息',
                'home': '主页',
                'back': '返回',
                'forward': '前进',
                'up': '上',
                'down': '下'
            }
            result = text_map.get(icon_type, '')
        
        self._icon_cache[icon_type] = result
        return result
    
    def get_button_text(self, text_key: str) -> str:
        """获取按钮文本
        
        Args:
            text_key: 文本键
            
        Returns:
            按钮文本
        """
        if text_key in self._button_text_cache:
            return self._button_text_cache[text_key]
        
        button_texts = {
            'refresh': '刷新',
            'login_new': '登录新账号',
            'switch_account': '切换已保存账号',
            'query_scores': '查询本学期成绩',
            'manage_accounts': '管理账号',
            'exit_app': '退出应用',
            'confirm': '确认',
            'cancel': '取消',
            'ok': '确定',
            'yes': '是',
            'no': '否',
            'save': '保存',
            'delete': '删除',
            'edit': '编辑',
            'add': '添加',
            'remove': '移除',
            'clear': '清空',
            'reset': '重置',
            'submit': '提交',
            'close': '关闭',
            'back': '返回',
            'next': '下一步',
            'previous': '上一步',
            'finish': '完成'
        }
        
        result = button_texts.get(text_key, text_key)
        self._button_text_cache[text_key] = result
        return result
    
    def clear_cache(self):
        """清空缓存"""
        self._icon_cache.clear()
        self._button_text_cache.clear()
    
    def is_emoji_supported(self) -> bool:
        """检查是否支持emoji"""
        return self.emoji_supported
    
    def is_font_registered(self) -> bool:
        """检查字体是否注册成功"""
        return self.font_registered

# 创建全局字体管理器实例
_font_manager = FontManager()

def init_fonts() -> bool:
    """初始化字体"""
    return _font_manager.register_fonts()

def get_icon(icon_type: str) -> str:
    """获取图标"""
    return _font_manager.get_icon_text(icon_type)

def get_button_text(text_key: str) -> str:
    """获取按钮文本"""
    return _font_manager.get_button_text(text_key)

def is_emoji_supported() -> bool:
    """检查是否支持emoji"""
    return _font_manager.is_emoji_supported()

def is_font_registered() -> bool:
    """检查字体是否注册成功"""
    return _font_manager.is_font_registered()

def clear_font_cache():
    """清空字体缓存"""
    _font_manager.clear_cache()

# 兼容性：保持原有接口
font_manager = _font_manager
