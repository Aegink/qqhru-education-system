#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心功能模块
包含配置管理、会话管理、认证和API请求等核心功能
"""

from .config import CONFIG, get_config, update_config
from .session import SessionManager, AutoSessionManager
from .auth import CaptchaHandler, LoginManager
from .api import make_request, query_scores, extract_student_name

__all__ = [
    'CONFIG', 'get_config', 'update_config',
    'SessionManager', 'AutoSessionManager',
    'CaptchaHandler', 'LoginManager',
    'make_request', 'query_scores', 'extract_student_name'
]
