#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证模块
处理验证码获取、登录认证等功能
"""

import os
import time
import hashlib
import logging
from typing import Optional, Tuple
from PIL import Image
from bs4 import BeautifulSoup

from .config import get_config
from .session import get_session

logger = logging.getLogger(__name__)

class TempFileManager:
    """临时文件管理器"""
    
    def __init__(self):
        self.debug_mode = False
        self.temp_files = []
    
    def set_debug_mode(self, debug_mode: bool):
        """设置调试模式"""
        self.debug_mode = debug_mode
    
    def save_content(self, content: str, filename: str, encoding: str = 'utf-8') -> str:
        """保存内容到临时文件"""
        if not self.debug_mode:
            return ""
        
        temp_dir = get_config("TEMP_DIR")
        os.makedirs(temp_dir, exist_ok=True)
        
        filepath = os.path.join(temp_dir, filename)
        try:
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(content)
            self.temp_files.append(filepath)
            logger.debug(f"已保存临时文件: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存临时文件失败: {e}")
            return ""
    
    def clean_all(self):
        """清理所有临时文件"""
        if self.debug_mode:
            return
        
        for filepath in self.temp_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.debug(f"已删除临时文件: {filepath}")
            except Exception as e:
                logger.debug(f"删除临时文件失败: {filepath}, 错误: {e}")
        
        self.temp_files.clear()

class CaptchaHandler:
    """验证码处理类，管理验证码的获取、显示和清理"""
    
    def __init__(self, base_url: Optional[str] = None):
        """初始化验证码处理器"""
        self.base_url = base_url or get_config("BASE_URL")
        self.current_captcha_path = None
        # 清理所有历史验证码图片
        self._clean_old_captchas()
    
    def _clean_old_captchas(self):
        """清理所有历史验证码图片"""
        try:
            temp_dir = get_config("TEMP_DIR")
            if os.path.exists(temp_dir):
                captcha_files = [f for f in os.listdir(temp_dir) 
                               if f.startswith("captcha_") and f.endswith(".jpg")]
                for file in captcha_files:
                    try:
                        os.remove(os.path.join(temp_dir, file))
                        logger.debug(f"已删除历史验证码: {file}")
                    except Exception as e:
                        logger.debug(f"删除验证码失败: {file}, 错误: {str(e)}")
        except Exception as e:
            logger.debug(f"清理验证码目录时出错: {str(e)}")
    
    def get_captcha(self, refresh: bool = False, max_retries: int = 10, 
                   delay: float = 0.5, student_id: Optional[str] = None) -> Optional[str]:
        """获取验证码，可选择是否刷新
        
        Args:
            refresh: 是否强制刷新验证码
            max_retries: 最大重试次数
            delay: 重试延迟时间(秒)
            student_id: 学号，用于在文件名中标识
            
        Returns:
            验证码图片路径，失败返回None
        """
        # 如果请求刷新或当前没有验证码，则删除旧的验证码
        if refresh or not self.current_captcha_path:
            self.delete_current()
        
        # 如果已有验证码且不需要刷新，则直接返回
        if not refresh and self.current_captcha_path and os.path.exists(self.current_captcha_path):
            return self.current_captcha_path
            
        # 带重试机制获取新验证码
        for attempt in range(max_retries):
            try:
                # 使用时间戳确保每次请求都是新的
                timestamp = int(time.time() * 1000)
                captcha_url = f"{self.base_url}/img/captcha.jpg?{timestamp}"
                
                # 延迟导入避免循环导入
                from .api import make_request

                # 获取验证码图片
                resp = make_request(
                    captcha_url,
                    headers={"Referer": f"{self.base_url}/login"}
                )
                
                # 检查响应是否有效
                if not resp or resp.status_code != 200:
                    logger.warning(f"验证码请求失败，状态码: {resp.status_code if resp else 'None'}")
                    time.sleep(delay * (attempt + 1))
                    continue
                    
                if len(resp.content) < 1024:  # 1024字节作为最小图片大小
                    logger.warning(f"验证码图片过小: {len(resp.content)}字节")
                    time.sleep(delay * (attempt + 1))
                    continue
                
                # 保存验证码图片，文件名中包含学号信息
                file_prefix = f"captcha_{student_id}_" if student_id else "captcha_"
                captcha_path = os.path.join(get_config("TEMP_DIR"), f"{file_prefix}{timestamp}.jpg")
                with open(captcha_path, "wb") as f:
                    f.write(resp.content)
                
                # 尝试打开图片
                try:
                    img = Image.open(captcha_path)
                    img.verify()  # 验证图片完整性
                    
                    # 不自动显示图片，避免UI卡死
                    # self._show_captcha(captcha_path)  # 注释掉自动显示
                    logger.info(f"验证码图片已保存: {captcha_path}")
                    
                    # 更新当前验证码路径
                    self.current_captcha_path = captcha_path
                    return captcha_path
                except Exception as img_error:
                    logger.error(f"验证码图片损坏: {img_error}")
                    if os.path.exists(captcha_path):
                        os.remove(captcha_path)
                    time.sleep(delay)
                    continue
                
            except Exception as e:
                logger.error(f"获取验证码尝试 {attempt+1}/{max_retries} 失败: {str(e)}")
                time.sleep(delay * (attempt + 1))  # 指数退避策略
        
        logger.error("多次尝试后仍无法获取有效验证码")
        return None
    
    def _show_captcha(self, image_path: str) -> bool:
        """更可靠的方式显示验证码图片"""
        try:
            # 先尝试使用PIL显示
            img = Image.open(image_path)
            img.show()
            return True
        except Exception as e:
            logger.warning(f"PIL显示图片失败: {str(e)}，尝试使用系统命令")
            
            try:
                # 根据操作系统选择不同的命令
                if os.name == 'nt':  # Windows
                    os.startfile(image_path)
                elif os.name == 'posix':  # Linux/Mac
                    import subprocess
                    # 尝试使用系统默认图片查看器
                    if os.system('which xdg-open > /dev/null') == 0:
                        subprocess.run(['xdg-open', image_path])
                    elif os.system('which open > /dev/null') == 0:  # MacOS
                        subprocess.run(['open', image_path])
                    else:
                        logger.warning("无法找到合适的图片查看器")
                        return False
                return True
            except Exception as e2:
                logger.error(f"系统命令显示图片失败: {str(e2)}")
                return False
    
    def refresh(self, student_id: Optional[str] = None) -> Optional[str]:
        """刷新验证码"""
        return self.get_captcha(refresh=True, student_id=student_id)
    
    def delete_current(self):
        """删除当前验证码图片"""
        if self.current_captcha_path and os.path.exists(self.current_captcha_path):
            try:
                os.remove(self.current_captcha_path)
                logger.debug(f"已删除验证码图片: {self.current_captcha_path}")
            except Exception as e:
                logger.error(f"删除验证码图片失败: {str(e)}")
            self.current_captcha_path = None
    
    def cleanup(self):
        """清理资源"""
        self.delete_current()
        self._clean_old_captchas()

class LoginManager:
    """登录管理类，处理登录相关操作"""

    def __init__(self, base_url: Optional[str] = None, captcha_handler: Optional[CaptchaHandler] = None,
                 session_manager=None, debug_mode: bool = False):
        """初始化登录管理器"""
        self.base_url = base_url or get_config("BASE_URL")
        self.login_page_url = f"{self.base_url}/login"
        self.login_post_url = f"{self.base_url}/j_spring_security_check"
        self.captcha_handler = captcha_handler or CaptchaHandler(self.base_url)
        self.session_manager = session_manager
        self.token_value = ""
        self.temp_manager = TempFileManager()
        self.temp_manager.set_debug_mode(debug_mode)

    def init_session(self) -> bool:
        """初始化会话，获取必要的cookie和token"""
        logger.info("正在初始化会话...")

        # 延迟导入避免循环导入
        from .api import make_request

        # 访问登录页面
        init_resp = make_request(self.login_page_url, timeout=10)
        if not init_resp or init_resp.status_code != 200:
            logger.error(f"初始化登录页面失败，状态码: {init_resp.status_code if init_resp else 'None'}")
            return False

        # 检查是否有JSESSIONID设置
        current_session = get_session()
        if 'JSESSIONID' in current_session.cookies:
            logger.info(f"已获取JSESSIONID: {current_session.cookies['JSESSIONID']}")
        else:
            logger.warning("警告: 未获取到JSESSIONID cookie")

        # 解析HTML，提取tokenValue
        soup = BeautifulSoup(init_resp.text, 'html.parser')
        token_input = soup.find('input', id='tokenValue')
        if token_input:
            self.token_value = token_input.get('value', '')
            logger.info(f"获取到tokenValue: {self.token_value}")
        else:
            logger.warning("警告: 未找到tokenValue，使用空值")
            self.token_value = ''

        # 只在调试模式下保存登录页面
        if self.temp_manager.debug_mode:
            self.temp_manager.save_content(
                init_resp.text,
                f"login_page_{time.strftime('%Y%m%d_%H%M%S')}.html",
                encoding="utf-8"
            )

        return True

    def login(self, student_id: str, password: str, max_attempts: int = 3,
              save_session: bool = True, captcha_code: Optional[str] = None) -> bool:
        """执行登录流程

        Args:
            student_id: 学号
            password: 密码
            max_attempts: 最大尝试次数
            save_session: 是否保存会话
            captcha_code: 验证码（如果提供则不会重新获取）

        Returns:
            登录是否成功
        """
        # 初始化会话
        if not self.init_session():
            return False

        # 登录尝试
        for attempt in range(max_attempts):
            logger.info(f"\n--- 登录尝试 {attempt+1}/{max_attempts} ---")

            # 获取验证码（如果没有提供）
            if not captcha_code:
                captcha_path = self.captcha_handler.refresh(student_id=student_id)
                if not captcha_path:
                    logger.error("无法获取验证码，终止登录")
                    return False

                # 在GUI模式下，验证码由外部提供
                # 在命令行模式下，需要用户输入
                if not hasattr(self, '_gui_mode') or not self._gui_mode:
                    captcha_code = self._get_captcha_input(student_id)
                    if not captcha_code:
                        return False

            # 对密码进行MD5加密
            md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()

            # 构造表单数据
            form_data = {
                "j_username": student_id,
                "j_password": md5_password,
                "j_captcha": captcha_code,
                "tokenValue": self.token_value
            }

            # 发送登录请求
            logger.info("正在提交登录请求...")
            login_headers = {"Origin": self.base_url, "Content-Type": "application/x-www-form-urlencoded"}

            # 延迟导入避免循环导入
            from .api import make_request

            response = make_request(
                self.login_post_url,
                method="POST",
                data=form_data,
                headers=login_headers,
                allow_redirects=False,
                timeout=15
            )

            # 检测登录结果
            login_result = self._check_login_response(response)
            if login_result == "success":
                logger.info("登录成功！")
                # 删除当前验证码图片
                self.captcha_handler.delete_current()

                # 保存会话
                if save_session and self.session_manager:
                    self.session_manager.save_session(student_id)

                return True
            elif login_result == "captcha_error":
                logger.warning("验证码错误，请重试！")
                captcha_code = None  # 重置验证码，下次循环重新获取
                continue
            elif login_result == "credential_error":
                logger.error("用户名或密码错误！")
                break  # 用户名密码错误，不需要重试
            else:  # login_result == "unknown"
                logger.warning("登录状态未知")
                captcha_code = None  # 重置验证码
                continue

        logger.info("\n登录过程结束")
        # 清理：删除最后一次使用的验证码图片
        self.captcha_handler.delete_current()
        self.temp_manager.clean_all()
        return False

    def _get_captcha_input(self, student_id: str) -> Optional[str]:
        """获取验证码输入（命令行模式）"""
        while True:
            action = input("请选择: 1.输入验证码  2.刷新验证码  3.取消登录\n").strip()

            if action == '1':
                # 用户输入验证码
                captcha_code = input("请输入验证码: ").strip()
                if captcha_code:
                    return captcha_code
                else:
                    logger.warning("验证码不能为空，请重新输入")
            elif action == '2':
                # 刷新验证码，传递学号参数
                captcha_path = self.captcha_handler.refresh(student_id=student_id)
                if not captcha_path:
                    logger.error("刷新验证码失败，请重试")
            elif action == '3':
                logger.info("取消登录")
                self.captcha_handler.delete_current()
                return None
            else:
                logger.warning("无效选项，请重新输入")

    def _check_login_response(self, response) -> str:
        """检查登录响应的状态

        Returns:
            "success": 登录成功
            "captcha_error": 验证码错误
            "credential_error": 用户名或密码错误
            "unknown": 未知错误
        """
        if not response:
            logger.error("登录请求失败")
            return "unknown"

        if response.status_code == 302:
            location = response.headers.get("Location", "")
            if "errorCode=badCaptcha" in location or location.endswith("/login?errorCode=badCaptcha"):
                return "captcha_error"
            elif location.endswith("/login?errorCode=badCredentials"):
                return "credential_error"
            else:
                return "success"
        else:
            # 分析响应内容
            logger.error(f"登录失败，状态码：{response.status_code}")

            # 保存响应内容用于调试
            debug_file = self.temp_manager.save_content(
                response.text,
                f"login_failed_{time.strftime('%Y%m%d_%H%M%S')}.html",
                encoding="utf-8"
            )
            if debug_file:
                logger.debug(f"已保存失败响应到: {debug_file}")

            # 解析HTML查找错误信息
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找JavaScript错误提示
            error_msg = self._extract_error_message(soup)
            if error_msg:
                logger.warning(f"错误信息: {error_msg}")

                # 根据错误信息判断错误类型
                if "验证码" in error_msg or "captcha" in error_msg.lower():
                    return "captcha_error"
                elif "用户名" in error_msg or "密码" in error_msg or "credential" in error_msg.lower():
                    return "credential_error"

            return "unknown"

    def _extract_error_message(self, soup) -> Optional[str]:
        """从HTML中提取错误信息"""
        try:
            # 查找JavaScript中的alert信息
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_content = script.string
                    if 'alert(' in script_content:
                        # 提取alert中的信息
                        import re
                        alert_match = re.search(r'alert\(["\']([^"\']+)["\']', script_content)
                        if alert_match:
                            return alert_match.group(1)

            # 查找错误提示div
            error_divs = soup.find_all('div', class_=['error', 'alert', 'message'])
            for div in error_divs:
                if div.get_text(strip=True):
                    return div.get_text(strip=True)

            return None
        except Exception as e:
            logger.debug(f"提取错误信息失败: {e}")
            return None

    def set_gui_mode(self, gui_mode: bool = True):
        """设置GUI模式"""
        self._gui_mode = gui_mode

    def cleanup(self):
        """清理资源"""
        self.captcha_handler.cleanup()
        self.temp_manager.clean_all()
