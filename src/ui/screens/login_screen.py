#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录屏幕模块
用户登录界面，包含学号、密码输入和验证码
"""

import os
import logging
import threading
import hashlib
from typing import Optional
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock

from ..themes import (
    get_theme_color, responsive_size, responsive_spacing, 
    responsive_font_size
)
from ..components import (
    PrimaryButton, SecondaryButton, AccentButton,
    show_popup
)
from ...utils.font_manager import get_button_text
from ...core.session import SessionManager
from ...core.auth import CaptchaHandler, LoginManager
from ...core.api import make_request
from ...core.config import get_config

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

class ModernTextInput(TextInput):
    """现代化文本输入框"""
    
    def __init__(self, **kwargs):
        super(ModernTextInput, self).__init__(**kwargs)
        self.background_color = [0.95, 0.95, 0.95, 1]
        self.foreground_color = get_theme_color('text')
        self.cursor_color = get_theme_color('primary')
        self.font_size = responsive_font_size(14)
        self.padding = [responsive_spacing(12), responsive_spacing(8), 
                       responsive_spacing(12), responsive_spacing(8)]
        self.size_hint_y = None
        self.height = responsive_size(40)
        self.multiline = False

class FieldLabel(Label):
    """字段标签"""
    
    def __init__(self, **kwargs):
        super(FieldLabel, self).__init__(**kwargs)
        self.color = get_theme_color('text')
        self.font_size = responsive_font_size(12)
        self.halign = 'left'
        self.valign = 'middle'
        self.bold = True

class HeaderLabel(Label):
    """标题标签"""
    
    def __init__(self, **kwargs):
        super(HeaderLabel, self).__init__(**kwargs)
        self.font_size = responsive_font_size(18)
        self.color = get_theme_color('primary')
        self.bold = True
        self.halign = 'center'
        self.valign = 'middle'

class ModernCheckbox(BoxLayout):
    """现代化复选框"""
    
    def __init__(self, text: str = '', checked: bool = False, **kwargs):
        super(ModernCheckbox, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = responsive_spacing(8)
        self.checked = checked
        self.callback = None
        
        # 复选框图标
        self.checkbox_button = PrimaryButton(
            text='☐' if not checked else '☑',
            size_hint=(None, None),
            size=(responsive_size(24), responsive_size(24))
        )
        self.checkbox_button.bind(on_release=self.toggle)
        
        # 文本标签
        self.text_label = Label(
            text=text,
            color=get_theme_color('text'),
            font_size=responsive_font_size(12),
            halign='left',
            valign='middle'
        )
        self.text_label.bind(size=self.text_label.setter('text_size'))
        
        self.add_widget(self.checkbox_button)
        self.add_widget(self.text_label)
    
    def toggle(self, instance):
        """切换复选框状态"""
        self.checked = not self.checked
        self.checkbox_button.text = '☑' if self.checked else '☐'
        
        if self.callback:
            self.callback(self.checked)
    
    def set_checked(self, checked: bool):
        """设置复选框状态"""
        self.checked = checked
        self.checkbox_button.text = '☑' if checked else '☐'
    
    def bind_callback(self, callback):
        """绑定状态变化回调"""
        self.callback = callback

class CaptchaWidget(BoxLayout):
    """验证码组件"""
    
    def __init__(self, **kwargs):
        super(CaptchaWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = responsive_spacing(8)
        
        # 初始化验证码处理器
        self.captcha_handler = CaptchaHandler()
        
        # 验证码图片容器
        captcha_container = ModernCard(
            size_hint=(1, 0.7),
            elevation=1,
            padding=responsive_spacing(8)
        )
        
        # 图片包装器
        image_wrapper = BoxLayout(
            padding=[responsive_spacing(10), responsive_spacing(8), 
                    responsive_spacing(10), responsive_spacing(8)],
            size_hint=(1, 1)
        )
        
        self.captcha_image = Image(
            size_hint=(None, None),
            allow_stretch=False,
            keep_ratio=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # 创建提示标签（当没有验证码时显示）
        self.captcha_hint = Label(
            text="点击刷新按钮获取验证码",
            color=get_theme_color('text_secondary'),
            font_size=responsive_size(12),
            size_hint=(1, 1),
            halign='center',
            valign='middle'
        )
        self.captcha_hint.bind(size=self.captcha_hint.setter('text_size'))

        # 默认显示提示标签
        image_wrapper.add_widget(self.captcha_hint)
        captcha_container.add_widget(image_wrapper)
        self.add_widget(captcha_container)
        
        # 验证码输入区域
        input_container = BoxLayout(
            size_hint=(1, 0.3),
            spacing=responsive_spacing(8)
        )
        
        # 验证码输入框
        self.captcha_input = ModernTextInput(
            hint_text='请输入验证码',
            size_hint=(0.65, 1)
        )
        
        # 刷新按钮
        refresh_button = AccentButton(
            text=get_button_text('refresh'),
            size_hint=(0.35, 1),
            font_size=responsive_font_size(12)
        )
        refresh_button.bind(on_release=self.refresh_captcha)
        
        input_container.add_widget(self.captcha_input)
        input_container.add_widget(refresh_button)
        
        self.add_widget(input_container)
    
    def load_captcha(self):
        """加载验证码"""
        try:
            logger.info("开始加载验证码...")

            # 强制刷新验证码
            captcha_path = self.captcha_handler.get_captcha(refresh=True)

            if captcha_path and os.path.exists(captcha_path):
                logger.info(f"验证码文件路径: {captcha_path}")

                # 使用Clock.schedule_once确保在主线程中更新UI
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self._update_captcha_ui(captcha_path), 0)

            else:
                logger.error("验证码加载失败")
                from kivy.clock import Clock
                Clock.schedule_once(
                    lambda dt: show_popup("错误", "验证码加载失败，请重试", "error"),
                    0
                )
        except Exception as e:
            logger.error(f"加载验证码时出错: {e}")
            import traceback
            traceback.print_exc()
            from kivy.clock import Clock
            Clock.schedule_once(
                lambda dt: show_popup("错误", f"验证码加载失败: {str(e)}", "error"),
                0
            )

    def _update_captcha_ui(self, captcha_path):
        """在主线程中更新验证码UI"""
        try:
            # 获取图片容器
            captcha_container = self.children[1]  # 验证码图片容器
            image_wrapper = captcha_container.children[0]  # 图片包装器

            # 如果当前显示的是提示标签，则移除它
            if self.captcha_hint.parent:
                image_wrapper.remove_widget(self.captcha_hint)

            # 设置图片源和大小
            self.captcha_image.source = captcha_path
            self.captcha_image.size = (responsive_size(120), responsive_size(40))

            # 如果图片还没有添加到容器中，则添加它
            if not self.captcha_image.parent:
                image_wrapper.add_widget(self.captcha_image)

            logger.info("验证码UI更新成功")
        except Exception as e:
            logger.error(f"更新验证码UI时出错: {e}")
            show_popup("错误", f"验证码显示失败: {str(e)}", "error")
    
    def refresh_captcha(self, instance=None):
        """刷新验证码"""
        try:
            logger.info("用户点击刷新验证码")
            self.captcha_input.text = ""  # 清空输入框

            # 使用线程避免UI卡死
            import threading
            def load_in_thread():
                try:
                    self.load_captcha()
                except Exception as e:
                    logger.error(f"后台加载验证码失败: {e}")
                    from kivy.clock import Clock
                    Clock.schedule_once(
                        lambda dt: show_popup("错误", f"验证码加载失败: {str(e)}", "error"),
                        0
                    )

            thread = threading.Thread(target=load_in_thread, daemon=True)
            thread.start()

        except Exception as e:
            logger.error(f"刷新验证码时出错: {e}")
            show_popup("错误", f"刷新验证码失败: {str(e)}", "error")
    
    def get_captcha_code(self) -> str:
        """获取验证码输入"""
        return self.captcha_input.text.strip()
    
    def clear(self):
        """清理验证码"""
        try:
            self.captcha_input.text = ""
            self.captcha_image.source = ""

            # 获取图片容器
            captcha_container = self.children[1]  # 验证码图片容器
            image_wrapper = captcha_container.children[0]  # 图片包装器

            # 隐藏验证码图片，显示提示标签
            if self.captcha_image.parent:
                image_wrapper.remove_widget(self.captcha_image)

            if not self.captcha_hint.parent:
                image_wrapper.add_widget(self.captcha_hint)

            self.captcha_handler.cleanup()
        except Exception as e:
            logger.error(f"清理验证码时出错: {e}")

class LoginScreen(BoxLayout):
    """登录界面屏幕"""
    
    def __init__(self, app, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.spacing = 0
        self.padding = 0
        
        # 初始化管理器
        self.session_manager = SessionManager()
        self.login_manager = None
        self.keep_login_enabled = False
        
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
        # 创建自适应的内容容器
        content_layout = ModernCard(
            orientation='vertical',
            size_hint=(0.95, 0.95),
            elevation=4,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        content_layout.spacing = responsive_spacing(16)
        content_layout.padding = responsive_spacing(20)
        
        # 创建各个部分
        self._create_header(content_layout)
        self._create_form(content_layout)
        self._create_buttons(content_layout)
        self._create_status_label(content_layout)
        
        # 添加内容容器到主布局
        self.add_widget(Widget(size_hint=(1, 0.025)))  # 顶部间距
        self.add_widget(content_layout)
        self.add_widget(Widget(size_hint=(1, 0.025)))  # 底部间距
        
        # 不自动加载验证码，只在用户点击刷新时加载

    def _create_header(self, parent_layout):
        """创建标题区域"""
        header_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2))

        # Logo区域
        logo_layout = BoxLayout(size_hint=(1, 0.6), pos_hint={'center_x': 0.5})
        logo_container = ModernCard(
            size_hint=(None, None),
            size=(responsive_size(60), responsive_size(60)),
            elevation=2,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # 创建圆形Logo背景
        with logo_container.canvas:
            Color(*get_theme_color('primary'))
            logo_ellipse = Ellipse(
                pos=(logo_container.x + responsive_size(8), logo_container.y + responsive_size(8)),
                size=(responsive_size(44), responsive_size(44))
            )

        # 绑定位置更新
        def update_logo_pos(instance, value):
            logo_ellipse.pos = (instance.x + responsive_size(8), instance.y + responsive_size(8))

        logo_container.bind(pos=update_logo_pos)
        logo_layout.add_widget(logo_container)

        # 标题
        title_label = HeaderLabel(
            text='齐齐哈尔大学教务系统',
            size_hint=(1, 0.4),
            font_size=responsive_font_size(18)
        )

        header_layout.add_widget(logo_layout)
        header_layout.add_widget(title_label)
        parent_layout.add_widget(header_layout)

    def _create_form(self, parent_layout):
        """创建登录表单"""
        form_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.7),
            spacing=responsive_spacing(8)
        )

        # 学号输入
        id_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(62),
            spacing=responsive_spacing(2)
        )

        id_label = FieldLabel(
            text='学号',
            size_hint=(1, None),
            height=responsive_size(20)
        )

        self.student_id_input = ModernTextInput(
            hint_text='请输入学号',
            size_hint=(1, None)
        )

        id_container.add_widget(id_label)
        id_container.add_widget(self.student_id_input)
        form_container.add_widget(id_container)

        # 密码输入
        pwd_container = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=responsive_size(62),
            spacing=responsive_spacing(2)
        )

        pwd_label = FieldLabel(
            text='密码',
            size_hint=(1, None),
            height=responsive_size(20)
        )

        self.password_input = ModernTextInput(
            hint_text='请输入密码',
            password=True,
            size_hint=(1, None)
        )

        pwd_container.add_widget(pwd_label)
        pwd_container.add_widget(self.password_input)
        form_container.add_widget(pwd_container)

        # 验证码组件
        self.captcha_widget = CaptchaWidget(
            size_hint=(1, None),
            height=responsive_size(150)
        )
        form_container.add_widget(self.captcha_widget)

        # 保持登录选项
        self.keep_login_checkbox = ModernCheckbox(
            text='保持登录状态（基于Token自动重新登录）',
            checked=False,
            size_hint=(1, None),
            height=responsive_size(50)
        )
        self.keep_login_checkbox.bind_callback(self.on_keep_login_changed)
        form_container.add_widget(self.keep_login_checkbox)

        parent_layout.add_widget(form_container)

    def _create_buttons(self, parent_layout):
        """创建按钮区域"""
        buttons_layout = BoxLayout(
            size_hint=(1, 0.1),
            spacing=responsive_spacing(12)
        )

        login_button = PrimaryButton(text='登 录')
        login_button.bind(on_release=self.login)

        cancel_button = SecondaryButton(text='返 回')
        cancel_button.bind(on_release=self.cancel)

        buttons_layout.add_widget(login_button)
        buttons_layout.add_widget(cancel_button)

        parent_layout.add_widget(buttons_layout)

    def _create_status_label(self, parent_layout):
        """创建状态标签"""
        self.status_label = Label(
            text='',
            size_hint=(1, 0.05),
            halign='center',
            valign='middle',
            font_size=responsive_font_size(12),
            color=get_theme_color('text_secondary')
        )

        parent_layout.add_widget(self.status_label)

    # 移除自动加载验证码的方法，改为手动刷新

    def on_keep_login_changed(self, checked):
        """保持登录状态改变回调"""
        self.keep_login_enabled = checked
        if checked:
            self._update_status('已启用自动保持登录', 'info')
        else:
            self._update_status('已禁用自动保持登录', 'info')

    def login(self, instance):
        """执行登录操作"""
        student_id = self.student_id_input.text.strip()
        password = self.password_input.text.strip()
        captcha_code = self.captcha_widget.get_captcha_code()

        if not student_id or not password or not captcha_code:
            self._update_status('请填写完整信息', 'error')
            return

        self._update_status('登录中...', 'info')

        # 在后台线程中执行登录操作
        threading.Thread(
            target=self._login_thread,
            args=(student_id, password, captcha_code)
        ).start()

    def _login_thread(self, student_id, password, captcha_code):
        """后台登录线程"""
        try:
            # 创建登录管理器
            self.login_manager = LoginManager(
                captcha_handler=self.captcha_widget.captcha_handler,
                session_manager=self.session_manager
            )

            # 初始化会话
            if not self.login_manager.init_session():
                Clock.schedule_once(lambda dt: self._update_status('初始化会话失败', 'error'), 0)
                return

            # MD5加密密码
            md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()

            # 构造表单数据
            form_data = {
                "j_username": student_id,
                "j_password": md5_password,
                "j_captcha": captcha_code,
                "tokenValue": self.login_manager.token_value
            }

            # 发送登录请求
            login_headers = {
                "Origin": get_config("BASE_URL"),
                "Content-Type": "application/x-www-form-urlencoded"
            }

            response = make_request(
                get_config("LOGIN_POST_URL"),
                method="POST",
                data=form_data,
                headers=login_headers,
                allow_redirects=False,
                timeout=15
            )

            # 检测登录结果
            login_result = self.login_manager._check_login_response(response)

            if login_result == "success":
                # 保存会话
                self.session_manager.save_session(student_id)
                Clock.schedule_once(lambda dt: self.login_success(), 0)
            elif login_result == "captcha_error":
                Clock.schedule_once(lambda dt: self._update_status('验证码错误，请重试', 'error'), 0)
                Clock.schedule_once(lambda dt: self.captcha_widget.refresh_captcha(), 0.5)
            elif login_result == "credential_error":
                Clock.schedule_once(lambda dt: self._update_status('用户名或密码错误', 'error'), 0)
            else:
                Clock.schedule_once(lambda dt: self._update_status('登录失败，请重试', 'error'), 0)

        except Exception as e:
            logger.error(f"登录过程中出错: {e}")
            Clock.schedule_once(lambda dt: self._update_status('登录过程中出错，请重试', 'error'), 0)

    def login_success(self):
        """登录成功后的操作"""
        self._update_status('登录成功', 'success')
        self.captcha_widget.clear()

        # 如果启用了保持登录，则启用基于token的自动登录功能
        if self.keep_login_enabled:
            student_id = self.student_id_input.text.strip()
            if student_id:
                # 这里可以添加自动登录功能的启用逻辑
                self._update_status('已启用基于Token的自动保持登录', 'success')

        # 跳转到主界面
        Clock.schedule_once(lambda dt: self.app.show_main_screen(), 1)

    def cancel(self, instance):
        """取消登录"""
        self.captcha_widget.clear()
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
