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
from kivy.core.window import Window

from ..themes import (
    get_theme_color, responsive_size, responsive_spacing,
    responsive_font_size, get_grade_color_and_style
)
from ..components import (
    PrimaryButton, SecondaryButton, show_popup, show_loading_dialog
)
from ...core.api import query_scores, get_scores_data
from ...core.session import get_session_manager

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
        # 只有当宽度大于0时才设置text_size，避免文本无法显示
        if self.width > 0:
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
        self.session_manager = get_session_manager()
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
            # 获取成绩数据
            success, scores_data, student_name = get_scores_data(debug_mode=False)

            if success:
                Clock.schedule_once(lambda dt: self._query_success(scores_data, student_name), 0)
            else:
                Clock.schedule_once(lambda dt: self._query_failed(), 0)

        except Exception as e:
            logger.error(f"查询成绩时出错: {e}")
            Clock.schedule_once(lambda dt: self._query_error(str(e)), 0)
    
    def _query_success(self, scores_data: list, student_name: str):
        """查询成功"""
        if self.loading_dialog:
            self.loading_dialog.dismiss()

        # 显示成绩数据
        self._display_scores(scores_data, student_name)
        show_popup("成功", f"成功查询到 {len(scores_data)} 门课程的成绩", "success")
    
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
    
    def _calculate_text_width(self, text: str, font_size: float, bold: bool = False) -> float:
        """精确计算文字的显示宽度"""
        from kivy.uix.label import Label

        if not text or text == '-':
            return responsive_size(20)  # 为空值或短横线预留最小宽度

        # 创建临时标签来测量文字宽度，使用实际的字体设置
        temp_label = Label(
            text=str(text),
            font_size=font_size,
            bold=bold,
            text_size=(None, None)
        )
        temp_label.texture_update()

        # 获取实际宽度，如果无法获取则使用估算
        if temp_label.texture_size:
            actual_width = temp_label.texture_size[0]
        else:
            # 备用估算：中文字符按字体大小计算，英文字符按字体大小的0.6倍计算
            chinese_chars = len([c for c in str(text) if ord(c) > 127])
            english_chars = len(str(text)) - chinese_chars
            actual_width = chinese_chars * font_size + english_chars * font_size * 0.6

        return actual_width

    def _get_card_content_width(self) -> float:
        """获取卡片内容的实际宽度（与查询按钮宽度一致）"""
        # 获取整个窗口宽度作为基准
        base_width = Window.width

        # 计算容器的padding总和
        # content_layout 左右padding: responsive_spacing(16) * 2 = 32
        content_padding = responsive_spacing(16) * 2

        # results_card (ModernCard) padding: responsive_spacing(16) * 2 = 32
        card_padding = responsive_spacing(16) * 2

        # 总的padding（这就是卡片内容的实际可用宽度）
        total_padding = content_padding + card_padding

        card_content_width = base_width - total_padding

        # 确保最小宽度
        min_width = responsive_size(300)
        return max(card_content_width, min_width)

    def _calculate_optimal_column_widths(self, scores_data: list) -> tuple[dict, float, bool]:
        """计算最优的列宽分配，智能利用屏幕空间，必要时启用水平滚动"""
        import logging
        logger = logging.getLogger(__name__)

        font_size = responsive_font_size(10)
        header_font_size = responsive_font_size(11)

        # 获取卡片内容宽度（与查询按钮宽度一致）
        card_width = self._get_card_content_width()
        logger.info(f"卡片内容宽度: {card_width:.1f}px")

        # 定义所有列的配置，移除绩点列
        all_columns = {
            'course_name': {'header': '课程名称', 'content_list': [], 'min_width': responsive_size(150)},
            'credit': {'header': '学分', 'content_list': [], 'min_width': responsive_size(60)},
            'grade': {'header': '成绩', 'content_list': [], 'min_width': responsive_size(70)},
            'type': {'header': '课程属性', 'content_list': [], 'min_width': responsive_size(80)}
        }

        # 收集所有内容，移除绩点列
        for score in scores_data:
            all_columns['course_name']['content_list'].append(score.get('课程名', score.get('课程名称', '')))
            all_columns['credit']['content_list'].append(str(score.get('学分', '')) if score.get('学分', '') else '-')
            all_columns['grade']['content_list'].append(str(score.get('成绩', '')) if score.get('成绩', '') else '-')
            all_columns['type']['content_list'].append(str(score.get('课程属性', '')) if score.get('课程属性', '') else '-')

        # 第一步：计算每列的内容需求宽度
        column_widths = {}
        total_content_width = 0

        for col_key, col_info in all_columns.items():
            # 计算表头宽度
            header_width = self._calculate_text_width(col_info['header'], header_font_size, bold=True)

            # 计算内容最大宽度
            max_content_width = 0
            for content in col_info['content_list']:
                content_width = self._calculate_text_width(content, font_size, bold=(col_key == 'grade'))
                max_content_width = max(max_content_width, content_width)

            # 取表头和内容的最大宽度，并添加padding
            cell_padding = responsive_spacing(20)  # 增加padding让内容更舒适
            content_width = max(header_width, max_content_width) + cell_padding

            # 确保不小于最小宽度
            required_width = max(content_width, col_info['min_width'])

            # 对课程名称列进行特殊处理，限制最大宽度避免过度扩展
            if col_key == 'course_name':
                max_course_name_width = responsive_size(250)  # 限制课程名称列的最大宽度
                required_width = min(required_width, max_course_name_width)

            column_widths[col_key] = {
                'required_width': required_width,
                'min_width': col_info['min_width']
            }
            total_content_width += required_width

            logger.info(f"{col_info['header']}列内容需求: {required_width:.1f}px")

        logger.info(f"内容总宽度: {total_content_width:.1f}px")

        # 滚动模式：ScrollView宽度为卡片宽度，表格内容保持实际宽度
        logger.info(f"使用滚动模式，ScrollView宽度: {card_width:.1f}px")

        # ScrollView的显示宽度为卡片宽度
        scroll_view_width = card_width

        # 表格内容宽度为实际需要的宽度
        final_table_width = total_content_width

        # 保持列的原始宽度，不进行压缩或扩展
        for col_key in column_widths.keys():
            column_widths[col_key]['final_width'] = column_widths[col_key]['required_width']

        # 始终启用水平滚动，让用户可以滑动查看所有内容
        needs_scroll = True

        # 输出最终列宽
        for col_key, col_info in zip(column_widths.keys(), all_columns.values()):
            final_width = column_widths[col_key]['final_width']
            logger.info(f"{col_info['header']}列最终宽度: {final_width:.1f}px")

        logger.info(f"ScrollView宽度: {scroll_view_width:.1f}px")
        logger.info(f"表格内容宽度: {final_table_width:.1f}px")
        logger.info(f"需要水平滚动: {'是' if needs_scroll else '否'}")

        return column_widths, final_table_width, needs_scroll, scroll_view_width

    def _display_scores(self, scores_data: list, student_name: str):
        """显示成绩数据"""
        self.results_content.clear_widgets()

        if not scores_data:
            card_content_width = self._get_card_content_width()
            no_data_label = StyledLabel(
                text="暂无成绩数据",
                size_hint=(None, None),
                width=card_content_width,
                height=responsive_size(40),
                font_size=responsive_font_size(12),
                color=get_theme_color('text_secondary'),
                halign='center',
                valign='middle'
            )
            no_data_label.text_size = (card_content_width, None)
            self.results_content.add_widget(no_data_label)
            self.results_content.height = responsive_size(40)
            # 设置宽度以确保正确显示
            self.results_content.width = card_content_width
            return

        # 计算卡片内容宽度
        card_content_width = self._get_card_content_width()

        # 添加标题
        title_label = StyledLabel(
            text=f"{student_name}的本学期成绩 (共{len(scores_data)}门课程)",
            size_hint=(None, None),
            width=card_content_width,
            height=responsive_size(40),
            font_size=responsive_font_size(14),
            color=get_theme_color('primary'),
            bold=True,
            halign='left',
            valign='middle'
        )
        # 确保标题文本能够正确显示
        title_label.text_size = (card_content_width, None)
        self.results_content.add_widget(title_label)

        # 计算最优列宽
        column_widths, final_table_width, needs_scroll, scroll_view_width = self._calculate_optimal_column_widths(scores_data)

        # 创建双向滚动容器（固定宽度，与卡片宽度一致）
        table_scroll = ScrollView(
            size_hint=(None, None),
            width=scroll_view_width,  # 使用卡片宽度
            height=responsive_size(400),
            do_scroll_x=True,  # 启用水平滚动
            do_scroll_y=True,  # 启用垂直滚动
            scroll_type=['bars'],  # 始终显示滚动条
            bar_width=responsive_size(12),
            bar_color=get_theme_color('primary'),
            bar_inactive_color=get_theme_color('text_secondary'),
            scroll_timeout=1000,
            bar_margin=responsive_size(2)
        )

        # 创建表格容器（使用实际内容宽度，高度将根据内容动态设置）
        table_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=final_table_width,  # 使用实际内容宽度
            spacing=0
        )

        # 创建表头（使用实际内容宽度）
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            width=final_table_width,  # 使用实际内容宽度
            height=responsive_size(42),
            spacing=0
        )

        # 添加表头背景色
        with header_layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.95, 0.95, 0.95, 1)
            self.header_bg_rect = Rectangle(pos=header_layout.pos, size=header_layout.size)
        header_layout.bind(pos=self._update_header_bg, size=self._update_header_bg)

        # 创建表头单元格，移除绩点列
        header_configs = [
            ('course_name', '课程名称', 'left'),
            ('credit', '学分', 'center'),
            ('grade', '成绩', 'center'),
            ('type', '课程属性', 'center')
        ]

        for i, (col_key, header_text, align) in enumerate(header_configs):
            final_width = column_widths[col_key]['final_width']

            # 使用固定像素宽度（滚动模式）
            header_cell = BoxLayout(
                orientation='vertical',
                size_hint=(None, 1),
                width=final_width
            )

            # 添加右边框（除了最后一列）
            if i < len(header_configs) - 1:
                with header_cell.canvas.after:
                    Color(0.8, 0.8, 0.8, 1)
                    Rectangle(pos=(header_cell.right - 1, header_cell.y), size=(1, header_cell.height))
                header_cell.bind(pos=self._update_cell_border, size=self._update_cell_border)

            # 创建内容容器
            content_container = BoxLayout(
                orientation='vertical',
                padding=[responsive_spacing(8), responsive_spacing(8), responsive_spacing(8), responsive_spacing(8)]
            )

            header_label = StyledLabel(
                text=header_text,
                size_hint=(1, 1),
                font_size=responsive_font_size(11),
                color=get_theme_color('text'),
                bold=True,
                halign=align,
                valign='middle'
            )

            content_container.add_widget(header_label)
            header_cell.add_widget(content_container)
            header_layout.add_widget(header_cell)

        # 创建数据容器（使用实际内容宽度）
        data_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=final_table_width,  # 使用实际内容宽度
            spacing=0
        )

        # 不添加测试标签，直接处理数据

        # 对成绩数据进行排序（按课程名称排序）
        sorted_scores = sorted(scores_data, key=lambda x: x.get('课程名', x.get('课程名称', '')))

        # 调试：输出所有课程名称
        logger.info("所有课程列表:")
        for i, score in enumerate(sorted_scores):
            course_name = score.get('课程名', score.get('课程名称', ''))
            logger.info(f"  {i+1}. {course_name}")

        # 先创建所有数据行，然后反向添加到容器中
        data_rows = []
        data_height = 0

        # 创建所有数据行
        for i, score in enumerate(sorted_scores):
            course_name = score.get('课程名', score.get('课程名称', ''))
            logger.info(f"正在处理第{i+1}行: {course_name}")

            # 创建数据行（使用实际内容宽度）
            row_height = responsive_size(44)
            score_layout = BoxLayout(
                orientation='horizontal',
                size_hint=(None, None),
                width=final_table_width,  # 使用实际内容宽度
                height=row_height,
                spacing=0
            )



            # 添加行背景色（交替显示）
            bg_color = (0.98, 0.98, 0.98, 1) if i % 2 == 1 else (1, 1, 1, 1)
            with score_layout.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(*bg_color)
                self.row_bg_rect = Rectangle(pos=score_layout.pos, size=score_layout.size)
            score_layout.bind(pos=self._update_row_bg, size=self._update_row_bg)

            # 准备单元格数据
            course_name = score.get('课程名', score.get('课程名称', ''))
            credit = str(score.get('学分', '')) if score.get('学分', '') else '-'

            # 处理成绩单元格（需要特殊颜色处理）
            grade = score.get('成绩', '')
            grade_text = str(grade) if grade else '-'
            course_type = str(score.get('课程属性', '')) if score.get('课程属性', '') else '-'

            # 处理成绩单元格（使用新的颜色分级系统）
            grade = score.get('成绩', '')
            grade_text = str(grade) if grade else '-'

            # 使用新的成绩颜色分级函数
            grade_color, grade_bold = get_grade_color_and_style(grade)

            course_type = str(score.get('课程属性', '')) if score.get('课程属性', '') else '-'

            # 创建数据单元格配置，移除绩点列
            # 创建数据单元格配置，移除绩点列
            cell_configs = [
                ('course_name', course_name, 'left', get_theme_color('text'), False),
                ('credit', credit, 'center', get_theme_color('text'), False),
                ('grade', grade_text, 'center', grade_color, grade_bold),
                ('type', course_type, 'center', get_theme_color('text_secondary'), False)
            ]

            # 添加数据单元格
            for j, (col_key, text, align, color, bold) in enumerate(cell_configs):
                final_width = column_widths[col_key]['final_width']

                # 使用固定像素宽度（滚动模式）
                cell_container = BoxLayout(
                    orientation='vertical',
                    size_hint=(None, 1),
                    width=final_width
                )

                # 添加右边框（除了最后一列）
                if j < len(cell_configs) - 1:
                    with cell_container.canvas.after:
                        Color(0.9, 0.9, 0.9, 1)
                        Rectangle(pos=(cell_container.right - 1, cell_container.y), size=(1, cell_container.height))
                    cell_container.bind(pos=self._update_cell_border, size=self._update_cell_border)

                # 创建内容容器
                content_container = BoxLayout(
                    orientation='vertical',
                    padding=[responsive_spacing(8), responsive_spacing(6), responsive_spacing(8), responsive_spacing(6)]
                )

                # 计算可用宽度
                available_cell_width = final_width - responsive_spacing(16)

                # 直接使用Kivy Label，避免StyledLabel的潜在问题
                from kivy.uix.label import Label
                cell_label = Label(
                    text=text,
                    size_hint=(1, 1),
                    font_size=responsive_font_size(10),
                    color=color,
                    halign=align,
                    valign='middle',
                    bold=bold,
                    text_size=(available_cell_width, None)  # 明确设置text_size
                )



                content_container.add_widget(cell_label)
                cell_container.add_widget(content_container)
                score_layout.add_widget(cell_container)

            # 添加底部边框
            with score_layout.canvas.after:
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=(score_layout.x, score_layout.y), size=(score_layout.width, 1))

            # 将数据行添加到列表中，稍后统一添加到容器
            data_rows.append((score_layout, course_name))
            data_height += responsive_size(44)

        # 反向添加数据行到容器中（最后一行先添加，第一行最后添加）
        # 这样确保第一行能够正确显示
        for score_layout, course_name in reversed(data_rows):
            data_container.add_widget(score_layout)

        # 设置数据容器高度
        data_container.height = data_height

        # 正确的顺序：先添加表头，再添加数据容器
        table_container.add_widget(header_layout)
        table_container.add_widget(data_container)

        # 设置表格容器的总高度
        total_table_height = responsive_size(42) + data_height  # 表头高度 + 数据高度
        table_container.height = total_table_height

        # 计算ScrollView的合适高度
        # 根据数据量动态调整最大高度，确保能显示所有数据
        base_max_height = 450  # 增加基础最大高度
        if len(sorted_scores) <= 10:
            # 10条以下数据时，让表格完全显示
            max_scroll_height = total_table_height
        else:
            # 大量数据时，限制最大高度并启用滚动
            max_scroll_height = responsive_size(base_max_height)

        scroll_height = min(total_table_height, max_scroll_height)

        # 记录高度计算信息
        logger.info(f"原始数据行数: {len(scores_data)}")
        logger.info(f"排序后数据行数: {len(sorted_scores)}")
        logger.info(f"实际添加的行数: {i + 1}")
        logger.info(f"数据容器高度: {data_height:.1f}px")
        logger.info(f"表格总高度: {total_table_height:.1f}px")
        logger.info(f"ScrollView高度: {scroll_height:.1f}px")
        logger.info(f"需要垂直滚动: {'是' if total_table_height > max_scroll_height else '否'}")

        # 更新ScrollView高度
        table_scroll.height = scroll_height

        # 将表格容器添加到滚动视图
        table_scroll.add_widget(table_container)

        # 确保ScrollView滚动到正确位置，显示表头和第一行数据
        def scroll_to_show_data(*args):
            content_height = table_container.height
            viewport_height = table_scroll.height

            if content_height > viewport_height:
                # 第一行的y位置是950.4，表头的y位置是1029.6
                # 视口范围是0.0-810.0，所以第一行不在视口内
                # 我们需要调整滚动位置，让第一行进入视口

                if data_container.children:
                    first_row = data_container.children[-1]  # 最后添加的是第一个显示的
                    first_row_y = first_row.y
                    first_row_height = first_row.height

                    # 计算需要的滚动位置，让第一行的底部刚好在视口顶部
                    # scroll_y = 0 表示显示内容的底部，scroll_y = 1 表示显示内容的顶部
                    # 我们需要让第一行的底部(y + height)在视口的顶部(810)
                    target_y_top = first_row_y + first_row_height  # 第一行的顶部

                    # 计算滚动比例：我们希望target_y_top对应视口的顶部
                    # 视口顶部对应的内容y坐标应该是 viewport_height
                    scroll_ratio = (content_height - target_y_top) / (content_height - viewport_height)
                    table_scroll.scroll_y = max(0.0, min(1.0, scroll_ratio))
                else:
                    table_scroll.scroll_y = 1.0
            else:
                # 内容高度小于视口高度，不需要滚动
                table_scroll.scroll_y = 1.0

            logger.info("ScrollView已调整滚动位置")
            logger.info(f"ScrollView内容高度: {content_height:.1f}px")
            logger.info(f"ScrollView视口高度: {viewport_height:.1f}px")
            logger.info(f"滚动位置: {table_scroll.scroll_y:.3f}")

            # 检查表头和第一行数据的位置
            logger.info(f"表头位置: y={header_layout.y:.1f}, height={header_layout.height:.1f}")
            if data_container.children:
                first_row = data_container.children[-1]  # Kivy中最后添加的是第一个显示的
                logger.info(f"第一行位置: y={first_row.y:.1f}, height={first_row.height:.1f}")

                # 计算实际的视口范围（相对于内容坐标系）
                # scroll_y = 0 时显示内容底部，scroll_y = 1 时显示内容顶部
                content_offset = (1.0 - table_scroll.scroll_y) * (content_height - viewport_height)
                viewport_bottom = content_offset
                viewport_top = content_offset + viewport_height
                logger.info(f"ScrollView视口范围（内容坐标系）: {viewport_bottom:.1f} - {viewport_top:.1f}")
                logger.info(f"第一行是否在视口内: {first_row.y >= viewport_bottom and first_row.y + first_row.height <= viewport_top}")

        # 延迟执行滚动，确保UI完全加载后再滚动
        from kivy.clock import Clock
        Clock.schedule_once(scroll_to_show_data, 0.5)

        # 创建一个容器来确保ScrollView与卡片对齐
        scroll_container = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=scroll_height  # 使用动态计算的高度
        )

        # 添加ScrollView到容器中
        scroll_container.add_widget(table_scroll)

        # 将容器添加到结果内容
        self.results_content.add_widget(scroll_container)

        # 更新结果内容的总高度和宽度（根据实际内容动态调整）
        self.results_content.height = responsive_size(40) + scroll_height  # 标题 + 动态表格高度
        self.results_content.width = card_content_width  # 设置宽度与卡片内容宽度一致

    def _update_header_bg(self, instance, value):
        """更新表头背景"""
        if hasattr(self, 'header_bg_rect'):
            self.header_bg_rect.pos = instance.pos
            self.header_bg_rect.size = instance.size

    def _update_row_bg(self, instance, value):
        """更新行背景"""
        if hasattr(self, 'row_bg_rect'):
            self.row_bg_rect.pos = instance.pos
            self.row_bg_rect.size = instance.size

    def _update_cell_bg(self, instance, value):
        """更新单元格背景"""
        if hasattr(instance, 'canvas') and instance.canvas.before:
            instance.canvas.before.clear()
            with instance.canvas.before:
                from kivy.graphics import Color, Rectangle
                # 根据行索引确定背景色
                bg_color = (0.98, 0.98, 0.98, 1) if hasattr(instance, '_row_index') and instance._row_index % 2 == 1 else (1, 1, 1, 1)
                Color(*bg_color)
                Rectangle(pos=instance.pos, size=instance.size)

    def _update_cell_border(self, instance, value):
        """更新单元格边框"""
        if hasattr(instance, 'canvas') and instance.canvas.after:
            instance.canvas.after.clear()
            with instance.canvas.after:
                from kivy.graphics import Color, Rectangle
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=(instance.right - 1, instance.y), size=(1, instance.height))

    def _update_separator(self, instance, value):
        """更新分隔线"""
        if hasattr(instance, 'canvas') and instance.canvas.before:
            instance.canvas.before.clear()
            with instance.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=instance.pos, size=instance.size)

    def go_back(self, instance):
        """返回主界面"""
        self.app.show_main_screen()
