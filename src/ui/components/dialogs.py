#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话框组件模块
提供各种类型的对话框和弹窗组件
"""

import logging
from typing import Optional, Callable, Any
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

from ..themes import (
    get_theme_color, get_status_color, responsive_font_size, 
    responsive_size, responsive_spacing
)
from .buttons import ModernButton, PrimaryButton, SecondaryButton

logger = logging.getLogger(__name__)

class ModernPopup(Popup):
    """现代化弹窗基类"""
    
    def __init__(self, **kwargs):
        # 设置默认样式
        kwargs.setdefault('size_hint', (0.9, None))
        kwargs.setdefault('height', responsive_size(200))
        kwargs.setdefault('separator_color', get_theme_color('divider'))
        kwargs.setdefault('title_color', get_theme_color('text'))
        kwargs.setdefault('title_size', responsive_font_size(18))
        
        super(ModernPopup, self).__init__(**kwargs)
        
        # 设置背景
        with self.canvas.before:
            Color(*get_theme_color('surface'))
            self.bg_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[responsive_size(12)]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, instance, value):
        """更新背景"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

class MessageDialog(ModernPopup):
    """消息对话框"""
    
    def __init__(self, title: str, message: str, message_type: str = 'info',
                 on_dismiss: Optional[Callable] = None, **kwargs):
        super(MessageDialog, self).__init__(title=title, **kwargs)
        
        self.message_type = message_type
        self.on_dismiss_callback = on_dismiss
        
        # 创建内容布局
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=responsive_spacing(16),
            padding=responsive_spacing(20)
        )
        
        # 消息标签
        message_label = Label(
            text=message,
            color=get_status_color(message_type),
            font_size=responsive_font_size(14),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        # 确定按钮
        ok_button = PrimaryButton(
            text='确定',
            size_hint=(None, None),
            size=(responsive_size(100), responsive_size(40)),
            pos_hint={'center_x': 0.5}
        )
        ok_button.bind(on_release=self._on_ok)
        
        content_layout.add_widget(message_label)
        content_layout.add_widget(ok_button)
        
        self.content = content_layout
    
    def _on_ok(self, instance):
        """确定按钮回调"""
        self.dismiss()
        if self.on_dismiss_callback:
            self.on_dismiss_callback()

class ConfirmationDialog(ModernPopup):
    """确认对话框"""
    
    def __init__(self, title: str, message: str, 
                 on_confirm: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None,
                 confirm_text: str = '确认',
                 cancel_text: str = '取消',
                 **kwargs):
        super(ConfirmationDialog, self).__init__(title=title, **kwargs)
        
        self.on_confirm_callback = on_confirm
        self.on_cancel_callback = on_cancel
        
        # 创建内容布局
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=responsive_spacing(16),
            padding=responsive_spacing(20)
        )
        
        # 消息标签
        message_label = Label(
            text=message,
            color=get_theme_color('text'),
            font_size=responsive_font_size(14),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        # 按钮布局
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=responsive_spacing(12),
            size_hint_y=None,
            height=responsive_size(40)
        )
        
        # 取消按钮
        cancel_button = SecondaryButton(
            text=cancel_text,
            size_hint=(0.5, 1)
        )
        cancel_button.bind(on_release=self._on_cancel)
        
        # 确认按钮
        confirm_button = PrimaryButton(
            text=confirm_text,
            size_hint=(0.5, 1)
        )
        confirm_button.bind(on_release=self._on_confirm)
        
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)
        
        content_layout.add_widget(message_label)
        content_layout.add_widget(button_layout)
        
        self.content = content_layout
    
    def _on_confirm(self, instance):
        """确认按钮回调"""
        self.dismiss()
        if self.on_confirm_callback:
            self.on_confirm_callback()
    
    def _on_cancel(self, instance):
        """取消按钮回调"""
        self.dismiss()
        if self.on_cancel_callback:
            self.on_cancel_callback()

class LoadingDialog(ModernPopup):
    """加载对话框"""
    
    def __init__(self, title: str = '加载中', message: str = '请稍候...', **kwargs):
        kwargs.setdefault('auto_dismiss', False)  # 不允许点击外部关闭
        super(LoadingDialog, self).__init__(title=title, **kwargs)
        
        # 创建内容布局
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=responsive_spacing(16),
            padding=responsive_spacing(20)
        )
        
        # 消息标签
        self.message_label = Label(
            text=message,
            color=get_theme_color('text'),
            font_size=responsive_font_size(14),
            halign='center',
            valign='middle'
        )
        
        # 进度条
        self.progress_bar = ProgressBar(
            size_hint_y=None,
            height=responsive_size(8),
            max=100,
            value=0
        )
        
        content_layout.add_widget(self.message_label)
        content_layout.add_widget(self.progress_bar)
        
        self.content = content_layout
        
        # 启动进度动画
        self._start_progress_animation()
    
    def _start_progress_animation(self):
        """启动进度条动画"""
        def update_progress(dt):
            if self.progress_bar.value >= 100:
                self.progress_bar.value = 0
            else:
                self.progress_bar.value += 2
        
        self.progress_event = Clock.schedule_interval(update_progress, 0.1)
    
    def update_message(self, message: str):
        """更新消息"""
        self.message_label.text = message
    
    def set_progress(self, value: float):
        """设置进度值"""
        self.progress_bar.value = min(max(value, 0), 100)
    
    def dismiss(self, *args, **kwargs):
        """关闭对话框"""
        if hasattr(self, 'progress_event'):
            self.progress_event.cancel()
        super(LoadingDialog, self).dismiss(*args, **kwargs)

class InputDialog(ModernPopup):
    """输入对话框"""
    
    def __init__(self, title: str, message: str, 
                 input_hint: str = '',
                 on_confirm: Optional[Callable[[str], None]] = None,
                 on_cancel: Optional[Callable] = None,
                 **kwargs):
        super(InputDialog, self).__init__(title=title, **kwargs)
        
        self.on_confirm_callback = on_confirm
        self.on_cancel_callback = on_cancel
        
        # 创建内容布局
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=responsive_spacing(16),
            padding=responsive_spacing(20)
        )
        
        # 消息标签
        message_label = Label(
            text=message,
            color=get_theme_color('text'),
            font_size=responsive_font_size(14),
            size_hint_y=None,
            height=responsive_size(30),
            halign='center',
            valign='middle'
        )
        
        # 输入框
        from kivy.uix.textinput import TextInput
        self.text_input = TextInput(
            hint_text=input_hint,
            size_hint_y=None,
            height=responsive_size(40),
            font_size=responsive_font_size(14),
            multiline=False
        )
        
        # 按钮布局
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=responsive_spacing(12),
            size_hint_y=None,
            height=responsive_size(40)
        )
        
        # 取消按钮
        cancel_button = SecondaryButton(
            text='取消',
            size_hint=(0.5, 1)
        )
        cancel_button.bind(on_release=self._on_cancel)
        
        # 确认按钮
        confirm_button = PrimaryButton(
            text='确认',
            size_hint=(0.5, 1)
        )
        confirm_button.bind(on_release=self._on_confirm)
        
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(confirm_button)
        
        content_layout.add_widget(message_label)
        content_layout.add_widget(self.text_input)
        content_layout.add_widget(button_layout)
        
        self.content = content_layout
        
        # 自动聚焦输入框
        Clock.schedule_once(lambda dt: self.text_input.focus, 0.1)
    
    def _on_confirm(self, instance):
        """确认按钮回调"""
        text = self.text_input.text.strip()
        self.dismiss()
        if self.on_confirm_callback:
            self.on_confirm_callback(text)
    
    def _on_cancel(self, instance):
        """取消按钮回调"""
        self.dismiss()
        if self.on_cancel_callback:
            self.on_cancel_callback()

# 便捷函数
def show_popup(title: str, message: str, message_type: str = 'info',
               on_dismiss: Optional[Callable] = None) -> MessageDialog:
    """显示消息弹窗
    
    Args:
        title: 标题
        message: 消息内容
        message_type: 消息类型 ('info', 'success', 'warning', 'error')
        on_dismiss: 关闭回调
        
    Returns:
        MessageDialog实例
    """
    dialog = MessageDialog(title, message, message_type, on_dismiss)
    dialog.open()
    return dialog

def show_confirmation_dialog(title: str, message: str,
                           on_confirm: Optional[Callable] = None,
                           on_cancel: Optional[Callable] = None) -> ConfirmationDialog:
    """显示确认对话框
    
    Args:
        title: 标题
        message: 消息内容
        on_confirm: 确认回调
        on_cancel: 取消回调
        
    Returns:
        ConfirmationDialog实例
    """
    dialog = ConfirmationDialog(title, message, on_confirm, on_cancel)
    dialog.open()
    return dialog

def show_loading_dialog(title: str = '加载中', message: str = '请稍候...') -> LoadingDialog:
    """显示加载对话框
    
    Args:
        title: 标题
        message: 消息内容
        
    Returns:
        LoadingDialog实例
    """
    dialog = LoadingDialog(title, message)
    dialog.open()
    return dialog
