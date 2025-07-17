#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助工具模块
包含文件清理、目录管理等辅助功能
"""

import os
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def ensure_directories(directories: Optional[List[str]] = None):
    """确保必要的目录存在
    
    Args:
        directories: 目录列表，如果为None则使用默认目录
    """
    if directories is None:
        from ..core.config import get_config
        directories = [
            get_config("DATA_DIR"),
            get_config("SESSION_DIR"),
            get_config("LOGS_DIR"),
            get_config("TEMP_DIR")
        ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"确保目录存在: {directory}")
        except Exception as e:
            logger.error(f"创建目录失败 {directory}: {e}")
            raise RuntimeError(f"无法创建必要的目录: {directory}")

def clean_history_files():
    """清理历史临时文件"""
    from ..core.config import get_config
    
    logger.info("开始清理临时文件...")
    
    temp_dir = get_config("TEMP_DIR")
    if not os.path.exists(temp_dir):
        logger.debug("临时目录不存在，跳过清理")
        return
    
    # 清理验证码图片
    try:
        captcha_files = [f for f in os.listdir(temp_dir) 
                        if f.startswith("captcha_") and f.endswith(".jpg")]
        for file in captcha_files:
            try:
                os.remove(os.path.join(temp_dir, file))
                logger.debug(f"已删除历史验证码: {file}")
            except Exception as e:
                logger.debug(f"删除文件失败: {file}, 错误: {str(e)}")
    except Exception as e:
        logger.error(f"清理验证码文件时出错: {e}")
    
    # 清理HTML文件
    try:
        html_files = [f for f in os.listdir(temp_dir) 
                     if f.startswith(("login_page_", "scores_page_")) and f.endswith(".html")]
        for file in html_files:
            try:
                os.remove(os.path.join(temp_dir, file))
                logger.debug(f"已删除历史HTML文件: {file}")
            except Exception as e:
                logger.debug(f"删除文件失败: {file}, 错误: {str(e)}")
    except Exception as e:
        logger.error(f"清理HTML文件时出错: {e}")
    
    # 清理JSON文件
    try:
        json_files = [f for f in os.listdir(temp_dir) 
                     if f.startswith("scores_data_") and f.endswith(".json")]
        for file in json_files:
            try:
                os.remove(os.path.join(temp_dir, file))
                logger.debug(f"已删除历史JSON文件: {file}")
            except Exception as e:
                logger.debug(f"删除文件失败: {file}, 错误: {str(e)}")
    except Exception as e:
        logger.error(f"清理JSON文件时出错: {e}")
    
    # 清理其他临时文件
    try:
        temp_files = [f for f in os.listdir(temp_dir) if f.startswith("temp_")]
        for file in temp_files:
            try:
                os.remove(os.path.join(temp_dir, file))
                logger.debug(f"已删除临时文件: {file}")
            except Exception as e:
                logger.debug(f"删除文件失败: {file}, 错误: {str(e)}")
    except Exception as e:
        logger.error(f"清理临时文件时出错: {e}")
            
    logger.info("临时文件清理完成")
    
    # 检查并清理无效的会话文件
    _clean_invalid_sessions()

def _clean_invalid_sessions():
    """清理无效的会话文件"""
    from ..core.config import get_config
    
    accounts_file = get_config("ACCOUNTS_FILE")
    session_dir = get_config("SESSION_DIR")
    
    if not os.path.exists(accounts_file):
        logger.debug("账号文件不存在，跳过会话文件清理")
        return
    
    try:
        with open(accounts_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        # 获取所有会话文件
        if os.path.exists(session_dir):
            session_files = [f for f in os.listdir(session_dir) if f.endswith(".session")]
            for file in session_files:
                # 提取学号
                student_id = file.replace(".session", "")
                # 如果学号不在账号列表中，删除会话文件
                if student_id not in accounts:
                    try:
                        os.remove(os.path.join(session_dir, file))
                        logger.info(f"已删除无效会话文件: {file}")
                    except Exception as e:
                        logger.error(f"删除无效会话文件失败: {file}, 错误: {str(e)}")
    except Exception as e:
        logger.error(f"清理无效会话文件时出错: {str(e)}")

def clean_directory(directory: str, patterns: List[str] = None, max_age_days: int = None):
    """清理指定目录中的文件
    
    Args:
        directory: 要清理的目录
        patterns: 文件名模式列表（支持通配符）
        max_age_days: 文件最大存活天数
    """
    if not os.path.exists(directory):
        logger.debug(f"目录不存在，跳过清理: {directory}")
        return
    
    import glob
    import time
    
    try:
        files_to_clean = []
        
        if patterns:
            # 根据模式匹配文件
            for pattern in patterns:
                pattern_path = os.path.join(directory, pattern)
                files_to_clean.extend(glob.glob(pattern_path))
        else:
            # 清理所有文件
            files_to_clean = [os.path.join(directory, f) 
                            for f in os.listdir(directory) 
                            if os.path.isfile(os.path.join(directory, f))]
        
        current_time = time.time()
        cleaned_count = 0
        
        for file_path in files_to_clean:
            try:
                # 检查文件年龄
                if max_age_days:
                    file_age = (current_time - os.path.getmtime(file_path)) / (24 * 3600)
                    if file_age < max_age_days:
                        continue
                
                os.remove(file_path)
                cleaned_count += 1
                logger.debug(f"已删除文件: {file_path}")
            except Exception as e:
                logger.debug(f"删除文件失败: {file_path}, 错误: {str(e)}")
        
        if cleaned_count > 0:
            logger.info(f"已清理 {cleaned_count} 个文件从目录: {directory}")
    except Exception as e:
        logger.error(f"清理目录时出错: {directory}, 错误: {str(e)}")

def get_file_size(file_path: str) -> int:
    """获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件大小（字节），失败返回0
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logger.debug(f"获取文件大小失败: {file_path}, 错误: {str(e)}")
        return 0

def get_directory_size(directory: str) -> int:
    """获取目录大小
    
    Args:
        directory: 目录路径
        
    Returns:
        目录大小（字节），失败返回0
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += get_file_size(file_path)
    except Exception as e:
        logger.debug(f"获取目录大小失败: {directory}, 错误: {str(e)}")
    
    return total_size

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        格式化的大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def safe_remove_file(file_path: str) -> bool:
    """安全删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        删除是否成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"已删除文件: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"删除文件失败: {file_path}, 错误: {str(e)}")
        return False

def safe_create_directory(directory: str) -> bool:
    """安全创建目录
    
    Args:
        directory: 目录路径
        
    Returns:
        创建是否成功
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"已创建目录: {directory}")
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {directory}, 错误: {str(e)}")
        return False

def is_file_locked(file_path: str) -> bool:
    """检查文件是否被锁定
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件是否被锁定
    """
    try:
        with open(file_path, 'a'):
            return False
    except IOError:
        return True
    except Exception:
        return True
