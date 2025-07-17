#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络设置屏幕模块
用于切换校内网和校外网
"""

import logging
import threading
from typing import Optional
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

from ..themes import (
    get_theme_color, get_input_colors, responsive_size, responsive_spacing,
    responsive_font_size
)
from ..components import (
    PrimaryButton, SecondaryButton, AccentButton,
    ModernCard, show_popup, show_confirmation_dialog
)

class NetworkTextInput(TextInput):
    """网络设置专用文本输入框"""

    def __init__(self, **kwargs):
        super(NetworkTextInput, self).__init__(**kwargs)

        # 获取输入框颜色配置
        input_colors = get_input_colors()

        # 设置样式
        self.multiline = False
        self.size_hint = (1, None)
        self.height = responsive_size(45)  # 增加高度
        self.font_size = responsive_font_size(16)  # 增大字体

        # 设置颜色 - 确保有足够的对比度
        self.foreground_color = input_colors['foreground']
        self.background_color = input_colors['background']
        self.cursor_color = input_colors['cursor']
        self.selection_color = input_colors['selection']

        # 设置内边距
        self.padding = [responsive_spacing(15), responsive_spacing(12),
                       responsive_spacing(15), responsive_spacing(12)]

        logger.debug(f"NetworkTextInput 创建，颜色配置: {input_colors}")
        logger.debug(f"前景色: {self.foreground_color}, 背景色: {self.background_color}")
from ...core.config import (
    get_available_networks, get_current_network, switch_network,
    get_network_status, get_config, update_config, save_config,
    add_network_config, update_network_config, remove_network_config
)
from ...core.api import make_request

logger = logging.getLogger(__name__)

class NetworkConfigDialog:
    """网络配置编辑对话框"""

    def __init__(self, network_name: str = "", network_config: dict = None, is_new: bool = False, on_save=None):
        self.network_name = network_name
        self.network_config = network_config or {}
        self.is_new = is_new
        self.on_save = on_save
        self.popup = None
        self.inputs = {}

        # 默认路径配置
        self.default_paths = {
            "base_url": "",
            "login_path": "/login",
            "login_post_path": "/j_spring_security_check",
            "scores_path": "/student/integratedQuery/scoreQuery/thisTermScores/index",
            "captcha_path": "/captcha",
            "logout_path": "/logout",
            "student_info_path": "/student/studentinfo/studentInfoModify/index",
            "description": ""
        }

        # 路径配置说明
        self.path_descriptions = {
            "base_url": "基础URL地址（如: http://111.43.36.164）",
            "login_path": "登录页面路径",
            "login_post_path": "登录提交路径",
            "scores_path": "成绩查询路径",
            "captcha_path": "验证码获取路径",
            "logout_path": "退出登录路径",
            "student_info_path": "学生信息路径",
            "description": "网络环境描述"
        }

    def _test_simple_popup(self):
        """测试简单弹窗"""
        from kivy.uix.popup import Popup
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label

        def test_button_click(instance):
            print("测试按钮被点击了！")
            logger.info("测试按钮被点击了！")
            instance.parent.parent.dismiss()  # 关闭弹窗

        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        content.add_widget(Label(text='这是一个测试弹窗', color=[0, 0, 0, 1]))

        test_btn = Button(
            text='测试按钮',
            size_hint=(1, None),
            height=50,
            background_color=[0, 1, 0, 1],
            color=[0, 0, 0, 1]
        )
        test_btn.bind(on_release=test_button_click)
        content.add_widget(test_btn)

        popup = Popup(
            title='按钮测试',
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=True
        )
        popup.open()

    def show(self):
        """显示对话框"""
        # 先测试简单弹窗
        # self._test_simple_popup()
        # return
        # 创建主容器 - 简化结构
        main_content = BoxLayout(
            orientation='vertical',
            spacing=20,
            padding=20
        )

        # 添加一个简单的标题
        from kivy.uix.label import Label
        title_label = Label(
            text=f"{'添加' if self.is_new else '编辑'}网络配置",
            color=[0, 0, 0, 1],
            font_size=18,
            size_hint=(1, None),
            height=40
        )
        main_content.add_widget(title_label)

        # 直接添加输入字段，不使用滚动视图
        # 如果是新建，添加网络名称输入
        if self.is_new:
            self._add_input_field(main_content, "network_name", "网络名称", self.network_name, "例如: 校内网2")

        # 添加所有配置项，但使用简化的布局
        for key, description in self.path_descriptions.items():
            current_value = self.network_config.get(key, self.default_paths.get(key, ""))
            if key == "description" and not current_value and not self.is_new:
                current_value = f"{self.network_name}网络环境"

            placeholder = self.default_paths.get(key, "")
            if key == "base_url":
                placeholder = "http://111.43.36.164"
            elif key == "description":
                placeholder = f"{self.network_name or '网络'}环境描述"

            self._add_input_field(main_content, key, description, current_value, placeholder)

        # 简化的按钮区域
        from kivy.uix.button import Button

        # 添加间距
        spacer = Widget(size_hint=(1, None), height=20)
        main_content.add_widget(spacer)

        # 取消按钮
        cancel_button = Button(
            text="取消",
            size_hint=(1, None),
            height=50,
            font_size=20,
            background_color=[0.8, 0.8, 0.8, 1],
            color=[0, 0, 0, 1]
        )

        def cancel_clicked(instance):
            print("取消按钮被点击！")
            logger.info("取消按钮被点击！")
            if hasattr(self, 'popup') and self.popup:
                self.popup.dismiss()

        cancel_button.bind(on_release=cancel_clicked)
        main_content.add_widget(cancel_button)

        # 保存按钮
        save_text = "添加" if self.is_new else "保存"
        save_button = Button(
            text=save_text,
            size_hint=(1, None),
            height=50,
            font_size=20,
            background_color=[0, 0.8, 0, 1],  # 绿色背景
            color=[1, 1, 1, 1]
        )

        def save_clicked(instance):
            print(f"{save_text}按钮被点击！")
            logger.info(f"{save_text}按钮被点击！")
            self._do_save()

        save_button.bind(on_release=save_clicked)
        main_content.add_widget(save_button)

        logger.debug("按钮已创建并绑定事件")

        # 创建简单的弹窗
        title_text = "网络配置"
        self.popup = Popup(
            title=title_text,
            content=main_content,
            size_hint=(0.8, 0.7),
            auto_dismiss=True  # 允许点击外部关闭
        )

        logger.debug("网络配置弹窗已创建，准备打开")
        self.popup.open()
        logger.debug("网络配置弹窗已打开")

    def _do_save(self):
        """执行保存操作"""
        try:
            logger.info("开始保存网络配置")

            # 收集所有输入值
            config_data = {}

            # 获取网络名称
            if self.is_new:
                network_name_input = self.inputs.get("network_name")
                if not network_name_input:
                    show_popup("错误", "找不到网络名称输入框", "error")
                    return

                network_name = network_name_input.text.strip()
                if not network_name:
                    show_popup("错误", "请输入网络名称", "error")
                    return
            else:
                network_name = self.network_name

            # 获取基础URL
            base_url_input = self.inputs.get("base_url")
            if not base_url_input:
                show_popup("错误", "找不到基础URL输入框", "error")
                return

            base_url = base_url_input.text.strip()
            if not base_url:
                show_popup("错误", "请输入基础URL地址", "error")
                return

            # 收集所有配置
            for key in self.path_descriptions.keys():
                if key in self.inputs:
                    value = self.inputs[key].text.strip()
                    if key == "base_url" and value:
                        config_data[key] = value
                    elif key != "base_url":
                        config_data[key] = value or self.default_paths.get(key, "")

            # 确保描述不为空
            if not config_data.get("description"):
                config_data["description"] = f"{network_name}网络环境"

            # 调用保存回调
            if self.on_save:
                success = self.on_save(network_name, config_data, self.is_new)
                if success:
                    show_popup("成功", "网络配置保存成功！", "success")
                    self.popup.dismiss()
                else:
                    show_popup("错误", "保存配置失败", "error")
            else:
                show_popup("错误", "没有设置保存回调函数", "error")

        except Exception as e:
            logger.error(f"保存网络配置失败: {e}", exc_info=True)
            show_popup("错误", f"保存配置失败: {str(e)}", "error")

    def _add_input_field(self, parent, key, label_text, current_value, placeholder):
        """添加输入字段"""
        # 标签
        label = Label(
            text=f"{label_text}:",
            font_size=responsive_font_size(16),
            color=[0, 0, 0, 1],  # 纯黑色文字
            bold=True,
            size_hint=(1, None),
            height=responsive_size(35),
            halign='left',
            valign='middle',
            markup=True
        )
        label.bind(size=label.setter('text_size'))
        parent.add_widget(label)

        # 输入框
        text_input = NetworkTextInput(
            text=str(current_value),
            hint_text=placeholder
        )

        self.inputs[key] = text_input
        parent.add_widget(text_input)

        # 添加一些间距
        spacer = Widget(size_hint=(1, None), height=responsive_size(8))
        parent.add_widget(spacer)

        logger.debug(f"添加输入字段: {key} = {label_text}, 当前值: {current_value}")
        logger.debug(f"标签颜色: {label.color}")




class NetworkCard(ModernCard):
    """网络选项卡片"""

    def __init__(self, network_name: str, url: str, description: str = "", is_current: bool = False,
                 on_select=None, on_edit=None, on_delete=None, on_test=None, on_quick_edit=None, **kwargs):
        super(NetworkCard, self).__init__(
            elevation=2 if is_current else 1,
            background_color=get_theme_color('primary_container') if is_current else get_theme_color('surface'),
            **kwargs
        )

        self.network_name = network_name
        self.url = url
        self.description = description or f"{network_name}网络环境"
        self.is_current = is_current
        self.on_select = on_select
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_test = on_test
        self.on_quick_edit = on_quick_edit

        self.orientation = 'vertical'
        self.padding = responsive_spacing(12)
        self.spacing = responsive_spacing(8)
        self.size_hint = (1, None)
        self.height = responsive_size(180)  # 增加高度以容纳更多按钮

        # 网络状态
        self.network_status = "未知"
        self.status_color = get_theme_color('text_secondary')

        self._create_content()
    
    def _create_content(self):
        """创建卡片内容"""
        # 标题行
        title_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.25))

        # 网络名称
        name_label = Label(
            text=self.network_name,
            font_size=responsive_font_size(16),
            color=get_theme_color('primary') if self.is_current else get_theme_color('text'),
            bold=self.is_current,
            halign='left',
            valign='middle',
            size_hint=(0.5, 1)
        )
        name_label.bind(size=name_label.setter('text_size'))
        title_layout.add_widget(name_label)

        # 状态显示
        self.status_label = Label(
            text=f"状态: {self.network_status}",
            font_size=responsive_font_size(12),
            color=self.status_color,
            halign='center',
            valign='middle',
            size_hint=(0.3, 1)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        title_layout.add_widget(self.status_label)

        # 当前网络标识
        if self.is_current:
            current_label = Label(
                text="当前网络",
                font_size=responsive_font_size(12),
                color=get_theme_color('primary'),
                halign='right',
                valign='middle',
                size_hint=(0.2, 1)
            )
            current_label.bind(size=current_label.setter('text_size'))
            title_layout.add_widget(current_label)
        else:
            title_layout.add_widget(Widget(size_hint=(0.2, 1)))

        self.add_widget(title_layout)

        # URL显示
        self.url_label = Label(
            text=self.url,
            font_size=responsive_font_size(12),
            color=get_theme_color('text_secondary'),
            halign='left',
            valign='middle',
            size_hint=(1, 0.2)
        )
        self.url_label.bind(size=self.url_label.setter('text_size'))
        self.add_widget(self.url_label)

        # 第一行按钮
        button_layout1 = BoxLayout(orientation='horizontal', size_hint=(1, 0.25), spacing=responsive_spacing(6))

        if not self.is_current:
            # 切换按钮
            switch_button = AccentButton(
                text="切换",
                size_hint=(0.3, 1),
                font_size=responsive_font_size(11)
            )
            switch_button.bind(on_release=self._on_switch)
            button_layout1.add_widget(switch_button)
        else:
            button_layout1.add_widget(Widget(size_hint=(0.3, 1)))

        # 测试按钮
        test_button = SecondaryButton(
            text="测试连接",
            size_hint=(0.35, 1),
            font_size=responsive_font_size(11)
        )
        test_button.bind(on_release=self._on_test)
        button_layout1.add_widget(test_button)

        # 配置按钮
        config_button = AccentButton(
            text="配置",
            size_hint=(0.25, 1),
            font_size=responsive_font_size(11)
        )
        config_button.bind(on_release=self._on_config)
        button_layout1.add_widget(config_button)

        # 删除按钮（非当前网络才显示）
        if not self.is_current:
            delete_button = SecondaryButton(
                text="删除",
                size_hint=(0.1, 1),
                font_size=responsive_font_size(11)
            )
            delete_button.bind(on_release=self._on_delete)
            button_layout1.add_widget(delete_button)

        self.add_widget(button_layout1)

        # 第二行按钮（快速编辑）
        button_layout2 = BoxLayout(orientation='horizontal', size_hint=(1, 0.25), spacing=responsive_spacing(6))

        # 快速编辑URL按钮
        quick_edit_button = SecondaryButton(
            text="快速编辑URL",
            size_hint=(1, 1),
            font_size=responsive_font_size(11)
        )
        quick_edit_button.bind(on_release=self._on_quick_edit)
        button_layout2.add_widget(quick_edit_button)

        self.add_widget(button_layout2)
    
    def _on_switch(self, instance):
        """切换网络"""
        if self.on_select:
            self.on_select(self.network_name)

    def _on_config(self, instance):
        """打开配置对话框"""
        if self.on_edit:
            self.on_edit(self.network_name)

    def _on_quick_edit(self, instance):
        """快速编辑URL"""
        if self.on_quick_edit:
            self.on_quick_edit(self.network_name, self.url)

    def _on_delete(self, instance):
        """删除网络"""
        if self.on_delete:
            self.on_delete(self.network_name)

    def _on_test(self, instance):
        """测试网络连接"""
        if self.on_test:
            self.on_test(self.network_name, self.url)

    def update_status(self, status: str, color=None):
        """更新网络状态"""
        self.network_status = status
        if color:
            self.status_color = color
        if hasattr(self, 'status_label'):
            self.status_label.text = f"状态: {status}"
            self.status_label.color = self.status_color

    def update_url(self, new_url: str):
        """更新URL显示"""
        self.url = new_url
        if hasattr(self, 'url_label'):
            self.url_label.text = new_url

class NetworkScreen(BoxLayout):
    """网络设置界面"""
    
    def __init__(self, app, **kwargs):
        super(NetworkScreen, self).__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = responsive_spacing(16)
        self.spacing = responsive_spacing(12)

        self._create_ui()
        self._refresh_network_list()
    
    def _create_ui(self):
        """创建界面"""
        # 标题
        title_label = Label(
            text="网络设置",
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
            text="选择合适的网络环境访问教务系统\n校外网：定时开放，适合校外访问\n校内网：校园内部网络，访问更稳定",
            font_size=responsive_font_size(12),
            color=get_theme_color('text_secondary'),
            size_hint=(1, None),
            height=responsive_size(60),
            halign='center',
            valign='middle'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        self.add_widget(desc_label)
        
        # 网络列表容器
        self.network_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=responsive_spacing(12)
        )
        self.add_widget(self.network_container)
        
        # 底部按钮
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=responsive_size(50),
            spacing=responsive_spacing(8)
        )

        # 添加网络按钮
        add_button = AccentButton(
            text="添加网络",
            size_hint=(0.25, 1),
            font_size=responsive_font_size(12)
        )
        add_button.bind(on_release=self._on_add_network)
        button_layout.add_widget(add_button)

        # 测试所有按钮
        test_all_button = SecondaryButton(
            text="测试所有",
            size_hint=(0.25, 1),
            font_size=responsive_font_size(12)
        )
        test_all_button.bind(on_release=self._on_test_all)
        button_layout.add_widget(test_all_button)

        # 刷新按钮
        refresh_button = SecondaryButton(
            text="刷新",
            size_hint=(0.2, 1),
            font_size=responsive_font_size(12)
        )
        refresh_button.bind(on_release=self._on_refresh)
        button_layout.add_widget(refresh_button)

        # 返回按钮
        back_button = PrimaryButton(
            text="返回",
            size_hint=(0.3, 1),
            font_size=responsive_font_size(12)
        )
        back_button.bind(on_release=self._on_back)
        button_layout.add_widget(back_button)

        self.add_widget(button_layout)
    
    def _refresh_network_list(self):
        """刷新网络列表"""
        try:
            # 清空现有内容
            self.network_container.clear_widgets()
            
            # 获取网络状态
            network_status = get_network_status()
            current_network = network_status["current_network"]
            available_networks = network_status["available_networks"]
            
            # 创建网络卡片
            self.network_cards = {}  # 保存卡片引用
            for network_name in available_networks:
                # 获取网络配置信息
                network_configs = get_config("NETWORK_CONFIGS", {})
                if network_name in network_configs:
                    # 使用新的配置格式
                    network_config = network_configs[network_name]
                    url = network_config["base_url"]
                    description = network_config.get("description", f"{network_name}网络环境")
                else:
                    # 兼容旧的配置格式
                    network_urls = get_config("NETWORK_URLS", {})
                    url = network_urls.get(network_name, "")
                    description = f"{network_name}网络环境"

                is_current = (network_name == current_network)

                card = NetworkCard(
                    network_name=network_name,
                    url=url,
                    description=description,
                    is_current=is_current,
                    on_select=self._on_network_select,
                    on_edit=self._on_network_config,
                    on_delete=self._on_network_delete,
                    on_test=self._on_network_test,
                    on_quick_edit=self._on_network_quick_edit
                )
                self.network_cards[network_name] = card
                self.network_container.add_widget(card)
            
            logger.info(f"网络列表已刷新，当前网络: {current_network}")
            
        except Exception as e:
            logger.error(f"刷新网络列表失败: {e}")
            show_popup("错误", f"刷新网络列表失败: {str(e)}", "error")
    
    def _on_network_select(self, network_name: str):
        """选择网络"""
        try:
            logger.info(f"用户选择切换到: {network_name}")
            
            # 显示确认对话框
            def confirm_switch():
                success = switch_network(network_name)
                if success:
                    show_popup("成功", f"已切换到{network_name}", "success")
                    # 延迟刷新界面
                    Clock.schedule_once(lambda dt: self._refresh_network_list(), 0.5)
                else:
                    show_popup("错误", f"切换到{network_name}失败", "error")
            
            # 这里可以添加确认对话框，暂时直接切换
            confirm_switch()
            
        except Exception as e:
            logger.error(f"切换网络失败: {e}")
            show_popup("错误", f"切换网络失败: {str(e)}", "error")
    
    def _on_network_edit(self, network_name: str, current_url: str):
        """编辑网络URL"""
        try:
            logger.info(f"用户编辑网络URL: {network_name}")
            
            # 创建编辑对话框
            self._show_edit_dialog(network_name, current_url)
            
        except Exception as e:
            logger.error(f"编辑网络URL失败: {e}")
            show_popup("错误", f"编辑网络URL失败: {str(e)}", "error")
    
    def _on_network_config(self, network_name: str):
        """打开网络配置对话框"""
        try:
            # 获取网络配置
            network_configs = get_config("NETWORK_CONFIGS", {})
            network_config = network_configs.get(network_name, {})

            def on_save(name, config_data, is_new):
                try:
                    if is_new:
                        # 添加新网络
                        success = add_network_config(name, config_data["base_url"], **{k: v for k, v in config_data.items() if k != "base_url"})
                    else:
                        # 更新现有网络
                        success = update_network_config(name, **config_data)

                    if success:
                        show_popup("成功", f"网络配置已{'添加' if is_new else '更新'}", "success")
                        self._refresh_network_list()
                        return True
                    else:
                        show_popup("错误", f"{'添加' if is_new else '更新'}网络配置失败", "error")
                        return False
                except Exception as e:
                    logger.error(f"保存网络配置失败: {e}")
                    show_popup("错误", f"保存配置失败: {str(e)}", "error")
                    return False

            # 显示配置对话框
            dialog = NetworkConfigDialog(
                network_name=network_name,
                network_config=network_config,
                is_new=False,
                on_save=on_save
            )
            dialog.show()

        except Exception as e:
            logger.error(f"打开网络配置对话框失败: {e}")
            show_popup("错误", f"打开配置对话框失败: {str(e)}", "error")

    def _on_network_quick_edit(self, network_name: str, current_url: str):
        """快速编辑网络URL"""
        self._show_quick_edit_dialog(network_name, current_url)

    def _show_quick_edit_dialog(self, network_name: str, current_url: str):
        """显示快速编辑URL对话框"""
        # 创建编辑对话框
        content = BoxLayout(orientation='vertical', spacing=responsive_spacing(10), padding=responsive_spacing(20))

        # 标题
        title_label = Label(
            text=f"编辑 {network_name} 的URL",
            font_size=responsive_font_size(16),
            color=get_theme_color('text'),
            size_hint=(1, None),
            height=responsive_size(30)
        )
        content.add_widget(title_label)

        # URL输入框
        url_input = TextInput(
            text=current_url,
            multiline=False,
            size_hint=(1, None),
            height=responsive_size(40),
            font_size=responsive_font_size(14),
            foreground_color=get_theme_color('text'),
            background_color=get_theme_color('surface'),
            cursor_color=get_theme_color('primary')
        )
        content.add_widget(url_input)

        # 按钮布局
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=responsive_size(40), spacing=responsive_spacing(10))

        # 取消按钮
        cancel_button = SecondaryButton(text="取消", size_hint=(0.5, 1))

        # 保存按钮
        save_button = PrimaryButton(text="保存", size_hint=(0.5, 1))

        button_layout.add_widget(cancel_button)
        button_layout.add_widget(save_button)
        content.add_widget(button_layout)

        # 创建弹窗
        popup = Popup(
            title="",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        def on_save(instance):
            new_url = url_input.text.strip()
            if new_url and new_url != current_url:
                success = update_network_config(network_name, base_url=new_url)
                if success:
                    show_popup("成功", f"{network_name}的URL已更新", "success")
                    self._refresh_network_list()
                else:
                    show_popup("错误", f"更新{network_name}的URL失败", "error")
            popup.dismiss()

        def on_cancel(instance):
            popup.dismiss()

        save_button.bind(on_release=on_save)
        cancel_button.bind(on_release=on_cancel)

        popup.open()

    def _on_network_test(self, network_name: str, url: str):
        """测试网络连接"""
        try:
            logger.info(f"测试网络连接: {network_name} ({url})")

            # 更新状态为测试中
            if network_name in self.network_cards:
                self.network_cards[network_name].update_status("测试中...", get_theme_color('warning'))

            # 在后台线程中测试连接
            def test_connection():
                try:
                    # 测试登录页面
                    test_url = f"{url}/login"
                    resp = make_request(test_url, timeout=10)

                    if resp and resp.status_code == 200:
                        status = "连接正常"
                        color = get_theme_color('success')
                    else:
                        status = f"连接失败({resp.status_code if resp else '超时'})"
                        color = get_theme_color('error')

                except Exception as e:
                    status = f"连接失败({str(e)[:20]})"
                    color = get_theme_color('error')

                # 在主线程中更新UI
                Clock.schedule_once(lambda dt: self._update_test_result(network_name, status, color), 0)

            thread = threading.Thread(target=test_connection, daemon=True)
            thread.start()

        except Exception as e:
            logger.error(f"测试网络连接失败: {e}")
            if network_name in self.network_cards:
                self.network_cards[network_name].update_status("测试失败", get_theme_color('error'))

    def _update_test_result(self, network_name: str, status: str, color):
        """更新测试结果"""
        if network_name in self.network_cards:
            self.network_cards[network_name].update_status(status, color)

    def _on_network_delete(self, network_name: str):
        """删除网络配置"""
        try:
            # 确认删除
            def confirm_delete():
                success = remove_network_config(network_name)
                if success:
                    show_popup("成功", f"已删除网络配置: {network_name}", "success")
                    self._refresh_network_list()
                else:
                    show_popup("错误", f"删除网络配置失败: {network_name}", "error")

            # 显示确认对话框
            show_confirmation_dialog(
                "确认删除",
                f"确定要删除网络配置 '{network_name}' 吗？",
                confirm_delete
            )

        except Exception as e:
            logger.error(f"删除网络配置失败: {e}")
            show_popup("错误", f"删除网络配置失败: {str(e)}", "error")
    
    def _on_add_network(self, instance):
        """添加新网络"""
        try:
            def on_save(name, config_data, is_new):
                try:
                    # 检查名称是否已存在
                    available_networks = get_available_networks()
                    if name in available_networks:
                        show_popup("错误", f"网络名称 '{name}' 已存在", "error")
                        return False

                    # 添加新网络配置
                    success = add_network_config(name, config_data["base_url"], **{k: v for k, v in config_data.items() if k != "base_url"})
                    if success:
                        show_popup("成功", f"已添加网络: {name}", "success")
                        self._refresh_network_list()
                        return True
                    else:
                        show_popup("错误", "添加网络失败", "error")
                        return False
                except Exception as e:
                    logger.error(f"添加网络失败: {e}")
                    show_popup("错误", f"添加网络失败: {str(e)}", "error")
                    return False

            # 显示添加网络对话框
            dialog = NetworkConfigDialog(
                network_name="",
                network_config={},
                is_new=True,
                on_save=on_save
            )
            dialog.show()

        except Exception as e:
            logger.error(f"打开添加网络对话框失败: {e}")
            show_popup("错误", f"打开添加网络对话框失败: {str(e)}", "error")

    def _on_test_all(self, instance):
        """测试所有网络连接"""
        try:
            logger.info("开始测试所有网络连接")

            network_urls = get_config("NETWORK_URLS")
            for network_name, url in network_urls.items():
                self._on_network_test(network_name, url)

            show_popup("提示", "已开始测试所有网络连接", "info")

        except Exception as e:
            logger.error(f"测试所有网络失败: {e}")
            show_popup("错误", f"测试所有网络失败: {str(e)}", "error")

    def _on_refresh(self, instance):
        """刷新按钮点击"""
        self._refresh_network_list()
        show_popup("提示", "网络状态已刷新", "info")

    def _on_back(self, instance):
        """返回主界面"""
        self.app.show_main_screen()
