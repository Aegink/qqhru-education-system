# 📱 齐齐哈尔大学教务系统查询工具 v2.0.0 - 完整使用说明

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Kivy](https://img.shields.io/badge/Kivy-2.3.1-green.svg)](https://kivy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-lightgrey.svg)]()
[![Build APK](https://github.com/your-username/your-repo/actions/workflows/build-apk.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/build-apk.yml)

一个现代化、模块化的齐齐哈尔大学教务系统成绩查询工具，采用全新的架构设计，提供更好的用户体验和代码可维护性。

---

## 📋 目录

1. [项目概述](#项目概述)
2. [快速开始](#快速开始)
3. [功能特性](#功能特性)
4. [网络设置](#网络设置)
5. [自动登录](#自动登录)
6. [验证码优化](#验证码优化)
7. [故障排除](#故障排除)
8. [开发指南](#开发指南)
9. [更新日志](#更新日志)

---

## 🎯 项目概述

### v2.0.0 重构版本特性

#### 🏗️ 全新架构
- **模块化设计**: 清晰的代码结构，分离关注点
- **类型提示**: 完整的类型注解，提高代码质量
- **错误处理**: 完善的异常处理和恢复机制
- **日志系统**: 详细的日志记录和调试支持

#### 🎨 现代化UI
- **响应式设计**: 自适应不同屏幕尺寸（手机、平板、桌面）
- **Material Design 3.0**: 采用最新的设计语言
- **主题支持**: 支持亮色和暗色主题
- **流畅动画**: 优化的用户交互体验

#### ⚡ 性能优化
- **内存管理**: 智能内存清理和纹理缓存管理
- **异步处理**: 后台线程处理，避免界面卡顿
- **资源优化**: 优化的资源加载和清理机制
- **启动速度**: 更快的应用启动时间

### 项目结构
```
project_root/
├── src/                          # 源代码目录
│   ├── __init__.py              # 主包初始化
│   ├── app.py                   # 主应用类
│   ├── core/                    # 核心功能模块
│   │   ├── config.py           # 配置管理
│   │   ├── session.py          # 会话管理
│   │   ├── auth.py             # 认证相关
│   │   ├── api.py              # API请求处理
│   │   └── auto_login.py       # 自动登录管理
│   ├── ui/                     # UI界面模块
│   │   ├── themes.py           # 主题和样式
│   │   ├── screens/            # 各个界面
│   │   └── components/         # UI组件
│   └── utils/                  # 工具模块
│       ├── font_manager.py     # 字体管理
│       ├── memory_manager.py   # 内存管理
│       └── helpers.py          # 辅助函数
├── assets/                     # 资源文件
├── data/                       # 数据目录
├── logs/                       # 日志目录
├── main.py                     # 应用入口
├── requirements.txt            # Python依赖
├── buildozer.spec             # Android打包配置
└── 启动应用.bat               # Windows启动器
```

---

## 🚀 快速开始

### 环境要求
- **Python**: 3.8 或更高版本（推荐 3.11+）
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+, Android 5.0+
- **内存**: 建议 2GB 以上（Android设备建议 1GB 以上）
- **网络**: 需要访问齐齐哈尔大学教务系统
- **存储**: 至少 100MB 可用空间

### 安装步骤

1. **下载项目**
   ```bash
   # 使用Git克隆（推荐）
   git clone <repository-url>
   cd education-system-query-tool
   
   # 或直接下载ZIP文件并解压
   ```

2. **创建虚拟环境**（推荐）
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行应用**
   ```bash
   python main.py
   ```

### 首次使用

1. **启动应用**: 运行 `python main.py`
2. **网络设置**: 根据网络环境选择校内网或校外网
3. **登录账号**: 点击"登录新账号"，输入学号和密码
4. **获取验证码**: 点击"刷新"按钮获取验证码
5. **完成登录**: 输入验证码并点击"登录"
6. **查询成绩**: 登录成功后，点击"查询本学期成绩"

---

## ✨ 功能特性

### 🔐 账号管理
- **多账号支持**: 支持保存和管理多个学生账号
- **会话持久化**: 自动保存登录状态，避免重复登录
- **智能切换**: 快速切换不同账号，支持会话验证
- **安全存储**: 本地安全存储账号信息

### 📊 成绩查询
- **实时查询**: 查询本学期最新成绩
- **详细信息**: 显示课程详细信息和统计数据
- **推送通知**: 支持成绩变化推送提醒（可选）
- **数据导出**: 支持成绩数据导出功能

### 🛠️ 技术特性
- **验证码处理**: 智能验证码识别和刷新
- **网络优化**: 智能重试和连接管理
- **配置管理**: 灵活的配置系统
- **跨平台**: 支持 Windows、macOS、Linux 和 Android

---

## 🌐 网络设置

### 功能概述
为了适应学校的网络环境（校内网和校外网定时开放），应用提供了完整的网络切换功能。

### 网络配置
```json
{
  "NETWORK_URLS": {
    "校外网": "http://111.43.36.164",
    "校内网": "http://10.10.10.10"
  },
  "CURRENT_NETWORK": "校外网"
}
```

### 使用方法

#### 1. 进入网络设置
- 主界面 → 点击"网络设置"按钮

#### 2. 查看网络状态
- 查看当前使用的网络和连接状态
- 每个网络显示实时连接状态

#### 3. 测试网络连接
- **单个测试**: 点击"测试连接"按钮
- **批量测试**: 点击"测试所有"按钮
- **状态显示**: 
  - 🟢 连接正常
  - 🔴 连接失败
  - 🟡 测试中

#### 4. 切换网络
- 选择目标网络 → 点击"切换"按钮
- 系统自动更新所有相关URL

#### 5. 管理网络配置
- **添加网络**: 点击"添加网络"按钮
- **编辑URL**: 点击"编辑"按钮在线修改
- **删除网络**: 点击"删除"按钮移除配置

### 网络状态说明
- **连接正常**: 网络可以正常访问教务系统
- **连接失败**: 网络超时或服务器地址错误
- **测试中**: 正在测试连接状态
- **未知**: 尚未测试连接状态

---

## 🔄 自动登录

### 功能概述
自动登录功能可以监控会话状态，在会话过期时尝试重新登录，确保用户始终保持登录状态。

### 配置参数
```json
{
  "AUTO_LOGIN_ENABLED": false,
  "AUTO_LOGIN_CHECK_INTERVAL": 300,
  "AUTO_LOGIN_RETRY_COUNT": 3,
  "SESSION_EXPIRE_THRESHOLD": 600
}
```

### 使用方法

#### 1. 启用自动登录
- **前置条件**: 确保已登录且会话有效
- **启用方式**: 点击"启用自动登录"按钮
- **确认启用**: 系统显示启用成功提示

#### 2. 检查状态
点击"检查状态"按钮查看详细信息：
```
启用状态: 是
当前账号: 20210001
会话状态: 有效
监控状态: 运行中
上次检查: 2025-07-17 11:15:30
检查间隔: 5分钟
```

#### 3. 禁用自动登录
- 点击"禁用自动登录"按钮
- 系统停止后台监控

### 状态指示
- **🟢 已启用**: 自动登录功能正常运行
- **🔴 未启用**: 自动登录功能未启用
- **🟡 会话无效**: 当前会话已过期
- **⚪ 未登录**: 没有当前登录账号

### 工作原理
1. **定期检查**: 每5分钟检查一次会话状态
2. **自动重连**: 发现会话过期时自动尝试重新登录
3. **状态更新**: 实时更新界面状态显示
4. **结果通知**: 登录成功或失败时显示通知

---

## 🔧 验证码优化

### 优化内容
- **按需加载**: 验证码只在点击刷新时获取，不自动加载
- **异步处理**: 后台线程处理验证码请求，避免UI卡死
- **用户提示**: 显示"点击刷新按钮获取验证码"提示
- **错误处理**: 完善的错误处理和重试机制

### 使用方法
1. **进入登录**: 点击"登录新账号"
2. **输入信息**: 输入学号和密码
3. **获取验证码**: 点击"刷新"按钮获取验证码
4. **输入验证码**: 在验证码输入框中输入
5. **完成登录**: 点击"登录"按钮

### 注意事项
- 首次进入登录界面时不会自动加载验证码
- 必须点击"刷新"按钮才能获取验证码
- 验证码错误时会自动刷新
- 可以多次点击刷新获取新验证码

---

## 🐛 故障排除

### 常见问题

#### Q: 启动时提示缺少依赖包
**A**: 确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

#### Q: 验证码加载失败
**A**: 
1. 检查网络连接
2. 点击"刷新验证码"重试
3. 确保可以访问教务系统网站

#### Q: 登录失败
**A**: 
1. 检查学号和密码是否正确
2. 确认验证码输入正确
3. 检查网络连接状态

#### Q: 界面显示异常
**A**: 
1. 重启应用
2. 检查屏幕分辨率设置
3. 更新显卡驱动

#### Q: 自动登录无法启用
**A**: 
1. 确保已手动登录账号
2. 验证当前会话是否有效
3. 检查网络连接状态

### 日志查看
应用会在 `logs/` 目录下生成日志文件：
- `app.log`: 应用运行日志
- 设置 `DEBUG=true` 获取详细日志

### 重置应用
如遇到严重问题，可以重置应用数据：
1. 删除 `data/` 目录
2. 删除 `temp/` 目录
3. 重新启动应用

---

## 👨‍💻 开发指南

### 开发环境设置
```bash
# 安装开发依赖
pip install -r requirements.txt

# 启用调试模式
export DEBUG=true  # Linux/macOS
set DEBUG=true     # Windows

# 运行应用
python main.py
```

### 代码结构说明
- **src/core/**: 核心业务逻辑
- **src/ui/**: 用户界面相关代码
- **src/utils/**: 工具函数和辅助类
- **src/app.py**: 主应用类

### 添加新功能
1. 在相应的模块中添加功能代码
2. 更新 `__init__.py` 文件的导出
3. 添加必要的测试
4. 更新文档

### 代码规范
- 使用 Python 3.8+ 语法
- 遵循 PEP 8 代码风格
- 添加适当的类型提示
- 编写清晰的文档字符串

---

## 📱 Android APK 打包

### GitHub Actions 自动构建（推荐）
本项目配置了完整的 GitHub Actions 工作流，可以自动构建 Android APK：

1. **Fork 项目**: Fork 本项目到您的 GitHub 账号
2. **启用 Actions**: 在 Actions 页面启用 GitHub Actions
3. **触发构建**:
   - 推送代码到 main/master 分支自动触发
   - 或在 Actions 页面手动触发 workflow
4. **下载 APK**: 构建完成后在 Releases 页面下载 APK

#### 构建特性
- ✅ 自动依赖管理和版本固定
- ✅ 自动生成应用图标和启动画面
- ✅ 支持 ARM64 架构（现代 Android 设备）
- ✅ 完整的错误日志和调试信息
- ✅ 自动发布到 GitHub Releases

### 本地打包
如果需要本地构建，请按以下步骤操作：

```bash
# 1. 安装构建依赖
pip install buildozer==1.5.0 cython==3.0.10

# 2. 安装项目依赖
pip install -r requirements.txt

# 3. 生成资源文件（如果不存在）
python create_assets.py

# 4. 构建 APK
buildozer android debug

# 5. 构建发布版本（可选）
buildozer android release
```

#### 本地构建要求
- Linux 或 macOS 系统（推荐 Ubuntu 20.04+）
- Java 17 JDK
- Android SDK 和 NDK（buildozer 会自动下载）
- 至少 8GB 可用磁盘空间

---

## 📝 更新日志

### v2.0.0 (2025-07-17)
#### 🎉 重大更新
- **完全重构**: 采用模块化架构设计
- **现代化UI**: Material Design 3.0风格界面
- **性能优化**: 内存管理和异步处理优化
- **跨平台支持**: 新增 Android APK 支持

#### 🆕 新增功能
- **网络设置**: 完整的网络切换和管理功能
- **自动登录**: 智能会话监控和自动重连
- **验证码优化**: 按需加载，避免不必要的网络请求
- **Android 支持**: 完整的 Android APK 构建流程
- **自动资源生成**: 自动生成应用图标和启动画面

#### 🔧 技术改进
- **类型提示**: 完整的类型注解支持
- **错误处理**: 完善的异常处理机制
- **日志系统**: 详细的日志记录和调试支持
- **配置管理**: 灵活的配置系统
- **依赖管理**: 固定所有依赖版本，确保构建可重现性
- **CI/CD**: 完整的 GitHub Actions 自动构建流程

#### 🐛 问题修复
- 修复验证码刷新卡死问题
- 修复UI尺寸适配问题
- 修复内存泄漏问题
- 修复网络超时处理问题
- 修复 Android 构建兼容性问题

---

## 📞 技术支持

### 获取帮助
- **查看日志**: 检查 `logs/app.log` 文件
- **重置数据**: 删除 `data/` 和 `temp/` 目录

### 报告问题
如果遇到问题，请提供：
- 操作系统版本
- Python版本
- 错误信息截图
- 日志文件内容

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Kivy](https://kivy.org/) - 跨平台 Python GUI 框架
- [Requests](https://requests.readthedocs.io/) - HTTP 库
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML 解析库
- [Pillow](https://pillow.readthedocs.io/) - 图像处理库

---

**注意**: 本工具仅供学习和个人使用，请遵守学校相关规定。

**版本**: v2.0.0  
**更新时间**: 2025年7月17日  
**状态**: ✅ 正常运行
