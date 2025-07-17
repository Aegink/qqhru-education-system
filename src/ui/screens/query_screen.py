#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询屏幕模块
成绩查询界面
"""

import logging
import threading
from typing import List
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
    PrimaryButton, SecondaryButton, show_popup, show_loading_dialog
)
from ...core.api import query_scores
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

class QueryScoresScreen(BoxLayout):
    """成绩查询界面屏幕"""
    
    def __init__(self, app, **kwargs):
        super(QueryScoresScreen, self).__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.spacing = 0
        self.padding = 0
        
        # 初始化会话管理器
        self.session_manager = SessionManager()
        self.loading_dialog = None
        
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
        
        self.content_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(600),
            spacing=responsive_spacing(16),
            padding=[responsive_spacing(16), responsive_spacing(24), 
                    responsive_spacing(16), responsive_spacing(24)]
        )
        
        # 创建查询控制卡片
        self._create_query_control_card()
        
        # 创建结果显示卡片
        self._create_results_card()
        
        content_scroll.add_widget(self.content_layout)
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
            text='成绩查询',
            size_hint=(1, 1),
            color=[1, 1, 1, 1],
            font_size=responsive_font_size(18),
            bold=True,
            halign='center',
            valign='middle'
        )
        
        app_bar.add_widget(back_button)
        app_bar.add_widget(title_label)
        
        self.add_widget(app_bar)
    
    def _create_query_control_card(self):
        """创建查询控制卡片"""
        control_card = ModernCard(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(120),
            elevation=2,
            padding=responsive_spacing(16),
            spacing=responsive_spacing(12)
        )
        
        # 标题
        title_label = StyledLabel(
            text='成绩查询',
            size_hint=(1, None),
            height=responsive_size(24),
            color=get_theme_color('primary'),
            bold=True,
            font_size=responsive_font_size(16)
        )
        
        # 说明文字
        info_label = StyledLabel(
            text='点击下方按钮查询本学期成绩',
            size_hint=(1, None),
            height=responsive_size(30),
            color=get_theme_color('text_secondary'),
            font_size=responsive_font_size(12),
            halign='center'
        )
        
        # 查询按钮
        query_button = PrimaryButton(
            text='查询本学期成绩',
            size_hint=(1, None),
            height=responsive_size(40),
            font_size=responsive_font_size(14)
        )
        query_button.bind(on_release=self.query_scores)
        
        control_card.add_widget(title_label)
        control_card.add_widget(info_label)
        control_card.add_widget(query_button)
        
        self.content_layout.add_widget(control_card)
    
    def _create_results_card(self):
        """创建结果显示卡片"""
        self.results_card = ModernCard(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(400),
            elevation=2,
            padding=responsive_spacing(16),
            spacing=responsive_spacing(12)
        )
        
        # 结果标题
        results_title = StyledLabel(
            text='查询结果',
            size_hint=(1, None),
            height=responsive_size(24),
            color=get_theme_color('primary'),
            bold=True,
            font_size=responsive_font_size(16)
        )
        
        # 结果内容区域
        self.results_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=True
        )
        
        self.results_content = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            spacing=responsive_spacing(8)
        )
        
        # 初始提示
        initial_label = StyledLabel(
            text='暂无查询结果',
            size_hint=(1, None),
            height=responsive_size(40),
            color=get_theme_color('text_secondary'),
            halign='center',
            valign='middle'
        )
        
        self.results_content.add_widget(initial_label)
        self.results_scroll.add_widget(self.results_content)
        
        self.results_card.add_widget(results_title)
        self.results_card.add_widget(self.results_scroll)
        
        self.content_layout.add_widget(self.results_card)
    
    def query_scores(self, instance):
        """查询成绩"""
        # 检查登录状态
        if not self.session_manager.get_current_account():
            show_popup("提示", "请先登录账号", "warning")
            return
        
        # 显示加载对话框
        self.loading_dialog = show_loading_dialog("查询中", "正在查询成绩，请稍候...")
        
        # 在后台线程中执行查询
        threading.Thread(target=self._query_thread).start()
    
    def _query_thread(self):
        """后台查询线程"""
        try:
            # 执行成绩查询
            success = query_scores(debug_mode=False)
            
            if success:
                Clock.schedule_once(lambda dt: self._query_success(), 0)
            else:
                Clock.schedule_once(lambda dt: self._query_failed(), 0)
                
        except Exception as e:
            logger.error(f"查询成绩时出错: {e}")
            Clock.schedule_once(lambda dt: self._query_error(str(e)), 0)
    
    def _query_success(self):
        """查询成功"""
        if self.loading_dialog:
            self.loading_dialog.dismiss()
        
        # 更新结果显示
        self._update_results("查询成功！成绩信息已显示在控制台中。")
        show_popup("成功", "成绩查询完成，请查看控制台输出", "success")
    
    def _query_failed(self):
        """查询失败"""
        if self.loading_dialog:
            self.loading_dialog.dismiss()
        
        self._update_results("查询失败，请检查网络连接或重新登录")
        show_popup("失败", "成绩查询失败，请重试", "error")
    
    def _query_error(self, error_msg: str):
        """查询出错"""
        if self.loading_dialog:
            self.loading_dialog.dismiss()
        
        self._update_results(f"查询出错: {error_msg}")
        show_popup("错误", f"查询过程中出错: {error_msg}", "error")
    
    def _update_results(self, message: str):
        """更新结果显示"""
        self.results_content.clear_widgets()
        
        result_label = StyledLabel(
            text=message,
            size_hint=(1, None),
            height=responsive_size(40),
            halign='center',
            valign='middle'
        )
        
        self.results_content.add_widget(result_label)
        self.results_content.height = responsive_size(40)
    
    def go_back(self, instance):
        """返回主界面"""
        self.app.show_main_screen()
