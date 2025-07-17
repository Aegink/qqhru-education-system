#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按钮组件模块
提供各种样式的现代化按钮组件
"""

import logging
from typing import Optional, Callable
from kivy.uix.button import Button
from kivy.properties import ListProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp

from ..themes import (
    get_theme_color, get_button_colors, responsive_font_size, 
    responsive_size, responsive_spacing
)

logger = logging.getLogger(__name__)

class ModernButton(Button):
    """现代化按钮 - 带圆角和主题色彩"""
    background_color = ListProperty([1, 1, 1, 1])
    background_normal = ''

    def __init__(self, button_type: str = 'primary', **kwargs):
        super(ModernButton, self).__init__(**kwargs)
        self.button_type = button_type
        self.size_hint_y = None
        self.height = responsive_size(40)
        self.font_size = responsive_font_size(14)
        self.bold = True

        # 获取按钮颜色配置
        colors = get_button_colors(button_type)
        self.background_color = colors['background']
        self.color = colors['text']

        # 创建背景图形
        self._create_background()
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _create_background(self):
        """创建按钮背景"""
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[responsive_size(8)]
            )

    def _update_graphics(self, instance, value):
        """更新图形元素"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def set_button_type(self, button_type: str):
        """设置按钮类型"""
        self.button_type = button_type
        colors = get_button_colors(button_type)
        self.background_color = colors['background']
        self.color = colors['text']
        
        # 更新背景颜色
        if hasattr(self, 'bg_rect'):
            self.canvas.before.clear()
            self._create_background()

class PrimaryButton(ModernButton):
    """主要按钮"""
    def __init__(self, **kwargs):
        super(PrimaryButton, self).__init__(button_type='primary', **kwargs)

class SecondaryButton(ModernButton):
    """次要按钮"""
    def __init__(self, **kwargs):
        super(SecondaryButton, self).__init__(button_type='secondary', **kwargs)

class AccentButton(ModernButton):
    """强调按钮"""
    def __init__(self, **kwargs):
        super(AccentButton, self).__init__(button_type='accent', **kwargs)

class ErrorButton(ModernButton):
    """错误/危险按钮"""
    def __init__(self, **kwargs):
        super(ErrorButton, self).__init__(button_type='error', **kwargs)

class SuccessButton(ModernButton):
    """成功按钮"""
    def __init__(self, **kwargs):
        super(SuccessButton, self).__init__(button_type='success', **kwargs)

class WarningButton(ModernButton):
    """警告按钮"""
    def __init__(self, **kwargs):
        super(WarningButton, self).__init__(button_type='warning', **kwargs)

class IconButton(ModernButton):
    """图标按钮 - 圆形按钮，适合放置图标"""
    def __init__(self, icon_text: str = '', **kwargs):
        super(IconButton, self).__init__(**kwargs)
        self.text = icon_text
        self.size_hint = (None, None)
        self.size = (responsive_size(48), responsive_size(48))
        self.font_size = responsive_font_size(18)

    def _create_background(self):
        """创建圆形背景"""
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[responsive_size(24)]  # 圆形
            )

class OutlineButton(Button):
    """轮廓按钮 - 只有边框，透明背景"""
    background_normal = ''
    background_down = ''

    def __init__(self, button_type: str = 'primary', **kwargs):
        super(OutlineButton, self).__init__(**kwargs)
        self.button_type = button_type
        self.size_hint_y = None
        self.height = responsive_size(40)
        self.font_size = responsive_font_size(14)
        self.bold = True

        # 设置颜色
        colors = get_button_colors(button_type)
        self.color = colors['background']  # 文字使用主题色
        
        # 创建边框
        self._create_border()
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _create_border(self):
        """创建按钮边框"""
        from kivy.graphics import Line
        
        with self.canvas.before:
            Color(*self.color)
            self.border_line = Line(
                rounded_rectangle=(
                    self.x, self.y, self.width, self.height, 
                    responsive_size(8)
                ),
                width=dp(2)
            )

    def _update_graphics(self, instance, value):
        """更新图形元素"""
        if hasattr(self, 'border_line'):
            self.border_line.rounded_rectangle = (
                self.x, self.y, self.width, self.height, 
                responsive_size(8)
            )

class TextButton(Button):
    """文本按钮 - 无背景，只有文字"""
    background_normal = ''
    background_down = ''

    def __init__(self, button_type: str = 'primary', **kwargs):
        super(TextButton, self).__init__(**kwargs)
        self.button_type = button_type
        self.size_hint_y = None
        self.height = responsive_size(36)
        self.font_size = responsive_font_size(14)
        self.bold = False

        # 设置文字颜色
        colors = get_button_colors(button_type)
        self.color = colors['background']

class FloatingActionButton(IconButton):
    """浮动操作按钮"""
    def __init__(self, **kwargs):
        super(FloatingActionButton, self).__init__(button_type='accent', **kwargs)
        self.size = (responsive_size(56), responsive_size(56))
        self.font_size = responsive_font_size(24)

    def _create_background(self):
        """创建带阴影的圆形背景"""
        from kivy.graphics import Ellipse
        
        with self.canvas.before:
            # 阴影
            Color(0, 0, 0, 0.2)
            self.shadow = Ellipse(
                pos=(self.x + dp(2), self.y - dp(2)), 
                size=self.size
            )
            
            # 主背景
            Color(*self.background_color)
            self.bg_rect = Ellipse(pos=self.pos, size=self.size)

    def _update_graphics(self, instance, value):
        """更新图形元素"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
        if hasattr(self, 'shadow'):
            self.shadow.pos = (self.x + dp(2), self.y - dp(2))
            self.shadow.size = self.size

# 便捷函数
def create_styled_button(text: str, button_type: str = 'primary', 
                        on_press: Optional[Callable] = None, **kwargs) -> ModernButton:
    """创建样式化按钮的便捷函数
    
    Args:
        text: 按钮文字
        button_type: 按钮类型
        on_press: 点击回调函数
        **kwargs: 其他参数
        
    Returns:
        ModernButton实例
    """
    button = ModernButton(text=text, button_type=button_type, **kwargs)
    if on_press:
        button.bind(on_release=on_press)
    return button

def create_icon_button(icon_text: str, button_type: str = 'primary',
                      on_press: Optional[Callable] = None, **kwargs) -> IconButton:
    """创建图标按钮的便捷函数
    
    Args:
        icon_text: 图标文字
        button_type: 按钮类型
        on_press: 点击回调函数
        **kwargs: 其他参数
        
    Returns:
        IconButton实例
    """
    button = IconButton(icon_text=icon_text, button_type=button_type, **kwargs)
    if on_press:
        button.bind(on_release=on_press)
    return button

# 兼容性别名
StyledButton = PrimaryButton
