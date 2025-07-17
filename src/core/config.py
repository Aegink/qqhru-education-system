#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
管理应用程序的所有配置项
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    # 网络环境配置 - 支持多种网络环境，每个环境有完整的URL配置
    "NETWORK_CONFIGS": {
        "校外网": {
            "base_url": "http://111.43.36.164",
            "login_path": "/login",
            "login_post_path": "/j_spring_security_check",
            "scores_path": "/student/integratedQuery/scoreQuery/thisTermScores/index",
            "captcha_path": "/captcha",
            "logout_path": "/logout",
            "student_info_path": "/student/studentinfo/studentInfoModify/index",
            "description": "校外网络环境，适用于校外访问教务系统"
        },
        "校内网": {
            "base_url": "http://10.10.10.10",
            "login_path": "/login",
            "login_post_path": "/j_spring_security_check",
            "scores_path": "/student/integratedQuery/scoreQuery/thisTermScores/index",
            "captcha_path": "/captcha",
            "logout_path": "/logout",
            "student_info_path": "/student/studentinfo/studentInfoModify/index",
            "description": "校内网络环境，适用于校内访问教务系统"
        }
    },
    "CURRENT_NETWORK": "校外网",  # 当前选择的网络环境

    # 系统URL配置（根据当前网络环境动态生成，请勿手动修改）
    "BASE_URL": "http://111.43.36.164",
    "LOGIN_URL": "http://111.43.36.164/login",
    "LOGIN_POST_URL": "http://111.43.36.164/j_spring_security_check",
    "SCORES_URL": "http://111.43.36.164/student/integratedQuery/scoreQuery/thisTermScores/index",
    "CAPTCHA_URL": "http://111.43.36.164/captcha",
    "LOGOUT_URL": "http://111.43.36.164/logout",
    "STUDENT_INFO_URL": "http://111.43.36.164/student/studentinfo/studentInfoModify/index",

    # 兼容性配置（为了向后兼容，从NETWORK_CONFIGS自动生成）
    "NETWORK_URLS": {
        "校外网": "http://111.43.36.164",
        "校内网": "http://10.10.10.10"
    },

    # 推送配置
    "PUSHPLUS_TOKEN": "you",  # 用户需要替换为自己的token
    "PUSHPLUS_URL": "http://www.pushplus.plus/send",
    
    # 目录配置
    "DATA_DIR": "data",
    "SESSION_DIR": "data/sessions",
    "ACCOUNTS_FILE": "data/accounts.json",
    "CREDENTIALS_FILE": "data/credentials.json",
    "LOGS_DIR": "logs",
    "TEMP_DIR": "temp",
    
    # 应用配置
    "DEBUG_MODE": False,
    "AUTO_LOGIN_ENABLED": False,       # 是否启用自动登录
    "AUTO_LOGIN_CHECK_INTERVAL": 300,  # 自动登录检查间隔（秒）
    "SESSION_EXPIRE_THRESHOLD": 600,   # 会话过期阈值（秒）
    "AUTO_LOGIN_RETRY_COUNT": 3,       # 自动登录重试次数
    "LAST_AUTO_LOGIN_TIME": 0,         # 上次自动登录时间戳
    
    # UI配置
    "WINDOW_WIDTH": 400,
    "WINDOW_HEIGHT": 600,
    "MIN_WINDOW_WIDTH": 350,
    "MIN_WINDOW_HEIGHT": 500,
    
    # 网络配置
    "REQUEST_TIMEOUT": 30,
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 1.0,
}

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        # 确保配置文件存放在data目录中
        if config_file is None:
            data_dir = DEFAULT_CONFIG["DATA_DIR"]
            # 确保data目录存在
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            config_file = os.path.join(data_dir, "config.json")
        self.config_file = config_file
        self._config = DEFAULT_CONFIG.copy()
        self._load_config()

        # 如果配置文件不存在，创建一个默认的
        if not os.path.exists(self.config_file):
            self.save_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._config.update(user_config)
                    logger.info(f"已加载配置文件: {self.config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 保存标准JSON格式
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)

            # 同时保存带注释的版本
            config_with_comments_file = self.config_file.replace('.json', '_commented.json')
            config_content = self._create_config_with_comments()
            with open(config_with_comments_file, 'w', encoding='utf-8') as f:
                f.write(config_content)

            logger.info(f"配置已保存到: {self.config_file}")
            logger.debug(f"带注释的配置已保存到: {config_with_comments_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def _create_config_with_comments(self) -> str:
        """创建带中文注释的配置文件内容"""
        lines = []
        lines.append("{")
        lines.append('  // ==================== 齐齐哈尔大学教务系统查询工具配置文件 ====================')
        lines.append('  // 本文件包含应用的所有配置项，请根据实际情况修改')
        lines.append('  // 修改后重启应用生效')
        lines.append('')

        # 网络环境配置
        if "NETWORK_CONFIGS" in self._config:
            lines.append('  // ==================== 网络环境配置 ====================')
            lines.append('  // 支持多种网络环境，每个环境包含完整的URL路径配置')
            lines.append('  // 可以添加新的网络环境或修改现有环境的配置')
            lines.append('  "NETWORK_CONFIGS": {')

            for i, (name, config) in enumerate(self._config["NETWORK_CONFIGS"].items()):
                lines.append(f'    "{name}": {{')
                lines.append(f'      "base_url": "{config["base_url"]}",  // 基础URL地址')
                lines.append(f'      "login_path": "{config["login_path"]}",  // 登录页面路径')
                lines.append(f'      "login_post_path": "{config["login_post_path"]}",  // 登录提交路径')
                lines.append(f'      "scores_path": "{config["scores_path"]}",  // 成绩查询路径')
                lines.append(f'      "captcha_path": "{config["captcha_path"]}",  // 验证码获取路径')
                lines.append(f'      "logout_path": "{config["logout_path"]}",  // 退出登录路径')
                lines.append(f'      "student_info_path": "{config["student_info_path"]}",  // 学生信息路径')
                lines.append(f'      "description": "{config["description"]}"  // 环境描述')

                if i < len(self._config["NETWORK_CONFIGS"]) - 1:
                    lines.append('    },')
                else:
                    lines.append('    }')

            lines.append('  },')
            lines.append('')

        # 当前网络
        if "CURRENT_NETWORK" in self._config:
            lines.append('  // 当前选择的网络环境（从上面的NETWORK_CONFIGS中选择）')
            lines.append(f'  "CURRENT_NETWORK": "{self._config["CURRENT_NETWORK"]}",')
            lines.append('')

        # 系统URL配置
        url_configs = [
            ("BASE_URL", "基础URL地址"),
            ("LOGIN_URL", "登录页面完整URL"),
            ("LOGIN_POST_URL", "登录提交完整URL"),
            ("SCORES_URL", "成绩查询完整URL"),
            ("CAPTCHA_URL", "验证码获取完整URL"),
            ("LOGOUT_URL", "退出登录完整URL"),
            ("STUDENT_INFO_URL", "学生信息完整URL")
        ]

        lines.append('  // ==================== 系统URL配置 ====================')
        lines.append('  // 以下URL根据当前网络环境自动生成，请勿手动修改')
        for key, desc in url_configs:
            if key in self._config:
                lines.append(f'  "{key}": "{self._config[key]}",  // {desc}')
        lines.append('')

        # 兼容性配置
        if "NETWORK_URLS" in self._config:
            lines.append('  // ==================== 兼容性配置 ====================')
            lines.append('  // 为了向后兼容保留的配置，从NETWORK_CONFIGS自动生成')
            lines.append('  "NETWORK_URLS": {')
            network_urls = self._config["NETWORK_URLS"]
            for i, (name, url) in enumerate(network_urls.items()):
                comma = "," if i < len(network_urls) - 1 else ""
                lines.append(f'    "{name}": "{url}"{comma}')
            lines.append('  },')
            lines.append('')

        # 推送配置
        lines.append('  // ==================== 推送通知配置 ====================')
        lines.append('  // 用于成绩变化推送通知，需要申请PushPlus token')
        if "PUSHPLUS_TOKEN" in self._config:
            lines.append(f'  "PUSHPLUS_TOKEN": "{self._config["PUSHPLUS_TOKEN"]}",  // 请替换为您的PushPlus token')
        if "PUSHPLUS_URL" in self._config:
            lines.append(f'  "PUSHPLUS_URL": "{self._config["PUSHPLUS_URL"]}",  // PushPlus推送接口地址')
        lines.append('')

        # 目录配置
        dir_configs = [
            ("DATA_DIR", "数据存储目录"),
            ("SESSION_DIR", "会话文件目录"),
            ("ACCOUNTS_FILE", "账号信息文件"),
            ("CREDENTIALS_FILE", "凭据文件"),
            ("LOGS_DIR", "日志文件目录"),
            ("TEMP_DIR", "临时文件目录")
        ]

        lines.append('  // ==================== 目录和文件配置 ====================')
        lines.append('  // 应用数据存储目录配置，建议使用默认值')
        for key, desc in dir_configs:
            if key in self._config:
                lines.append(f'  "{key}": "{self._config[key]}",  // {desc}')
        lines.append('')

        # 应用配置
        app_configs = [
            ("DEBUG_MODE", "调试模式，开启后会显示详细日志"),
            ("AUTO_LOGIN_ENABLED", "自动登录功能开关"),
            ("AUTO_LOGIN_CHECK_INTERVAL", "自动登录检查间隔（秒）"),
            ("SESSION_EXPIRE_THRESHOLD", "会话过期阈值（秒）"),
            ("AUTO_LOGIN_RETRY_COUNT", "自动登录重试次数"),
            ("LAST_AUTO_LOGIN_TIME", "上次自动登录时间戳")
        ]

        lines.append('  // ==================== 应用功能配置 ====================')
        for key, desc in app_configs:
            if key in self._config:
                value = self._config[key]
                if isinstance(value, bool):
                    value_str = "true" if value else "false"
                else:
                    value_str = str(value)
                lines.append(f'  "{key}": {value_str},  // {desc}')
        lines.append('')

        # UI配置
        ui_configs = [
            ("WINDOW_WIDTH", "窗口宽度"),
            ("WINDOW_HEIGHT", "窗口高度"),
            ("MIN_WINDOW_WIDTH", "最小窗口宽度"),
            ("MIN_WINDOW_HEIGHT", "最小窗口高度")
        ]

        lines.append('  // ==================== 界面配置 ====================')
        lines.append('  // 应用窗口大小配置')
        for key, desc in ui_configs:
            if key in self._config:
                lines.append(f'  "{key}": {self._config[key]},  // {desc}')
        lines.append('')

        # 网络配置
        net_configs = [
            ("REQUEST_TIMEOUT", "网络请求超时时间（秒）"),
            ("MAX_RETRIES", "最大重试次数"),
            ("RETRY_DELAY", "重试延迟时间（秒）")
        ]

        lines.append('  // ==================== 网络请求配置 ====================')
        lines.append('  // 网络请求超时和重试配置')
        for key, desc in net_configs:
            if key in self._config:
                lines.append(f'  "{key}": {self._config[key]},  // {desc}')

        # 移除最后一个逗号
        if lines and lines[-1].endswith(','):
            lines[-1] = lines[-1][:-1]

        lines.append('')
        lines.append('  // ==================== 配置文件结束 ====================')
        lines.append('}')

        return '\n'.join(lines)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置项"""
        self._config[key] = value
    
    def update(self, config_dict: Dict[str, Any]):
        """批量更新配置"""
        self._config.update(config_dict)
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()
    
    def reset_to_default(self):
        """重置为默认配置"""
        self._config = DEFAULT_CONFIG.copy()

    def delete_config_file(self):
        """删除配置文件"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                logger.info(f"配置文件已删除: {self.config_file}")
                return True
            else:
                logger.warning(f"配置文件不存在: {self.config_file}")
                return False
        except Exception as e:
            logger.error(f"删除配置文件失败: {e}")
            return False

    def get_config_file_path(self) -> str:
        """获取配置文件路径"""
        return self.config_file

    def get_config_file_size(self) -> int:
        """获取配置文件大小（字节）"""
        try:
            if os.path.exists(self.config_file):
                return os.path.getsize(self.config_file)
            return 0
        except Exception:
            return 0

    def backup_config(self, backup_path: Optional[str] = None) -> bool:
        """备份配置文件"""
        try:
            if not os.path.exists(self.config_file):
                logger.warning("配置文件不存在，无法备份")
                return False

            if backup_path is None:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"config_backup_{timestamp}.json"
                backup_path = os.path.join(os.path.dirname(self.config_file), backup_filename)

            import shutil
            shutil.copy2(self.config_file, backup_path)
            logger.info(f"配置文件已备份到: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"备份配置文件失败: {e}")
            return False

# 全局配置管理器实例
_config_manager = ConfigManager()

# 兼容性：保持原有的CONFIG字典接口
CONFIG = _config_manager.get_all()

def get_config(key: str, default: Any = None) -> Any:
    """获取配置项"""
    return _config_manager.get(key, default)

def update_config(key: str, value: Any):
    """更新配置项"""
    _config_manager.set(key, value)
    # 同步更新CONFIG字典
    CONFIG[key] = value

def save_config():
    """保存配置"""
    _config_manager.save_config()

def load_config():
    """重新加载配置"""
    _config_manager._load_config()
    CONFIG.clear()
    CONFIG.update(_config_manager.get_all())

def delete_config_file():
    """删除配置文件"""
    return _config_manager.delete_config_file()

def get_config_file_path():
    """获取配置文件路径"""
    return _config_manager.get_config_file_path()

def get_config_file_info():
    """获取配置文件信息"""
    path = _config_manager.get_config_file_path()
    size = _config_manager.get_config_file_size()
    exists = os.path.exists(path)

    info = {
        "path": path,
        "size": size,
        "exists": exists,
        "size_mb": round(size / 1024 / 1024, 2) if size > 0 else 0
    }

    if exists:
        try:
            import datetime
            mtime = os.path.getmtime(path)
            info["modified_time"] = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            info["modified_time"] = "未知"

    return info

def backup_config(backup_path: Optional[str] = None):
    """备份配置文件"""
    return _config_manager.backup_config(backup_path)

def reset_config():
    """重置配置为默认值"""
    _config_manager.reset_to_default()
    save_config()
    # 同步更新CONFIG字典
    CONFIG.clear()
    CONFIG.update(_config_manager.get_all())
    logger.info("配置已重置为默认值")

# 确保必要目录存在
def ensure_directories():
    """确保必要的目录存在"""
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

# 网络切换功能
def get_available_networks():
    """获取可用的网络选项"""
    # 优先使用新的NETWORK_CONFIGS配置
    network_configs = get_config("NETWORK_CONFIGS", {})
    if network_configs:
        return list(network_configs.keys())

    # 兼容旧的NETWORK_URLS配置
    return list(get_config("NETWORK_URLS", {}).keys())

def get_current_network():
    """获取当前选择的网络"""
    return get_config("CURRENT_NETWORK")

def switch_network(network_name: str):
    """切换网络环境

    Args:
        network_name: 网络名称（如"校外网"、"校内网"）

    Returns:
        bool: 切换是否成功
    """
    try:
        # 优先使用新的NETWORK_CONFIGS配置
        network_configs = get_config("NETWORK_CONFIGS", {})
        if network_name in network_configs:
            # 使用新的配置格式
            network_config = network_configs[network_name]
            base_url = network_config["base_url"]

            # 更新所有相关的URL配置
            update_config("CURRENT_NETWORK", network_name)
            update_config("BASE_URL", base_url)
            update_config("LOGIN_URL", f"{base_url}{network_config['login_path']}")
            update_config("LOGIN_POST_URL", f"{base_url}{network_config['login_post_path']}")
            update_config("SCORES_URL", f"{base_url}{network_config['scores_path']}")
            update_config("CAPTCHA_URL", f"{base_url}{network_config['captcha_path']}")
            update_config("LOGOUT_URL", f"{base_url}{network_config['logout_path']}")
            update_config("STUDENT_INFO_URL", f"{base_url}{network_config['student_info_path']}")

            # 更新兼容性配置
            network_urls = {}
            for name, config in network_configs.items():
                network_urls[name] = config["base_url"]
            update_config("NETWORK_URLS", network_urls)

        else:
            # 兼容旧的NETWORK_URLS配置
            network_urls = get_config("NETWORK_URLS")
            if network_name not in network_urls:
                logger.error(f"未知的网络选项: {network_name}")
                return False

            base_url = network_urls[network_name]

            # 更新基本URL配置（使用默认路径）
            update_config("CURRENT_NETWORK", network_name)
            update_config("BASE_URL", base_url)
            update_config("LOGIN_URL", f"{base_url}/login")
            update_config("LOGIN_POST_URL", f"{base_url}/j_spring_security_check")
            update_config("SCORES_URL", f"{base_url}/student/integratedQuery/scoreQuery/thisTermScores/index")
            update_config("CAPTCHA_URL", f"{base_url}/captcha")
            update_config("LOGOUT_URL", f"{base_url}/logout")
            update_config("STUDENT_INFO_URL", f"{base_url}/student/studentinfo/studentInfoModify/index")

        # 保存配置
        save_config()

        logger.info(f"已切换到网络环境: {network_name} ({base_url})")
        return True

    except Exception as e:
        logger.error(f"切换网络环境失败: {e}")
        return False

def add_network_config(network_name: str, base_url: str, **kwargs):
    """添加网络配置

    Args:
        network_name: 网络名称
        base_url: 基础URL
        **kwargs: 其他路径配置（login_path, scores_path等）
    """
    try:
        network_configs = get_config("NETWORK_CONFIGS", {}).copy()

        # 默认路径配置
        default_paths = {
            "login_path": "/login",
            "login_post_path": "/j_spring_security_check",
            "scores_path": "/student/integratedQuery/scoreQuery/thisTermScores/index",
            "captcha_path": "/captcha",
            "logout_path": "/logout",
            "student_info_path": "/student/studentinfo/studentInfoModify/index",
            "description": f"{network_name}网络环境"
        }

        # 合并用户提供的配置
        network_config = {
            "base_url": base_url,
            **default_paths,
            **kwargs
        }

        network_configs[network_name] = network_config
        update_config("NETWORK_CONFIGS", network_configs)

        # 更新兼容性配置
        network_urls = {}
        for name, config in network_configs.items():
            network_urls[name] = config["base_url"]
        update_config("NETWORK_URLS", network_urls)

        save_config()
        logger.info(f"已添加网络配置: {network_name} ({base_url})")
        return True

    except Exception as e:
        logger.error(f"添加网络配置失败: {e}")
        return False

def update_network_config(network_name: str, **kwargs):
    """更新网络配置

    Args:
        network_name: 网络名称
        **kwargs: 要更新的配置项
    """
    try:
        network_configs = get_config("NETWORK_CONFIGS", {}).copy()

        if network_name not in network_configs:
            logger.error(f"网络配置不存在: {network_name}")
            return False

        # 更新配置
        network_configs[network_name].update(kwargs)
        update_config("NETWORK_CONFIGS", network_configs)

        # 更新兼容性配置
        network_urls = {}
        for name, config in network_configs.items():
            network_urls[name] = config["base_url"]
        update_config("NETWORK_URLS", network_urls)

        save_config()
        logger.info(f"已更新网络配置: {network_name}")
        return True

    except Exception as e:
        logger.error(f"更新网络配置失败: {e}")
        return False

def remove_network_config(network_name: str):
    """删除网络配置

    Args:
        network_name: 网络名称
    """
    try:
        network_configs = get_config("NETWORK_CONFIGS", {}).copy()

        if network_name not in network_configs:
            logger.error(f"网络配置不存在: {network_name}")
            return False

        # 检查是否是当前网络
        current_network = get_config("CURRENT_NETWORK")
        if current_network == network_name:
            logger.error(f"无法删除当前使用的网络配置: {network_name}")
            return False

        # 删除配置
        del network_configs[network_name]
        update_config("NETWORK_CONFIGS", network_configs)

        # 更新兼容性配置
        network_urls = {}
        for name, config in network_configs.items():
            network_urls[name] = config["base_url"]
        update_config("NETWORK_URLS", network_urls)

        save_config()
        logger.info(f"已删除网络配置: {network_name}")
        return True

    except Exception as e:
        logger.error(f"删除网络配置失败: {e}")
        return False

def get_network_status():
    """获取网络状态信息"""
    current_network = get_current_network()
    base_url = get_config("BASE_URL")
    return {
        "current_network": current_network,
        "base_url": base_url,
        "available_networks": get_available_networks()
    }

def update_network_url(network_name: str, url: str):
    """更新网络URL

    Args:
        network_name: 网络名称
        url: 新的URL地址

    Returns:
        bool: 更新是否成功
    """
    try:
        network_urls = get_config("NETWORK_URLS").copy()
        network_urls[network_name] = url
        update_config("NETWORK_URLS", network_urls)

        # 如果更新的是当前网络，则同时更新相关URL
        if network_name == get_current_network():
            switch_network(network_name)
        else:
            save_config()

        logger.info(f"已更新{network_name}的URL为: {url}")
        return True

    except Exception as e:
        logger.error(f"更新网络URL失败: {e}")
        return False

# 初始化时确保目录存在
ensure_directories()
