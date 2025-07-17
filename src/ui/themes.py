#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI主题模块
定义应用的颜色主题、样式和响应式设计
"""

import logging
from typing import Dict, List, Tuple, Optional
from kivy.metrics import dp
from kivy.core.window import Window

logger = logging.getLogger(__name__)

# 定义现代化主题颜色 - Material Design 3.0 风格
THEME_COLORS = {
    'primary': [0.26, 0.54, 0.96, 1],      # 现代蓝色 #4285F4
    'primary_variant': [0.13, 0.42, 0.91, 1],  # 深蓝色 #2196F3
    'secondary': [0.96, 0.96, 0.96, 1],    # 浅灰色背景
    'secondary_variant': [0.93, 0.93, 0.93, 1],  # 更深的灰色
    'accent': [0.25, 0.80, 0.46, 1],       # 现代绿色 #4CAF75
    'accent_variant': [0.20, 0.69, 0.39, 1],   # 深绿色
    'background': [0.98, 0.98, 0.98, 1],   # 温暖的白色背景
    'surface': [1, 1, 1, 1],               # 纯白色表面
    'text': [0.13, 0.13, 0.13, 1],         # 深灰色文字 #212121
    'text_secondary': [0.46, 0.46, 0.46, 1],  # 次要文字颜色
    'error': [0.96, 0.26, 0.21, 1],        # 现代红色 #F44336
    'success': [0.30, 0.69, 0.31, 1],      # 成功绿色 #4CAF50
    'warning': [1.0, 0.60, 0.0, 1],        # 警告橙色 #FF9800
    'info': [0.13, 0.59, 0.95, 1],         # 信息蓝色 #2196F3
    'shadow': [0, 0, 0, 0.1],              # 阴影颜色
    'divider': [0.88, 0.88, 0.88, 1],      # 分割线颜色
}

# 暗色主题
DARK_THEME_COLORS = {
    'primary': [0.38, 0.61, 0.97, 1],      # 亮蓝色
    'primary_variant': [0.26, 0.54, 0.96, 1],
    'secondary': [0.18, 0.18, 0.18, 1],    # 深灰色背景
    'secondary_variant': [0.25, 0.25, 0.25, 1],
    'accent': [0.30, 0.85, 0.51, 1],       # 亮绿色
    'accent_variant': [0.25, 0.80, 0.46, 1],
    'background': [0.08, 0.08, 0.08, 1],   # 深色背景
    'surface': [0.12, 0.12, 0.12, 1],      # 深色表面
    'text': [0.87, 0.87, 0.87, 1],         # 浅色文字
    'text_secondary': [0.60, 0.60, 0.60, 1],
    'error': [0.97, 0.38, 0.33, 1],
    'success': [0.40, 0.79, 0.41, 1],
    'warning': [1.0, 0.70, 0.2, 1],
    'info': [0.25, 0.69, 0.96, 1],
    'shadow': [0, 0, 0, 0.3],
    'divider': [0.30, 0.30, 0.30, 1],
}

# 当前主题
_current_theme = THEME_COLORS
_is_dark_theme = False

# 响应式设计配置
RESPONSIVE_CONFIG = {
    'mobile': {
        'max_width': 600,
        'scale_factor': 1.0,
        'font_scale': 1.0,
        'spacing_scale': 1.0
    },
    'tablet': {
        'max_width': 1024,
        'scale_factor': 1.2,
        'font_scale': 1.1,
        'spacing_scale': 1.1
    },
    'desktop': {
        'max_width': float('inf'),
        'scale_factor': 0.8,  # 桌面端缩小以适应更大屏幕
        'font_scale': 0.9,
        'spacing_scale': 0.9
    }
}

def get_device_type() -> str:
    """获取设备类型"""
    width = Window.width
    
    if width <= RESPONSIVE_CONFIG['mobile']['max_width']:
        return 'mobile'
    elif width <= RESPONSIVE_CONFIG['tablet']['max_width']:
        return 'tablet'
    else:
        return 'desktop'

def get_scale_factor() -> float:
    """获取当前设备的缩放因子"""
    device_type = get_device_type()
    return RESPONSIVE_CONFIG[device_type]['scale_factor']

def get_font_scale() -> float:
    """获取字体缩放因子"""
    device_type = get_device_type()
    return RESPONSIVE_CONFIG[device_type]['font_scale']

def get_spacing_scale() -> float:
    """获取间距缩放因子"""
    device_type = get_device_type()
    return RESPONSIVE_CONFIG[device_type]['spacing_scale']

def responsive_size(base_size: float) -> float:
    """响应式尺寸计算"""
    return dp(base_size * get_scale_factor())

def responsive_font_size(base_size: float) -> float:
    """响应式字体大小计算"""
    return dp(base_size * get_font_scale())

def responsive_spacing(base_spacing: float) -> float:
    """响应式间距计算"""
    return dp(base_spacing * get_spacing_scale())

def get_theme_color(color_name: str) -> List[float]:
    """获取主题颜色
    
    Args:
        color_name: 颜色名称
        
    Returns:
        RGBA颜色值列表
    """
    return _current_theme.get(color_name, [0, 0, 0, 1])

def set_theme(dark_mode: bool = False):
    """设置主题
    
    Args:
        dark_mode: 是否使用暗色主题
    """
    global _current_theme, _is_dark_theme
    
    if dark_mode:
        _current_theme = DARK_THEME_COLORS
        _is_dark_theme = True
        logger.info("已切换到暗色主题")
    else:
        _current_theme = THEME_COLORS
        _is_dark_theme = False
        logger.info("已切换到亮色主题")

def is_dark_theme() -> bool:
    """检查是否为暗色主题"""
    return _is_dark_theme

def apply_theme(widget, theme_properties: Dict[str, str]):
    """应用主题到组件
    
    Args:
        widget: Kivy组件
        theme_properties: 主题属性映射
    """
    try:
        for prop_name, color_name in theme_properties.items():
            if hasattr(widget, prop_name):
                color_value = get_theme_color(color_name)
                setattr(widget, prop_name, color_value)
    except Exception as e:
        logger.error(f"应用主题失败: {e}")

def get_button_colors(button_type: str = 'primary') -> Dict[str, List[float]]:
    """获取按钮颜色配置
    
    Args:
        button_type: 按钮类型
        
    Returns:
        包含背景色和文字色的字典
    """
    color_configs = {
        'primary': {
            'background': get_theme_color('primary'),
            'text': [1, 1, 1, 1]
        },
        'secondary': {
            'background': get_theme_color('secondary'),
            'text': get_theme_color('text')
        },
        'accent': {
            'background': get_theme_color('accent'),
            'text': [1, 1, 1, 1]
        },
        'error': {
            'background': get_theme_color('error'),
            'text': [1, 1, 1, 1]
        },
        'success': {
            'background': get_theme_color('success'),
            'text': [1, 1, 1, 1]
        },
        'warning': {
            'background': get_theme_color('warning'),
            'text': [1, 1, 1, 1]
        }
    }
    
    return color_configs.get(button_type, color_configs['primary'])

def get_input_colors() -> Dict[str, List[float]]:
    """获取输入框颜色配置"""
    primary_color = get_theme_color('primary')
    selection_color = primary_color[:3] + [0.3]  # 使用主色调的半透明版本作为选择色

    return {
        'background': [0.95, 0.95, 0.95, 1] if not _is_dark_theme else [0.20, 0.20, 0.20, 1],
        'foreground': get_theme_color('text'),
        'cursor': get_theme_color('primary'),
        'selection': selection_color
    }

def get_card_colors(elevation: int = 2) -> Dict[str, List[float]]:
    """获取卡片颜色配置
    
    Args:
        elevation: 阴影高度
        
    Returns:
        包含背景色和阴影色的字典
    """
    shadow_opacity = min(0.1 + elevation * 0.02, 0.3)  # 根据高度调整阴影透明度
    
    return {
        'background': get_theme_color('surface'),
        'shadow': [0, 0, 0, shadow_opacity]
    }

def update_responsive_config(config: Dict[str, Dict[str, float]]):
    """更新响应式配置
    
    Args:
        config: 新的响应式配置
    """
    global RESPONSIVE_CONFIG
    RESPONSIVE_CONFIG.update(config)
    logger.info("响应式配置已更新")

def get_status_color(status: str) -> List[float]:
    """根据状态获取颜色
    
    Args:
        status: 状态类型 ('success', 'error', 'warning', 'info')
        
    Returns:
        RGBA颜色值列表
    """
    status_colors = {
        'success': get_theme_color('success'),
        'error': get_theme_color('error'),
        'warning': get_theme_color('warning'),
        'info': get_theme_color('info'),
        'default': get_theme_color('text_secondary')
    }
    
    return status_colors.get(status, status_colors['default'])

# 监听窗口大小变化以更新响应式设计
def _on_window_resize(instance, size):
    """窗口大小变化回调"""
    device_type = get_device_type()
    logger.debug(f"窗口大小变化: {size}, 设备类型: {device_type}")

# 绑定窗口大小变化事件
Window.bind(size=_on_window_resize)
