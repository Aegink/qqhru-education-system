#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主屏幕模块
应用的主界面，显示账号状态和功能菜单
"""

import logging
import threading
from typing import Optional
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from ..themes import (
    get_theme_color, responsive_size, responsive_spacing, 
    responsive_font_size
)
from ..components import (
    ModernButton, PrimaryButton, SecondaryButton, AccentButton,
    show_popup, show_confirmation_dialog
)
from ...utils.font_manager import get_button_text
from ...core.session import SessionManager
from ...core.api import make_request, extract_student_name
from ...core.config import get_config, get_network_status
from ...core.session import SessionManager
from ...core.auto_login import get_auto_login_manager

logger = logging.getLogger(__name__)

class ModernCard(BoxLayout):
    """现代化卡片容器"""
    
    def __init__(self, elevation: int = 2, background_color: Optional[list] = None, **kwargs):
        super(ModernCard, self).__init__(**kwargs)
        
        self.elevation = elevation
        self.background_color = background_color or get_theme_color('surface')
        
        # 创建背景
        with self.canvas.before:
            # 阴影效果
            if elevation > 0:
                Color(*get_theme_color('shadow'))
                from kivy.graphics import RoundedRectangle
                self.shadow = RoundedRectangle(
                    pos=(self.x + responsive_size(elevation), self.y - responsive_size(elevation)),
                    size=self.size,
                    radius=[responsive_size(12)]
                )

            # 主背景
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[responsive_size(12)]
            )

        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, instance, value):
        """更新图形元素"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
        
        if hasattr(self, 'shadow'):
            self.shadow.pos = (self.x + responsive_size(self.elevation), 
                             self.y - responsive_size(self.elevation))
            self.shadow.size = self.size

class StyledLabel(Label):
    """样式化标签"""
    
    def __init__(self, **kwargs):
        super(StyledLabel, self).__init__(**kwargs)
        self.color = get_theme_color('text')
        self.font_size = responsive_font_size(14)
        self.halign = 'left'
        self.valign = 'middle'
        
        # 只有在需要时才设置text_size
        if 'text_size' not in kwargs:
            self.bind(size=self._update_text_size)

    def _update_text_size(self, instance, value):
        """更新文本大小"""
        if self.halign != 'center':
            self.text_size = (self.width, None)

class HeaderLabel(StyledLabel):
    """标题标签"""
    
    def __init__(self, **kwargs):
        super(HeaderLabel, self).__init__(**kwargs)
        self.font_size = responsive_font_size(20)
        self.color = get_theme_color('primary')
        self.bold = True
        self.halign = 'center'

class MainScreen(BoxLayout):
    """主界面屏幕"""
    
    def __init__(self, app, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.app = app
        self.session_manager = SessionManager()
        self.auto_login_manager = get_auto_login_manager()

        self.orientation = 'vertical'
        self.spacing = 0
        self.padding = 0

        # 设置自动登录回调
        self.auto_login_manager.on_status_change = self._on_auto_login_status_change
        self.auto_login_manager.on_login_success = self._on_auto_login_success
        self.auto_login_manager.on_login_failed = self._on_auto_login_failed

        # 设置背景色
        with self.canvas.before:
            Color(*get_theme_color('background'))
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self._create_ui()
    
    def _update_bg(self, instance, value):
        """更新背景"""
        if hasattr(self, 'bg'):
            self.bg.pos = self.pos
            self.bg.size = self.size
    
    def _create_ui(self):
        """创建用户界面"""
        # 创建顶部应用栏
        self._create_app_bar()
        
        # 主内容区域
        content_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        content_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(800),
            spacing=responsive_spacing(16),
            padding=[responsive_spacing(16), responsive_spacing(24), 
                    responsive_spacing(16), responsive_spacing(24)]
        )
        
        # 创建各个卡片
        self._create_account_card(content_layout)
        self._create_functions_card(content_layout)
        self._create_status_card(content_layout)
        
        content_scroll.add_widget(content_layout)
        self.add_widget(content_scroll)
    
    def _create_app_bar(self):
        """创建顶部应用栏"""
        app_bar = ModernCard(
            orientation='horizontal',
            size_hint=(1, None),
            height=responsive_size(64),
            elevation=2,
            background_color=get_theme_color('primary'),
            padding=[responsive_spacing(16), 0, responsive_spacing(16), 0]
        )
        
        # 应用标题
        title_label = HeaderLabel(
            text='齐齐哈尔大学教务系统',
            size_hint=(1, 1),
            color=[1, 1, 1, 1],
            halign='left',
            valign='middle',
            text_size=(None, responsive_size(64))
        )
        app_bar.add_widget(title_label)
        
        self.add_widget(app_bar)
    
    def _create_account_card(self, parent_layout):
        """创建账号信息卡片"""
        account_card = ModernCard(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(140),
            elevation=2,
            padding=responsive_spacing(16)
        )
        
        account_title = StyledLabel(
            text='账号状态',
            size_hint=(1, None),
            height=responsive_size(24),
            color=get_theme_color('primary'),
            bold=True,
            font_size=responsive_font_size(16)
        )
        
        self.account_info = StyledLabel(
            text='当前未登录',
            size_hint=(1, None),
            height=responsive_size(40),
            halign='center',
            valign='middle',
            font_size=responsive_font_size(16)
        )
        
        # 自动登录状态
        self.auto_login_status = StyledLabel(
            text='自动登录: 未启用',
            size_hint=(1, None),
            height=responsive_size(30),
            halign='center',
            font_size=responsive_font_size(12),
            color=get_theme_color('text_secondary')
        )
        
        # 自动登录控制按钮
        auto_login_controls = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=responsive_size(36),
            spacing=responsive_spacing(12)
        )
        
        self.toggle_auto_login_btn = SecondaryButton(
            text='启用自动登录',
            size_hint=(0.6, 1),
            font_size=responsive_font_size(12)
        )
        
        self.check_status_btn = SecondaryButton(
            text='检查状态',
            size_hint=(0.4, 1),
            font_size=responsive_font_size(12)
        )
        
        # 绑定事件
        self.toggle_auto_login_btn.bind(on_release=self.toggle_auto_login)
        self.check_status_btn.bind(on_release=self.check_auto_login_status)
        
        auto_login_controls.add_widget(self.toggle_auto_login_btn)
        auto_login_controls.add_widget(self.check_status_btn)
        
        account_card.add_widget(account_title)
        account_card.add_widget(self.account_info)
        account_card.add_widget(self.auto_login_status)
        account_card.add_widget(auto_login_controls)
        
        parent_layout.add_widget(account_card)
    
    def _create_functions_card(self, parent_layout):
        """创建功能菜单卡片"""
        functions_card = ModernCard(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(360),
            elevation=2,
            padding=responsive_spacing(16),
            spacing=responsive_spacing(16)
        )
        
        functions_title = StyledLabel(
            text='功能菜单',
            size_hint=(1, None),
            height=responsive_size(24),
            color=get_theme_color('primary'),
            bold=True,
            font_size=responsive_font_size(16)
        )
        functions_card.add_widget(functions_title)
        
        # 功能按钮
        buttons_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=responsive_spacing(12)
        )
        
        # 创建各个功能按钮
        self._create_function_buttons(buttons_layout)
        
        functions_card.add_widget(buttons_layout)
        parent_layout.add_widget(functions_card)
    
    def _create_function_buttons(self, parent_layout):
        """创建功能按钮"""
        # 登录按钮
        login_button = PrimaryButton(
            text=get_button_text('login_new'),
            font_size=responsive_font_size(14)
        )
        login_button.bind(on_release=self.show_login)
        
        # 切换账号按钮
        switch_button = PrimaryButton(
            text=get_button_text('switch_account'),
            font_size=responsive_font_size(14)
        )
        switch_button.bind(on_release=self.show_switch_account)
        
        # 查询成绩按钮
        query_button = AccentButton(
            text=get_button_text('query_scores'),
            font_size=responsive_font_size(14)
        )
        query_button.bind(on_release=self.show_query_scores)
        
        # 管理账号按钮
        manage_button = PrimaryButton(
            text=get_button_text('manage_accounts'),
            font_size=responsive_font_size(14)
        )
        manage_button.bind(on_release=self.show_manage_accounts)

        # 网络设置按钮
        network_button = SecondaryButton(
            text="网络设置",
            font_size=responsive_font_size(14)
        )
        network_button.bind(on_release=self.show_network_settings)

        # 配置管理按钮
        config_button = SecondaryButton(
            text="配置管理",
            font_size=responsive_font_size(14)
        )
        config_button.bind(on_release=self.show_config_management)

        # 退出按钮
        exit_button = SecondaryButton(
            text=get_button_text('exit_app'),
            font_size=responsive_font_size(14)
        )
        exit_button.bind(on_release=self.exit_app)

        parent_layout.add_widget(login_button)
        parent_layout.add_widget(switch_button)
        parent_layout.add_widget(query_button)
        parent_layout.add_widget(manage_button)
        parent_layout.add_widget(network_button)
        parent_layout.add_widget(config_button)
        parent_layout.add_widget(exit_button)
    
    def _create_status_card(self, parent_layout):
        """创建状态信息卡片"""
        status_card = ModernCard(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(80),
            elevation=1,
            padding=responsive_spacing(16)
        )
        
        status_title = StyledLabel(
            text='状态信息',
            size_hint=(1, None),
            height=responsive_size(24),
            color=get_theme_color('text_secondary'),
            font_size=responsive_font_size(12)
        )
        
        self.status_label = StyledLabel(
            text='',
            size_hint=(1, None),
            height=responsive_size(30),
            halign='center'
        )
        
        status_card.add_widget(status_title)
        status_card.add_widget(self.status_label)

        parent_layout.add_widget(status_card)

    def update_account_info(self):
        """更新当前账号信息"""
        # 更新网络状态
        self._update_network_status()

        # 更新自动登录状态
        self._update_auto_login_status()

        current_account = self.session_manager.get_current_account()
        if current_account:
            # 尝试获取学生姓名
            try:
                resp = make_request(get_config("SCORES_URL"), timeout=10)
                if resp and resp.status_code == 200 and "login" not in resp.url:
                    student_name = extract_student_name(resp.text)
                    if student_name:
                        self.account_info.text = f"当前登录: {student_name}({current_account})"
                        self.account_info.color = get_theme_color('success')
                    else:
                        self.account_info.text = f"当前登录: {current_account}"
                        self.account_info.color = get_theme_color('primary')
                else:
                    self.account_info.text = f"当前账号: {current_account} (会话可能已过期)"
                    self.account_info.color = get_theme_color('error')
            except Exception as e:
                logger.error(f"更新账号信息失败: {e}")
                self.account_info.text = f"当前账号: {current_account} (状态未知)"
                self.account_info.color = get_theme_color('warning')
        else:
            self.account_info.text = "当前未登录"
            self.account_info.color = get_theme_color('text')

    def _update_network_status(self):
        """更新网络状态显示"""
        try:
            network_status = get_network_status()
            current_network = network_status["current_network"]
            base_url = network_status["base_url"]

            # 更新状态标签显示网络信息
            network_info = f"网络: {current_network} ({base_url})"
            self.update_status(network_info, 'info')

        except Exception as e:
            logger.error(f"更新网络状态失败: {e}")
            self.update_status("网络状态未知", 'warning')

    def _update_auto_login_status(self):
        """更新自动登录状态显示"""
        try:
            status = self.auto_login_manager.check_status()

            # 更新状态文本
            if hasattr(self, 'auto_login_status'):
                status_text = f"自动登录: {status.get('description', '未知')}"
                self.auto_login_status.text = status_text

                # 设置状态颜色
                status_type = status.get('status_type', 'info')
                if status_type == 'success':
                    self.auto_login_status.color = get_theme_color('success')
                elif status_type == 'error':
                    self.auto_login_status.color = get_theme_color('error')
                elif status_type == 'warning':
                    self.auto_login_status.color = get_theme_color('warning')
                else:
                    self.auto_login_status.color = get_theme_color('text_secondary')

            # 更新按钮文本
            if hasattr(self, 'toggle_auto_login_btn'):
                if status.get('enabled', False):
                    self.toggle_auto_login_btn.text = "禁用自动登录"
                else:
                    self.toggle_auto_login_btn.text = "启用自动登录"

        except Exception as e:
            logger.error(f"更新自动登录状态失败: {e}")

    def _on_auto_login_status_change(self, status_text: str, status_type: str):
        """自动登录状态变化回调"""
        try:
            # 更新状态显示
            self._update_auto_login_status()
            logger.info(f"自动登录状态变化: {status_text}")
        except Exception as e:
            logger.error(f"处理自动登录状态变化失败: {e}")

    def _on_auto_login_success(self):
        """自动登录成功回调"""
        try:
            show_popup("自动登录", "自动登录成功", "success")
            # 更新账号信息
            self.update_account_info()
            logger.info("自动登录成功")
        except Exception as e:
            logger.error(f"处理自动登录成功回调失败: {e}")

    def _on_auto_login_failed(self):
        """自动登录失败回调"""
        try:
            show_popup("自动登录", "自动登录失败，请手动重新登录", "warning")
            logger.warning("自动登录失败")
        except Exception as e:
            logger.error(f"处理自动登录失败回调失败: {e}")

    def show_login(self, instance):
        """显示登录界面"""
        self.app.show_login_screen()

    def show_switch_account(self, instance):
        """显示切换账号界面"""
        self.app.show_switch_account_screen()

    def show_query_scores(self, instance):
        """显示成绩查询界面"""
        if self.session_manager.get_current_account():
            self.app.show_query_scores_screen()
        else:
            self.status_label.text = "请先登录"
            self.status_label.color = get_theme_color('error')
            show_popup("提示", "请先登录账号", "warning")

    def show_manage_accounts(self, instance):
        """显示账号管理界面"""
        self.app.show_switch_account_screen()

    def show_network_settings(self, instance):
        """显示网络设置界面"""
        try:
            self.app.show_network_screen()
        except Exception as e:
            logger.error(f"显示网络设置界面失败: {e}")
            show_popup("错误", f"显示网络设置界面失败: {str(e)}", "error")

    def show_config_management(self, instance):
        """显示配置管理界面"""
        try:
            self.app.show_config_screen()
        except Exception as e:
            logger.error(f"显示配置管理界面失败: {e}")
            show_popup("错误", f"显示配置管理界面失败: {str(e)}", "error")

    def exit_app(self, instance):
        """退出应用"""
        def confirm_exit():
            self.app.stop()

        show_confirmation_dialog(
            "确认退出",
            "确定要退出应用吗？",
            on_confirm=confirm_exit
        )

    def toggle_auto_login(self, instance):
        """切换自动登录状态"""
        try:
            current_account = self.session_manager.get_current_account()
            if not current_account:
                show_popup("提示", "请先登录账号才能启用自动登录", "warning")
                return

            if self.auto_login_manager.is_enabled():
                # 禁用自动登录
                success = self.auto_login_manager.disable_auto_login()
                if success:
                    show_popup("成功", "自动登录已禁用", "success")
                else:
                    show_popup("错误", "禁用自动登录失败", "error")
            else:
                # 启用自动登录
                if not self.session_manager.is_session_valid():
                    show_popup("提示", "当前会话无效，请重新登录后再启用自动登录", "warning")
                    return

                success = self.auto_login_manager.enable_auto_login()
                if success:
                    show_popup("成功", "自动登录已启用，将定期检查会话状态", "success")
                else:
                    show_popup("错误", "启用自动登录失败", "error")

            # 更新界面状态
            self._update_auto_login_status()

        except Exception as e:
            logger.error(f"切换自动登录状态失败: {e}")
            show_popup("错误", f"操作失败: {str(e)}", "error")

    def check_auto_login_status(self, instance):
        """检查自动登录状态"""
        try:
            # 强制执行一次状态检查
            self.auto_login_manager.force_check_now()

            # 获取详细状态
            status = self.auto_login_manager.check_status()

            # 构建状态信息
            status_info = []
            status_info.append(f"启用状态: {'是' if status.get('enabled') else '否'}")
            status_info.append(f"当前账号: {status.get('current_account', '无')}")
            status_info.append(f"会话状态: {'有效' if status.get('session_valid') else '无效'}")
            status_info.append(f"监控状态: {'运行中' if status.get('is_checking') else '未运行'}")

            last_check = status.get('last_check_time', 0)
            if last_check > 0:
                import datetime
                last_check_str = datetime.datetime.fromtimestamp(last_check).strftime('%Y-%m-%d %H:%M:%S')
                status_info.append(f"上次检查: {last_check_str}")

            check_interval = status.get('check_interval', 300)
            status_info.append(f"检查间隔: {check_interval // 60}分钟")

            status_text = "\n".join(status_info)
            show_popup("自动登录状态", status_text, status.get('status_type', 'info'))

            # 更新界面状态
            self._update_auto_login_status()

        except Exception as e:
            logger.error(f"检查自动登录状态失败: {e}")
            show_popup("错误", f"检查状态失败: {str(e)}", "error")

    def update_status(self, message: str, status_type: str = 'info'):
        """更新状态信息

        Args:
            message: 状态消息
            status_type: 状态类型 ('info', 'success', 'warning', 'error')
        """
        self.status_label.text = message

        status_colors = {
            'info': get_theme_color('info'),
            'success': get_theme_color('success'),
            'warning': get_theme_color('warning'),
            'error': get_theme_color('error')
        }

        self.status_label.color = status_colors.get(status_type, get_theme_color('text'))

        # 5秒后清空状态信息
        Clock.schedule_once(lambda dt: self._clear_status(), 5)

    def _clear_status(self):
        """清空状态信息"""
        self.status_label.text = ""
