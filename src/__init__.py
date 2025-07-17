#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
齐齐哈尔大学教务系统查询工具
主包初始化文件
"""

__version__ = "2.0.0"
__author__ = "Education System Team"
__description__ = "齐齐哈尔大学教务系统查询工具 - 重构版本"

# 导出主要组件
from .app import EducationSystemApp

__all__ = ['EducationSystemApp']
