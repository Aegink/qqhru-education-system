#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号切换屏幕模块
管理和切换已保存的账号
"""

import logging
import threading
from typing import Dict, Any
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from ..themes import (
    get_theme_color, responsive_size, responsive_spacing, 
    responsive_font_size
)
from ..components import (
    PrimaryButton, SecondaryButton, ErrorButton,
    show_popup, show_confirmation_dialog
)
from ...core.session import SessionManager

logger = logging.getLogger(__name__)

class ModernCard(BoxLayout):
    """现代化卡片容器"""
    
    def __init__(self, elevation: int = 2, background_color: list = None, **kwargs):
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
        
        if 'text_size' not in kwargs:
            self.bind(size=self._update_text_size)

    def _update_text_size(self, instance, value):
        """更新文本大小"""
        if self.halign != 'center':
            self.text_size = (self.width, None)

class BackgroundBox(BoxLayout):
    """带背景色的布局容器"""
    
    def __init__(self, background_color: list = None, **kwargs):
        super(BackgroundBox, self).__init__(**kwargs)
        self.background_color = background_color or get_theme_color('secondary')
        
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, instance, value):
        """更新背景"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

class SwitchAccountScreen(BoxLayout):
    """账号切换界面屏幕"""
    
    def __init__(self, app, **kwargs):
        super(SwitchAccountScreen, self).__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.spacing = 0
        self.padding = 0
        
        # 初始化会话管理器
        self.session_manager = SessionManager()
        
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
            height=responsive_size(600),
            spacing=responsive_spacing(16),
            padding=[responsive_spacing(16), responsive_spacing(24), 
                    responsive_spacing(16), responsive_spacing(24)]
        )
        
        # 创建账号列表卡片
        self._create_accounts_card(content_layout)
        
        # 创建状态卡片
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
        
        # 返回按钮
        back_button = SecondaryButton(
            text='← 返回',
            size_hint=(None, None),
            size=(responsive_size(80), responsive_size(40)),
            pos_hint={'center_y': 0.5}
        )
        back_button.bind(on_release=self.go_back)
        
        # 标题
        title_label = StyledLabel(
            text='账号管理',
            size_hint=(1, 1),
            color=[1, 1, 1, 1],
            font_size=responsive_font_size(18),
            bold=True,
            halign='center',
            valign='middle'
        )
        
        # 刷新按钮
        refresh_button = SecondaryButton(
            text='刷新',
            size_hint=(None, None),
            size=(responsive_size(60), responsive_size(40)),
            pos_hint={'center_y': 0.5}
        )
        refresh_button.bind(on_release=self.refresh_accounts)
        
        app_bar.add_widget(back_button)
        app_bar.add_widget(title_label)
        app_bar.add_widget(refresh_button)
        
        self.add_widget(app_bar)
    
    def _create_accounts_card(self, parent_layout):
        """创建账号列表卡片"""
        accounts_card = ModernCard(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(400),
            elevation=2,
            padding=responsive_spacing(16),
            spacing=responsive_spacing(12)
        )
        
        # 标题
        title_label = StyledLabel(
            text='已保存的账号',
            size_hint=(1, None),
            height=responsive_size(24),
            color=get_theme_color('primary'),
            bold=True,
            font_size=responsive_font_size(16)
        )
        
        # 账号列表滚动区域
        accounts_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        self.accounts_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            spacing=responsive_spacing(4)
        )
        self.accounts_layout.bind(minimum_height=self.accounts_layout.setter('height'))
        
        accounts_scroll.add_widget(self.accounts_layout)
        
        accounts_card.add_widget(title_label)
        accounts_card.add_widget(accounts_scroll)
        
        parent_layout.add_widget(accounts_card)
    
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
    
    def refresh_accounts(self, instance=None):
        """刷新账号列表"""
        self.accounts_layout.clear_widgets()
        accounts = self.session_manager.list_accounts()
        
        if not accounts:
            no_accounts_label = StyledLabel(
                text='没有保存的账号',
                size_hint=(1, None),
                height=responsive_size(40),
                halign='center'
            )
            self.accounts_layout.add_widget(no_accounts_label)
            return
        
        # 添加表头
        header = BackgroundBox(
            size_hint=(1, None),
            height=responsive_size(40),
            background_color=get_theme_color('primary')
        )
        
        header.add_widget(StyledLabel(
            text='学号',
            size_hint=(0.5, 1),
            color=[1, 1, 1, 1],
            bold=True,
            halign='center'
        ))
        header.add_widget(StyledLabel(
            text='上次登录',
            size_hint=(0.3, 1),
            color=[1, 1, 1, 1],
            bold=True,
            halign='center'
        ))
        header.add_widget(Widget(size_hint=(0.2, 1)))  # 操作按钮占位
        
        self.accounts_layout.add_widget(header)
        
        # 添加账号行
        for student_id, account_info in accounts.items():
            last_login = account_info.get('last_login', '未知')
            
            account_layout = BackgroundBox(
                size_hint=(1, None),
                height=responsive_size(50),
                background_color=get_theme_color('secondary')
            )
            
            account_layout.add_widget(StyledLabel(
                text=f"{student_id}",
                size_hint=(0.5, 1),
                halign='center'
            ))
            account_layout.add_widget(StyledLabel(
                text=f"{last_login}",
                size_hint=(0.3, 1),
                halign='center'
            ))
            
            buttons_box = BoxLayout(
                size_hint=(0.2, 1),
                spacing=responsive_spacing(5)
            )
            
            switch_button = PrimaryButton(
                text='切换',
                size_hint=(0.5, 0.8),
                pos_hint={'center_y': 0.5},
                font_size=responsive_font_size(10)
            )
            switch_button.bind(on_release=partial(self.switch_account, student_id))
            
            delete_button = ErrorButton(
                text='删除',
                size_hint=(0.5, 0.8),
                pos_hint={'center_y': 0.5},
                font_size=responsive_font_size(10)
            )
            delete_button.bind(on_release=partial(self.delete_account, student_id))
            
            buttons_box.add_widget(switch_button)
            buttons_box.add_widget(delete_button)
            account_layout.add_widget(buttons_box)
            
            self.accounts_layout.add_widget(account_layout)

    def switch_account(self, student_id, instance):
        """切换到指定账号"""
        self._update_status(f'正在切换到账号 {student_id}...', 'info')

        # 在后台线程中执行切换操作
        threading.Thread(target=self._switch_account_thread, args=(student_id,)).start()

    def _switch_account_thread(self, student_id):
        """后台切换账号线程"""
        try:
            if self.session_manager.load_session(student_id):
                # 验证会话有效性
                if self.session_manager.verify_session(student_id):
                    Clock.schedule_once(lambda dt: self.switch_success(student_id), 0)
                else:
                    # 会话已过期
                    Clock.schedule_once(lambda dt: self.session_expired(student_id), 0)
            else:
                Clock.schedule_once(lambda dt: self._update_status(f'切换账号失败', 'error'), 0)
        except Exception as e:
            logger.error(f"切换账号时出错: {e}")
            Clock.schedule_once(lambda dt: self._update_status(f'切换账号出错: {str(e)}', 'error'), 0)

    def switch_success(self, student_id):
        """切换成功"""
        self._update_status(f'已切换到账号 {student_id}', 'success')
        show_popup("成功", f"已成功切换到账号 {student_id}", "success")

        # 延迟跳转到主界面
        Clock.schedule_once(lambda dt: self.app.show_main_screen(), 1)

    def session_expired(self, student_id):
        """会话已过期"""
        self._update_status(f'账号 {student_id} 会话已过期', 'warning')

        def relogin():
            self.app.show_login_screen()
            # 如果登录界面有学号输入框，可以预填充
            if hasattr(self.app, 'login_screen') and hasattr(self.app.login_screen, 'student_id_input'):
                self.app.login_screen.student_id_input.text = student_id

        show_confirmation_dialog(
            "会话已过期",
            f"账号 {student_id} 的会话已过期，是否重新登录？",
            on_confirm=relogin
        )

    def delete_account(self, student_id, instance):
        """删除指定账号"""
        def confirm_delete():
            if self.session_manager.delete_account(student_id):
                self._update_status(f'已删除账号 {student_id}', 'success')
                self.refresh_accounts()  # 刷新账号列表
                show_popup("成功", f"已删除账号 {student_id}", "success")
            else:
                self._update_status(f'删除账号 {student_id} 失败', 'error')
                show_popup("失败", f"删除账号 {student_id} 失败", "error")

        show_confirmation_dialog(
            "确认删除",
            f"确定要删除账号 {student_id} 吗？\n此操作将删除该账号的所有保存信息。",
            on_confirm=confirm_delete
        )

    def go_back(self, instance):
        """返回主界面"""
        self.app.show_main_screen()

    def _update_status(self, message: str, status_type: str = 'info'):
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

        # 5秒后清空状态信息（除了成功状态）
        if status_type != 'success':
            Clock.schedule_once(lambda dt: self._clear_status(), 5)

    def _clear_status(self):
        """清空状态信息"""
        self.status_label.text = ""
