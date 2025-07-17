#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理模块
处理用户会话的保存、加载、验证和自动管理
"""

import os
import json
import pickle
import time
import threading
import logging
from typing import Dict, Optional, Any

from .config import get_config

logger = logging.getLogger(__name__)

# 全局会话对象
session = None

def get_session():
    """获取全局会话对象"""
    global session
    if session is None:
        import requests
        session = requests.Session()
    return session

def set_session(new_session):
    """设置全局会话对象"""
    global session
    session = new_session

class SessionManager:
    """会话管理类，处理会话的保存、加载和验证"""

    _instance = None
    _initialized = False

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化会话管理器"""
        if SessionManager._initialized:
            return

        self.sessions_dir = get_config("SESSION_DIR")
        self.accounts_file = get_config("ACCOUNTS_FILE")
        self.accounts = self._load_accounts()
        self.current_account = None

        # 确保目录存在
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.accounts_file), exist_ok=True)

        SessionManager._initialized = True
    
    def _load_accounts(self) -> Dict[str, Any]:
        """加载保存的账号信息"""
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载账号信息失败: {str(e)}")
        return {}
    
    def _save_accounts(self):
        """保存账号信息到文件"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存账号信息失败: {str(e)}")
    
    def save_session(self, student_id: str) -> bool:
        """保存当前会话"""
        if not student_id:
            logger.error("保存会话失败: 学号为空")
            return False
            
        session_file = os.path.join(self.sessions_dir, f"{student_id}.session")
        try:
            current_session = get_session()
            with open(session_file, 'wb') as f:
                pickle.dump(current_session, f)
            logger.info(f"会话已保存: {student_id}")
            
            # 更新账号列表
            if student_id not in self.accounts:
                self.accounts[student_id] = {"last_login": time.strftime("%Y-%m-%d %H:%M:%S")}
            else:
                self.accounts[student_id]["last_login"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            self._save_accounts()
            self.current_account = student_id
            return True
        except Exception as e:
            logger.error(f"保存会话失败: {str(e)}")
            return False
    
    def load_session(self, student_id: str) -> bool:
        """加载指定学号的会话"""
        session_file = os.path.join(self.sessions_dir, f"{student_id}.session")
        if not os.path.exists(session_file):
            logger.warning(f"会话文件不存在: {student_id}")
            return False
            
        try:
            with open(session_file, 'rb') as f:
                loaded_session = pickle.load(f)
            
            # 替换全局会话
            set_session(loaded_session)
            self.current_account = student_id
            logger.info(f"已加载会话: {student_id}")
            return True
        except Exception as e:
            logger.error(f"加载会话失败: {str(e)}")
            return False
    
    def verify_session(self, student_id: Optional[str] = None) -> bool:
        """验证会话是否有效"""
        if student_id is None:
            student_id = self.current_account
            
        if not student_id:
            return False
            
        # 尝试访问需要登录的页面
        try:
            # 延迟导入避免循环导入
            from .api import make_request, extract_student_name

            resp = make_request(get_config("SCORES_URL"), timeout=10)
            if resp and resp.status_code == 200 and "login" not in resp.url:
                # 提取学生姓名以进一步验证
                student_name = extract_student_name(resp.text)
                if student_name:
                    logger.info(f"会话有效，当前用户: {student_name}")
                    return True
            logger.warning("会话已过期或无效")
            return False
        except Exception as e:
            logger.error(f"验证会话时出错: {str(e)}")
            return False

    def is_session_valid(self, student_id: Optional[str] = None) -> bool:
        """检查会话是否有效（verify_session的别名）"""
        return self.verify_session(student_id)

    def list_accounts(self) -> Dict[str, Any]:
        """获取所有保存的账号"""
        return self.accounts.copy()
    
    def get_current_account(self) -> Optional[str]:
        """获取当前登录的账号"""
        return self.current_account
    
    def delete_account(self, student_id: str) -> bool:
        """删除指定账号的会话和信息"""
        try:
            # 删除会话文件
            session_file = os.path.join(self.sessions_dir, f"{student_id}.session")
            if os.path.exists(session_file):
                os.remove(session_file)
            
            # 从账号列表中移除
            if student_id in self.accounts:
                del self.accounts[student_id]
                self._save_accounts()
            
            # 如果删除的是当前账号，清空当前账号
            if self.current_account == student_id:
                self.current_account = None
            
            logger.info(f"已删除账号: {student_id}")
            return True
        except Exception as e:
            logger.error(f"删除账号失败: {str(e)}")
            return False
    
    def cleanup(self):
        """清理资源"""
        # 保存账号信息
        self._save_accounts()
        logger.info("会话管理器已清理")

class AutoSessionManager:
    """自动会话管理器，基于token提供自动保持登录状态的功能"""

    def __init__(self, session_manager: SessionManager, login_manager_class=None):
        """初始化自动会话管理器"""
        self.session_manager = session_manager
        self.login_manager_class = login_manager_class
        self.credentials_file = get_config("CREDENTIALS_FILE")
        self.check_interval = get_config("AUTO_LOGIN_CHECK_INTERVAL")
        self.expire_threshold = get_config("SESSION_EXPIRE_THRESHOLD")

        # 自动登录状态
        self.auto_login_enabled = False
        self.current_student_id = None
        self.check_timer = None
        self.last_check_time = 0
        self.login_in_progress = False

        # Token和会话信息
        self.session_tokens = {}  # 存储每个账号的token信息

        # 加载保存的token信息
        self.session_tokens = self._load_session_tokens()

        # 确保目录存在
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
    
    def _load_session_tokens(self) -> Dict[str, Any]:
        """加载保存的会话token信息"""
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载会话token失败: {str(e)}")
        return {}
    
    def _save_session_tokens(self):
        """保存会话token信息"""
        try:
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_tokens, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存会话token失败: {str(e)}")
    
    def save_session_info(self, student_id: str) -> bool:
        """保存会话信息和token"""
        try:
            current_session = get_session()
            if not current_session:
                return False
            
            # 提取会话中的重要信息
            session_info = {
                'cookies': dict(current_session.cookies),
                'headers': dict(current_session.headers),
                'last_saved': time.time(),
                'session_valid': True,
                'last_verified': time.time()
            }
            
            self.session_tokens[student_id] = session_info
            self._save_session_tokens()
            logger.info(f"已保存会话token信息: {student_id}")
            return True
        except Exception as e:
            logger.error(f"保存会话token信息失败: {str(e)}")
            return False
    
    def restore_session_from_tokens(self, student_id: str) -> bool:
        """从保存的token恢复会话"""
        if student_id not in self.session_tokens:
            logger.warning(f"没有找到账号的token信息: {student_id}")
            return False
        
        try:
            session_info = self.session_tokens[student_id]
            current_session = get_session()
            
            # 恢复cookies和headers
            current_session.cookies.update(session_info.get('cookies', {}))
            current_session.headers.update(session_info.get('headers', {}))
            
            logger.info(f"已从token恢复会话: {student_id}")
            return True
        except Exception as e:
            logger.error(f"从token恢复会话失败: {str(e)}")
            return False

    def enable_auto_login(self, student_id: str) -> bool:
        """启用基于token的自动登录"""
        # 检查当前是否已登录该账号
        current_account = self.session_manager.get_current_account()
        if current_account != student_id:
            logger.error(f"当前登录账号 {current_account} 与目标账号 {student_id} 不匹配")
            return False

        # 验证当前会话是否有效
        if not self.session_manager.verify_session(student_id):
            logger.error(f"当前会话无效，无法启用自动登录: {student_id}")
            return False

        # 保存当前会话信息
        if not self.save_session_info(student_id):
            logger.error("保存会话信息失败，无法启用自动登录")
            return False

        self.auto_login_enabled = True
        self.current_student_id = student_id
        self.last_check_time = time.time()

        # 启动定时检查
        self._start_check_timer()

        logger.info(f"已启用基于token的自动登录: {student_id}")
        return True

    def disable_auto_login(self):
        """禁用自动登录"""
        self.auto_login_enabled = False
        self.current_student_id = None

        if self.check_timer:
            self.check_timer.cancel()
            self.check_timer = None

        logger.info("已禁用自动登录")

    def _start_check_timer(self):
        """启动定时检查"""
        if self.check_timer:
            self.check_timer.cancel()

        self.check_timer = threading.Timer(self.check_interval, self._check_session_status)
        self.check_timer.daemon = True
        self.check_timer.start()

    def _check_session_status(self):
        """检查会话状态"""
        if not self.auto_login_enabled or not self.current_student_id:
            return

        try:
            # 避免重复检查
            if self.login_in_progress:
                logger.debug("登录正在进行中，跳过此次检查")
                self._start_check_timer()  # 重新启动定时器
                return

            # 检查会话是否有效
            if not self.session_manager.verify_session(self.current_student_id):
                logger.warning(f"检测到会话过期，准备自动重新登录: {self.current_student_id}")
                self._auto_relogin()
            else:
                logger.debug(f"会话状态正常: {self.current_student_id}")

            # 更新最后检查时间
            self.last_check_time = time.time()

        except Exception as e:
            logger.error(f"检查会话状态时出错: {str(e)}")

        # 重新启动定时器
        if self.auto_login_enabled:
            self._start_check_timer()

    def _auto_relogin(self) -> bool:
        """基于token的自动重新登录"""
        if not self.current_student_id or self.login_in_progress:
            return False

        self.login_in_progress = True
        success = False

        try:
            logger.info(f"开始基于token的自动重新登录: {self.current_student_id}")

            # 尝试恢复会话token
            if self.restore_session_from_tokens(self.current_student_id):
                # 验证恢复的会话是否有效
                if self.session_manager.verify_session(self.current_student_id):
                    logger.info(f"基于token的自动登录成功: {self.current_student_id}")
                    # 更新会话验证时间
                    if self.current_student_id in self.session_tokens:
                        self.session_tokens[self.current_student_id]['last_verified'] = time.time()
                        self._save_session_tokens()
                    success = True
                else:
                    logger.warning(f"恢复的token会话无效: {self.current_student_id}")
                    # 标记token为无效
                    if self.current_student_id in self.session_tokens:
                        self.session_tokens[self.current_student_id]['session_valid'] = False
                        self._save_session_tokens()
            else:
                logger.warning(f"无法恢复会话token: {self.current_student_id}")

        except Exception as e:
            logger.error(f"自动重新登录时出错: {str(e)}")
        finally:
            self.login_in_progress = False

        return success

    def cleanup(self):
        """清理资源"""
        self.disable_auto_login()
        self._save_session_tokens()
        logger.info("自动会话管理器已清理")


# 全局SessionManager实例获取函数
def get_session_manager() -> SessionManager:
    """获取SessionManager单例实例"""
    return SessionManager()
