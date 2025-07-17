#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理屏幕模块
用于管理应用配置文件
"""

import os
import logging
from typing import Optional
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock

from ..themes import (
    get_theme_color, responsive_size, responsive_spacing, 
    responsive_font_size
)
from ..components import (
    PrimaryButton, SecondaryButton, AccentButton,
    ModernCard, show_popup, show_confirmation_dialog
)
from ...core.config import (
    get_config_file_info, delete_config_file, backup_config,
    reset_config, get_config_file_path
)

logger = logging.getLogger(__name__)

class ConfigInfoCard(ModernCard):
    """配置信息卡片"""
    
    def __init__(self, **kwargs):
        super(ConfigInfoCard, self).__init__(
            elevation=2,
            background_color=get_theme_color('surface'),
            **kwargs
        )
        
        self.orientation = 'vertical'
        self.padding = responsive_spacing(16)
        self.spacing = responsive_spacing(12)
        self.size_hint = (1, None)
        self.height = responsive_size(200)
        
        self._create_content()
        self._update_info()
    
    def _create_content(self):
        """创建卡片内容"""
        # 标题
        title_label = Label(
            text="配置文件信息",
            font_size=responsive_font_size(16),
            color=get_theme_color('text'),
            bold=True,
            size_hint=(1, None),
            height=responsive_size(30),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)
        
        # 信息显示区域
        self.info_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=responsive_spacing(8)
        )
        self.add_widget(self.info_layout)
    
    def _update_info(self):
        """更新配置信息"""
        try:
            # 清空现有内容
            self.info_layout.clear_widgets()
            
            # 获取配置文件信息
            info = get_config_file_info()
            
            # 创建信息标签
            info_items = [
                ("文件路径", info.get("path", "未知")),
                ("文件大小", f"{info.get('size', 0)} 字节"),
                ("文件状态", "存在" if info.get("exists", False) else "不存在"),
                ("修改时间", info.get("modified_time", "未知"))
            ]
            
            for label_text, value_text in info_items:
                item_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint=(1, None),
                    height=responsive_size(25)
                )
                
                # 标签
                label = Label(
                    text=f"{label_text}:",
                    font_size=responsive_font_size(12),
                    color=get_theme_color('text_secondary'),
                    size_hint=(0.3, 1),
                    halign='left',
                    valign='middle'
                )
                label.bind(size=label.setter('text_size'))
                item_layout.add_widget(label)
                
                # 值
                value = Label(
                    text=str(value_text),
                    font_size=responsive_font_size(12),
                    color=get_theme_color('text'),
                    size_hint=(0.7, 1),
                    halign='left',
                    valign='middle'
                )
                value.bind(size=value.setter('text_size'))
                item_layout.add_widget(value)
                
                self.info_layout.add_widget(item_layout)
            
        except Exception as e:
            logger.error(f"更新配置信息失败: {e}")
            error_label = Label(
                text=f"获取配置信息失败: {str(e)}",
                font_size=responsive_font_size(12),
                color=get_theme_color('error'),
                size_hint=(1, 1),
                halign='center',
                valign='middle'
            )
            error_label.bind(size=error_label.setter('text_size'))
            self.info_layout.add_widget(error_label)
    
    def refresh_info(self):
        """刷新配置信息"""
        self._update_info()

class ConfigScreen(BoxLayout):
    """配置管理界面"""
    
    def __init__(self, app, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = responsive_spacing(16)
        self.spacing = responsive_spacing(16)
        
        self._create_ui()
    
    def _create_ui(self):
        """创建界面"""
        # 标题
        title_label = Label(
            text="配置管理",
            font_size=responsive_font_size(24),
            color=get_theme_color('text'),
            bold=True,
            size_hint=(1, None),
            height=responsive_size(40),
            halign='center',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)
        
        # 说明文字
        desc_label = Label(
            text="管理应用配置文件，包括备份、重置和删除操作",
            font_size=responsive_font_size(12),
            color=get_theme_color('text_secondary'),
            size_hint=(1, None),
            height=responsive_size(40),
            halign='center',
            valign='middle'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        self.add_widget(desc_label)
        
        # 配置信息卡片
        self.config_info_card = ConfigInfoCard()
        self.add_widget(self.config_info_card)
        
        # 操作按钮区域
        self._create_action_buttons()
        
        # 底部按钮
        self._create_bottom_buttons()
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        # 第一行按钮
        button_layout1 = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=responsive_size(50),
            spacing=responsive_spacing(12)
        )
        
        # 备份配置按钮
        backup_button = AccentButton(
            text="备份配置",
            size_hint=(0.5, 1),
            font_size=responsive_font_size(14)
        )
        backup_button.bind(on_release=self._on_backup_config)
        button_layout1.add_widget(backup_button)
        
        # 刷新信息按钮
        refresh_button = SecondaryButton(
            text="刷新信息",
            size_hint=(0.5, 1),
            font_size=responsive_font_size(14)
        )
        refresh_button.bind(on_release=self._on_refresh_info)
        button_layout1.add_widget(refresh_button)
        
        self.add_widget(button_layout1)
        
        # 第二行按钮
        button_layout2 = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=responsive_size(50),
            spacing=responsive_spacing(12)
        )
        
        # 重置配置按钮
        reset_button = SecondaryButton(
            text="重置配置",
            size_hint=(0.5, 1),
            font_size=responsive_font_size(14)
        )
        reset_button.bind(on_release=self._on_reset_config)
        button_layout2.add_widget(reset_button)
        
        # 删除配置按钮
        delete_button = SecondaryButton(
            text="删除配置",
            size_hint=(0.5, 1),
            font_size=responsive_font_size(14)
        )
        delete_button.bind(on_release=self._on_delete_config)
        button_layout2.add_widget(delete_button)
        
        self.add_widget(button_layout2)
    
    def _create_bottom_buttons(self):
        """创建底部按钮"""
        # 间距
        self.add_widget(Widget(size_hint=(1, 1)))
        
        # 底部按钮
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=responsive_size(50),
            spacing=responsive_spacing(12)
        )
        
        # 打开配置目录按钮
        open_dir_button = SecondaryButton(
            text="打开配置目录",
            size_hint=(0.5, 1),
            font_size=responsive_font_size(14)
        )
        open_dir_button.bind(on_release=self._on_open_config_dir)
        button_layout.add_widget(open_dir_button)
        
        # 返回按钮
        back_button = PrimaryButton(
            text="返回主界面",
            size_hint=(0.5, 1),
            font_size=responsive_font_size(14)
        )
        back_button.bind(on_release=self._on_back)
        button_layout.add_widget(back_button)
        
        self.add_widget(button_layout)
    
    def _on_backup_config(self, instance):
        """备份配置"""
        try:
            success = backup_config()
            if success:
                show_popup("成功", "配置文件已备份", "success")
                self.config_info_card.refresh_info()
            else:
                show_popup("错误", "备份配置文件失败", "error")
        except Exception as e:
            logger.error(f"备份配置失败: {e}")
            show_popup("错误", f"备份配置失败: {str(e)}", "error")
    
    def _on_refresh_info(self, instance):
        """刷新信息"""
        self.config_info_card.refresh_info()
        show_popup("提示", "配置信息已刷新", "info")
    
    def _on_reset_config(self, instance):
        """重置配置"""
        def confirm_reset():
            try:
                reset_config()
                show_popup("成功", "配置已重置为默认值", "success")
                self.config_info_card.refresh_info()
            except Exception as e:
                logger.error(f"重置配置失败: {e}")
                show_popup("错误", f"重置配置失败: {str(e)}", "error")
        
        show_confirmation_dialog(
            "确认重置",
            "确定要重置配置为默认值吗？\n这将清除所有自定义设置。",
            confirm_reset
        )
    
    def _on_delete_config(self, instance):
        """删除配置"""
        def confirm_delete():
            try:
                success = delete_config_file()
                if success:
                    show_popup("成功", "配置文件已删除", "success")
                    self.config_info_card.refresh_info()
                else:
                    show_popup("提示", "配置文件不存在或删除失败", "warning")
            except Exception as e:
                logger.error(f"删除配置失败: {e}")
                show_popup("错误", f"删除配置失败: {str(e)}", "error")
        
        show_confirmation_dialog(
            "确认删除",
            "确定要删除配置文件吗？\n这将清除所有设置，下次启动时将使用默认配置。",
            confirm_delete
        )
    
    def _on_open_config_dir(self, instance):
        """打开配置目录"""
        try:
            config_path = get_config_file_path()
            config_dir = os.path.dirname(config_path)
            
            if os.path.exists(config_dir):
                import subprocess
                import sys
                
                if sys.platform == "win32":
                    subprocess.run(["explorer", config_dir])
                elif sys.platform == "darwin":
                    subprocess.run(["open", config_dir])
                else:
                    subprocess.run(["xdg-open", config_dir])
                
                show_popup("提示", f"已打开配置目录:\n{config_dir}", "info")
            else:
                show_popup("错误", "配置目录不存在", "error")
                
        except Exception as e:
            logger.error(f"打开配置目录失败: {e}")
            show_popup("错误", f"打开配置目录失败: {str(e)}", "error")
    
    def _on_back(self, instance):
        """返回主界面"""
        self.app.show_main_screen()
