#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI屏幕模块
包含应用的各个界面屏幕
"""

from .main_screen import MainScreen
from .login_screen import LoginScreen
from .query_screen import QueryScoresScreen
from .account_screen import SwitchAccountScreen
from .network_screen import NetworkScreen
from .config_screen import ConfigScreen

__all__ = ['MainScreen', 'LoginScreen', 'QueryScoresScreen', 'SwitchAccountScreen', 'NetworkScreen', 'ConfigScreen']
