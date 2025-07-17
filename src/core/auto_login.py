#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动登录管理模块
处理自动登录功能的启用、禁用和状态检查
"""

import time
import logging
import threading
from typing import Optional, Dict, Any
from kivy.clock import Clock

from .config import get_config, update_config, save_config
from .session import get_session_manager
from .auth import LoginManager
from .api import make_request, extract_student_name

logger = logging.getLogger(__name__)

class AutoLoginManager:
    """自动登录管理器"""
    
    def __init__(self):
        self.session_manager = get_session_manager()
        self.login_manager = LoginManager()
        self._check_thread: Optional[threading.Thread] = None
        self._stop_checking = False
        self._is_checking = False
        
        # 状态回调
        self.on_status_change = None
        self.on_login_success = None
        self.on_login_failed = None
    
    def is_enabled(self) -> bool:
        """检查自动登录是否启用"""
        return get_config("AUTO_LOGIN_ENABLED", False)
    
    def enable_auto_login(self) -> bool:
        """启用自动登录"""
        try:
            # 检查是否有当前账号
            current_account = self.session_manager.get_current_account()
            if not current_account:
                logger.warning("没有当前账号，无法启用自动登录")
                return False
            
            # 检查当前账号是否有有效会话
            if not self.session_manager.is_session_valid():
                logger.warning("当前会话无效，无法启用自动登录")
                return False
            
            # 启用自动登录
            update_config("AUTO_LOGIN_ENABLED", True)
            update_config("LAST_AUTO_LOGIN_TIME", int(time.time()))
            save_config()
            
            # 启动检查线程
            self._start_checking()
            
            logger.info("自动登录已启用")
            if self.on_status_change:
                self.on_status_change("已启用", "success")
            
            return True
            
        except Exception as e:
            logger.error(f"启用自动登录失败: {e}")
            return False
    
    def disable_auto_login(self) -> bool:
        """禁用自动登录"""
        try:
            # 禁用自动登录
            update_config("AUTO_LOGIN_ENABLED", False)
            save_config()
            
            # 停止检查线程
            self._stop_checking_thread()
            
            logger.info("自动登录已禁用")
            if self.on_status_change:
                self.on_status_change("未启用", "info")
            
            return True
            
        except Exception as e:
            logger.error(f"禁用自动登录失败: {e}")
            return False
    
    def toggle_auto_login(self) -> bool:
        """切换自动登录状态"""
        if self.is_enabled():
            return self.disable_auto_login()
        else:
            return self.enable_auto_login()
    
    def check_status(self) -> Dict[str, Any]:
        """检查自动登录状态"""
        try:
            current_account = self.session_manager.get_current_account()
            is_enabled = self.is_enabled()
            is_session_valid = self.session_manager.is_session_valid() if current_account else False
            last_check_time = get_config("LAST_AUTO_LOGIN_TIME", 0)
            
            status = {
                "enabled": is_enabled,
                "current_account": current_account,
                "session_valid": is_session_valid,
                "last_check_time": last_check_time,
                "is_checking": self._is_checking,
                "check_interval": get_config("AUTO_LOGIN_CHECK_INTERVAL", 300)
            }
            
            # 生成状态描述
            if not current_account:
                status["description"] = "未登录"
                status["status_type"] = "warning"
            elif not is_enabled:
                status["description"] = "未启用"
                status["status_type"] = "info"
            elif not is_session_valid:
                status["description"] = "会话无效"
                status["status_type"] = "error"
            elif self._is_checking:
                status["description"] = "监控中"
                status["status_type"] = "success"
            else:
                status["description"] = "已启用"
                status["status_type"] = "success"
            
            return status
            
        except Exception as e:
            logger.error(f"检查自动登录状态失败: {e}")
            return {
                "enabled": False,
                "description": "状态未知",
                "status_type": "error",
                "error": str(e)
            }
    
    def _start_checking(self):
        """启动自动检查线程"""
        if self._check_thread and self._check_thread.is_alive():
            return
        
        self._stop_checking = False
        self._check_thread = threading.Thread(target=self._check_loop, daemon=True)
        self._check_thread.start()
        logger.info("自动登录检查线程已启动")
    
    def _stop_checking_thread(self):
        """停止检查线程"""
        self._stop_checking = True
        if self._check_thread and self._check_thread.is_alive():
            self._check_thread.join(timeout=5)
        self._is_checking = False
        logger.info("自动登录检查线程已停止")
    
    def _check_loop(self):
        """自动检查循环"""
        self._is_checking = True
        
        while not self._stop_checking and self.is_enabled():
            try:
                # 检查会话是否有效
                if not self.session_manager.is_session_valid():
                    logger.info("检测到会话失效，尝试自动重新登录")
                    self._attempt_auto_login()
                
                # 更新最后检查时间
                update_config("LAST_AUTO_LOGIN_TIME", int(time.time()))
                save_config()
                
                # 等待下次检查
                check_interval = get_config("AUTO_LOGIN_CHECK_INTERVAL", 300)
                for _ in range(check_interval):
                    if self._stop_checking:
                        break
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"自动登录检查出错: {e}")
                time.sleep(60)  # 出错时等待1分钟再重试
        
        self._is_checking = False
        logger.info("自动登录检查循环已退出")
    
    def _attempt_auto_login(self):
        """尝试自动登录"""
        try:
            current_account = self.session_manager.get_current_account()
            if not current_account:
                logger.warning("没有当前账号，无法自动登录")
                return False
            
            # 获取保存的凭据
            credentials = self.session_manager.get_saved_credentials(current_account)
            if not credentials:
                logger.warning(f"账号 {current_account} 没有保存的凭据，无法自动登录")
                return False
            
            # 尝试登录
            retry_count = get_config("AUTO_LOGIN_RETRY_COUNT", 3)
            for attempt in range(retry_count):
                try:
                    logger.info(f"自动登录尝试 {attempt + 1}/{retry_count}")
                    
                    # 这里需要实现自动获取验证码和登录的逻辑
                    # 暂时只检查会话状态
                    success = self._try_login_with_credentials(credentials)
                    
                    if success:
                        logger.info("自动登录成功")
                        if self.on_login_success:
                            Clock.schedule_once(lambda dt: self.on_login_success(), 0)
                        return True
                    
                except Exception as e:
                    logger.warning(f"自动登录尝试 {attempt + 1} 失败: {e}")
                
                # 等待后重试
                if attempt < retry_count - 1:
                    time.sleep(5)
            
            logger.error("自动登录失败，已达到最大重试次数")
            if self.on_login_failed:
                Clock.schedule_once(lambda dt: self.on_login_failed(), 0)
            
            return False
            
        except Exception as e:
            logger.error(f"自动登录过程出错: {e}")
            return False
    
    def _try_login_with_credentials(self, credentials: Dict[str, str]) -> bool:
        """使用凭据尝试登录"""
        try:
            # 这里应该实现完整的登录逻辑
            # 包括获取验证码、提交登录表单等
            # 暂时只返回False，表示需要手动登录
            
            # TODO: 实现自动验证码识别和登录
            logger.info("自动登录功能需要验证码识别，暂时返回失败")
            return False
            
        except Exception as e:
            logger.error(f"使用凭据登录失败: {e}")
            return False
    
    def force_check_now(self):
        """立即执行一次状态检查"""
        try:
            if not self.is_enabled():
                logger.info("自动登录未启用，跳过检查")
                return
            
            current_account = self.session_manager.get_current_account()
            if not current_account:
                logger.warning("没有当前账号")
                return
            
            # 检查会话状态
            is_valid = self.session_manager.is_session_valid()
            logger.info(f"当前会话状态: {'有效' if is_valid else '无效'}")
            
            if not is_valid:
                logger.info("会话无效，建议重新登录")
            
            # 更新检查时间
            update_config("LAST_AUTO_LOGIN_TIME", int(time.time()))
            save_config()
            
        except Exception as e:
            logger.error(f"强制检查失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        self._stop_checking_thread()

# 全局自动登录管理器实例
_auto_login_manager = None

def get_auto_login_manager() -> AutoLoginManager:
    """获取自动登录管理器实例"""
    global _auto_login_manager
    if _auto_login_manager is None:
        _auto_login_manager = AutoLoginManager()
    return _auto_login_manager
