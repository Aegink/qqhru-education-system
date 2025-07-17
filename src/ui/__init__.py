#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI界面模块
包含所有用户界面相关的组件和屏幕
"""

from .screens import MainScreen, LoginScreen, QueryScoresScreen, SwitchAccountScreen
from .themes import (
    THEME_COLORS, DARK_THEME_COLORS, get_theme_color, set_theme,
    is_dark_theme, apply_theme, get_device_type, responsive_size,
    responsive_font_size, responsive_spacing
)
from .components import (
    ModernButton, PrimaryButton, SecondaryButton, AccentButton,
    ErrorButton, SuccessButton, WarningButton, IconButton,
    OutlineButton, TextButton, FloatingActionButton,
    create_styled_button, create_icon_button,
    ModernPopup, MessageDialog, ConfirmationDialog, LoadingDialog, InputDialog,
    show_popup, show_confirmation_dialog, show_loading_dialog
)

__all__ = [
    # 屏幕组件
    'MainScreen', 'LoginScreen', 'QueryScoresScreen', 'SwitchAccountScreen',

    # 主题相关
    'THEME_COLORS', 'DARK_THEME_COLORS', 'get_theme_color', 'set_theme',
    'is_dark_theme', 'apply_theme', 'get_device_type', 'responsive_size',
    'responsive_font_size', 'responsive_spacing',

    # 按钮组件
    'ModernButton', 'PrimaryButton', 'SecondaryButton', 'AccentButton',
    'ErrorButton', 'SuccessButton', 'WarningButton', 'IconButton',
    'OutlineButton', 'TextButton', 'FloatingActionButton',
    'create_styled_button', 'create_icon_button',

    # 对话框组件
    'ModernPopup', 'MessageDialog', 'ConfirmationDialog', 'LoadingDialog', 'InputDialog',
    'show_popup', 'show_confirmation_dialog', 'show_loading_dialog'
]
