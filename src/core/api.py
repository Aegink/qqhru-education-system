#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API模块
处理HTTP请求、成绩查询等API相关功能
"""

import re
import time
import json
import logging
import requests
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup

from .config import get_config
from .session import get_session

logger = logging.getLogger(__name__)

# 全局请求头
GLOBAL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def make_request(url: str, method: str = "GET", data: Optional[Dict] = None, 
                headers: Optional[Dict] = None, allow_redirects: bool = True, 
                timeout: int = 10, max_retries: int = 3) -> Optional[requests.Response]:
    """统一处理HTTP请求，简化错误处理和日志记录，添加智能重试机制
    
    Args:
        url: 请求URL
        method: 请求方法 (GET/POST)
        data: POST数据
        headers: 额外的请求头
        allow_redirects: 是否允许重定向
        timeout: 超时时间
        max_retries: 最大重试次数
        
    Returns:
        响应对象，失败返回None
    """
    current_session = get_session()
    
    for attempt in range(max_retries):
        try:
            # 使用全局headers作为基础，如果提供了额外headers则合并
            request_headers = GLOBAL_HEADERS.copy()
            if headers:
                request_headers.update(headers)
                
            # 根据请求方法选择不同的处理方式
            if method.upper() == "GET":
                response = current_session.get(
                    url, 
                    headers=request_headers, 
                    timeout=timeout, 
                    allow_redirects=allow_redirects
                )
            elif method.upper() == "POST":
                # 如果是POST请求且有数据，自动设置content-type
                if data and "Content-Type" not in request_headers:
                    request_headers["Content-Type"] = "application/x-www-form-urlencoded"
                response = current_session.post(
                    url, 
                    data=data, 
                    headers=request_headers, 
                    timeout=timeout, 
                    allow_redirects=allow_redirects
                )
            else:
                logger.error(f"不支持的HTTP方法: {method}")
                return None
                
            # 记录请求结果
            logger.debug(f"{method} {url} - 状态码: {response.status_code}")
            
            return response
        except requests.exceptions.Timeout:
            wait_time = 2 ** attempt  # 指数退避策略
            logger.warning(f"请求超时: {url}，尝试次数: {attempt+1}/{max_retries}，等待 {wait_time} 秒后重试")
            if attempt < max_retries - 1:  # 不是最后一次尝试
                time.sleep(wait_time)
            else:
                logger.error(f"请求超时: {url}，已达最大尝试次数")
                return None
        except requests.exceptions.ConnectionError:
            wait_time = 2 ** attempt  # 指数退避策略
            logger.warning(f"连接错误: {url}，尝试次数: {attempt+1}/{max_retries}，等待 {wait_time} 秒后重试")
            if attempt < max_retries - 1:  # 不是最后一次尝试
                time.sleep(wait_time)
            else:
                logger.error(f"连接错误: {url}，已达最大尝试次数")
                return None
        except Exception as e:
            logger.error(f"请求异常: {url}, 错误: {str(e)}")
            return None
    
    return None

def extract_student_name(html_content: str) -> Optional[str]:
    """从HTML内容中提取学生姓名
    
    Args:
        html_content: HTML页面内容
        
    Returns:
        学生姓名，失败返回None
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        user_info_span = soup.find('span', class_='user-info')
        
        if user_info_span:
            # 获取所有文本节点
            texts = user_info_span.find_all(text=True, recursive=True)
            
            # 查找包含姓名的文本节点
            for text in texts:
                # 跳过包含"欢迎您"的文本
                if "欢迎您" in text or "欢迎" in text:
                    continue
                
                # 尝试提取纯姓名文本
                name_text = text.strip()
                if name_text and len(name_text) < 10:  # 假设姓名长度小于10个字符
                    return name_text
            
            # 如果没找到单独的姓名节点，尝试从整个文本中提取
            full_text = user_info_span.get_text(strip=True)
            if "欢迎您" in full_text:
                # 分割文本并提取姓名部分
                parts = full_text.split("欢迎您")
                if len(parts) > 1:
                    name_part = parts[1].strip()
                    # 去除可能的标点符号
                    name_part = re.sub(r'[，,。、\s]', '', name_part)
                    return name_part
            return full_text.replace("欢迎您", "").strip()
        
        logger.warning("未找到用户信息区域")
        return None
    except Exception as e:
        logger.error(f"提取学生姓名时出错: {str(e)}")
        return None

class TempFileManager:
    """临时文件管理器（用于调试）"""
    
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
        
        import os
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
    
    def save_json(self, data: Any, filename: str) -> str:
        """保存JSON数据到临时文件"""
        if not self.debug_mode:
            return ""
        
        import os
        temp_dir = get_config("TEMP_DIR")
        os.makedirs(temp_dir, exist_ok=True)
        
        filepath = os.path.join(temp_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.temp_files.append(filepath)
            logger.debug(f"已保存JSON文件: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            return ""
    
    def clean_all(self):
        """清理所有临时文件"""
        if self.debug_mode:
            return
        
        import os
        for filepath in self.temp_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.debug(f"已删除临时文件: {filepath}")
            except Exception as e:
                logger.debug(f"删除临时文件失败: {filepath}, 错误: {e}")
        
        self.temp_files.clear()

def get_scores_from_api(soup: BeautifulSoup, temp_manager: TempFileManager, 
                       debug_mode: bool = False) -> List[List[str]]:
    """从API获取成绩数据
    
    Args:
        soup: 解析后的HTML页面
        temp_manager: 临时文件管理器
        debug_mode: 是否开启调试模式
        
    Returns:
        成绩数据行列表
    """
    logger.info("尝试从API获取成绩数据...")
    
    # 从页面中提取数据URL
    data_url = None
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'var url =' in script.string:
            url_match = re.search(r'var url = "([^"]+)"', script.string)
            if url_match:
                data_url = url_match.group(1)
                break
    
    if not data_url:
        # 如果找不到URL，使用默认URL
        data_url = "/student/integratedQuery/scoreQuery/rCkM7fdfvX/thisTermScores/data"
    
    # 构建完整URL
    full_data_url = f"{get_config('BASE_URL')}{data_url}"
    logger.info(f"获取成绩数据URL: {full_data_url}")
    
    # 请求成绩数据
    try:
        data_resp = make_request(full_data_url, timeout=15)
        if data_resp and data_resp.status_code == 200:
            try:
                score_data = data_resp.json()
                
                # 只在调试模式下保存JSON数据
                if debug_mode:
                    json_debug_file = temp_manager.save_json(
                        score_data, 
                        f"scores_data_{time.strftime('%Y%m%d_%H%M%S')}.json"
                    )
                    if json_debug_file:
                        logger.debug(f"已保存成绩数据到: {json_debug_file}")
                
                # 提取成绩数据
                if score_data and len(score_data) > 0 and 'list' in score_data[0]:
                    score_list = score_data[0]['list']
                    if score_list and len(score_list) > 0:
                        logger.info(f"成功获取到 {len(score_list)} 条成绩记录")
                        
                        # 转换为表格行格式
                        rows = []
                        for item in score_list:
                            row = []
                            # 课程号
                            row.append(item.get('id', {}).get('courseNumber', ''))
                            # 课序号
                            row.append(item.get('coureSequenceNumber', ''))
                            # 课程名
                            row.append(item.get('courseName', ''))
                            # 学分
                            row.append(item.get('credit', ''))
                            # 课程属性
                            row.append(item.get('coursePropertyName', ''))
                            # 课程最高分
                            row.append(item.get('maxcj', ''))
                            # 课程最低分
                            row.append(item.get('mincj', ''))
                            # 课程平均分
                            row.append(item.get('avgcj', ''))
                            # 成绩
                            if item.get('inputMethodCode') == '002':
                                row.append(item.get('levelName', ''))
                            else:
                                row.append(item.get('courseScore', ''))
                            # 名次
                            row.append(item.get('rank', ''))
                            # 未通过原因
                            row.append(item.get('unpassedReasonExplain', ''))
                            # 英文课程名
                            row.append(item.get('englishCourseName', ''))
                            
                            rows.append(row)
                        
                        return rows
            except Exception as json_error:
                logger.error(f"解析成绩数据失败: {str(json_error)}")
    except Exception as req_error:
        logger.error(f"请求成绩数据失败: {str(req_error)}")
    
    return []

def get_scores_from_html(soup: BeautifulSoup) -> List[List[str]]:
    """从HTML解析成绩表格

    Args:
        soup: 解析后的HTML页面

    Returns:
        成绩数据行列表
    """
    rows = []

    # 方法1：查找ID为scoretbody的元素
    score_table = soup.find('tbody', id='scoretbody')
    if score_table:
        logger.info("找到ID为scoretbody的表格")
        for row in score_table.find_all('tr'):
            cols = [td.get_text(strip=True) for td in row.find_all('td')]
            if cols:  # 确保非空行
                rows.append(cols)

    # 方法2：如果方法1失败，尝试使用CSS选择器
    if not rows:
        logger.info("尝试使用CSS选择器查找表格行...")
        all_trs = soup.select("#scoretbody tr")
        if all_trs:
            for tr in all_trs:
                cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                if cols:
                    rows.append(cols)

    # 方法3：如果上述方法都失败，尝试查找任何包含成绩数据的表格
    if not rows:
        logger.info("尝试查找页面中任何表格...")
        for table in soup.find_all('table', class_='table'):
            tbody = table.find('tbody')
            if tbody:
                for tr in tbody.find_all('tr'):
                    cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                    if cols and len(cols) > 5:  # 假设成绩行有足够多的列
                        rows.append(cols)

    return rows

def handle_no_scores(response: requests.Response, student_name: str):
    """处理没有成绩数据的情况

    Args:
        response: HTTP响应对象
        student_name: 学生姓名
    """
    logger.warning("未能找到成绩数据，请检查页面结构或登录状态")

    # 检查是否需要重新登录
    if "login" in response.url:
        logger.warning("检测到页面已跳转到登录页，会话可能已过期")
        return

    logger.info("本学期可能没有成绩数据")
    # 发送通知
    pushplus_notify(f"{student_name}的成绩查询结果", "本学期没有成绩数据")

def display_score_results(score_rows: List[List[str]], student_name: str):
    """显示成绩结果

    Args:
        score_rows: 成绩数据行
        student_name: 学生姓名
    """
    if not score_rows:
        logger.info("没有成绩数据可显示")
        return

    logger.info(f"\n{student_name}的本学期成绩:")
    logger.info("=" * 80)

    # 表头
    headers = ["课程号", "课序号", "课程名", "学分", "课程属性", "最高分", "最低分", "平均分", "成绩", "名次", "未通过原因", "英文课程名"]

    # 计算列宽
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(header)
        for row in score_rows:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(min(max_width + 2, 20))  # 限制最大宽度

    # 打印表头
    header_line = ""
    for i, header in enumerate(headers):
        if i < len(col_widths):
            header_line += header.ljust(col_widths[i])
    logger.info(header_line)
    logger.info("-" * len(header_line))

    # 打印数据行
    for row in score_rows:
        data_line = ""
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cell_str = str(cell)[:col_widths[i]-2]  # 截断过长的内容
                data_line += cell_str.ljust(col_widths[i])
        logger.info(data_line)

    logger.info("=" * 80)
    logger.info(f"共查询到 {len(score_rows)} 门课程的成绩")

def pushplus_notify(title: str, content: str) -> bool:
    """发送PushPlus通知

    Args:
        title: 通知标题
        content: 通知内容

    Returns:
        发送是否成功
    """
    token = get_config("PUSHPLUS_TOKEN")
    if not token or token == "you":
        logger.debug("未配置PushPlus token，跳过通知发送")
        return False

    try:
        url = get_config("PUSHPLUS_URL")
        data = {
            "token": token,
            "title": title,
            "content": content
        }

        response = make_request(url, method="POST", data=data, timeout=10)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                logger.info("通知发送成功")
                return True
            else:
                logger.error(f"通知发送失败: {result.get('msg', '未知错误')}")
        else:
            logger.error("通知发送请求失败")
    except Exception as e:
        logger.error(f"发送通知时出错: {e}")

    return False

def query_scores(debug_mode: bool = False) -> bool:
    """查询本学期成绩并格式化输出

    Args:
        debug_mode: 是否开启调试模式

    Returns:
        查询是否成功
    """
    # 成绩查询URL
    scores_url = get_config("SCORES_URL")

    # 创建临时文件管理器
    temp_manager = TempFileManager()
    temp_manager.set_debug_mode(debug_mode)

    try:
        logger.info("\n正在访问成绩查询页面...")
        scores_resp = make_request(scores_url, timeout=15)

        if not scores_resp or scores_resp.status_code != 200:
            logger.error(f"成绩查询失败，状态码: {scores_resp.status_code if scores_resp else 'None'}")
            return False

        # 只在调试模式下保存页面内容
        if debug_mode:
            debug_file = temp_manager.save_content(
                scores_resp.text,
                f"scores_page_{time.strftime('%Y%m%d_%H%M%S')}.html",
                encoding="utf-8"
            )
            if debug_file:
                logger.debug(f"已保存页面内容到: {debug_file}")

        # 解析HTML
        soup = BeautifulSoup(scores_resp.text, 'html.parser')

        # 提取学生姓名
        student_name = extract_student_name(scores_resp.text)
        if student_name:
            logger.info(f"获取到学生姓名: {student_name}")
        else:
            logger.warning("未能获取学生姓名")
            student_name = "同学"  # 默认称呼

        # 尝试从API获取成绩数据
        score_rows = get_scores_from_api(soup, temp_manager, debug_mode)

        # 如果API方法失败，尝试从HTML解析
        if not score_rows:
            logger.info("\n尝试从HTML解析成绩表格...")
            score_rows = get_scores_from_html(soup)

        # 如果使用所有方法后仍然没有数据
        if not score_rows:
            handle_no_scores(scores_resp, student_name)
            temp_manager.clean_all()
            return True

        # 处理和显示成绩数据
        display_score_results(score_rows, student_name)

        # 清理临时文件
        temp_manager.clean_all()
        return True
    except Exception as e:
        logger.error(f"查询成绩时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 清理临时文件
        temp_manager.clean_all()
        return False
