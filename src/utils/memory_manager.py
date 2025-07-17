#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内存管理模块
优化应用性能，管理内存使用和纹理缓存
"""

import gc
import weakref
import logging
import threading
import time
from typing import Optional, Dict, Any
from kivy.clock import Clock

logger = logging.getLogger(__name__)

class MemoryManager:
    """内存管理器 - 帮助优化应用性能"""

    def __init__(self):
        self.texture_cache = weakref.WeakValueDictionary()
        self.cleanup_interval = 30  # 30秒清理一次
        self.last_cleanup_time = 0
        self.cleanup_scheduled = False
        self.memory_stats = {
            'texture_cleanups': 0,
            'gc_collections': 0,
            'cache_clears': 0
        }
        self._lock = threading.Lock()

    def cleanup_textures(self):
        """清理未使用的纹理"""
        with self._lock:
            try:
                # 强制垃圾回收
                collected = gc.collect()
                self.memory_stats['gc_collections'] += 1
                
                # 清理Kivy的纹理缓存
                try:
                    from kivy.cache import Cache
                    Cache.remove('kv.texture')
                    Cache.remove('kv.image')
                    self.memory_stats['cache_clears'] += 1
                except ImportError:
                    # 如果Kivy不可用，跳过
                    pass
                except Exception as cache_error:
                    logger.debug(f"清理Kivy缓存时出错: {cache_error}")

                self.memory_stats['texture_cleanups'] += 1
                self.last_cleanup_time = time.time()
                
                logger.debug(f"已执行纹理清理，回收对象数: {collected}")
            except Exception as e:
                logger.error(f"纹理清理失败: {e}")

    def schedule_cleanup(self):
        """定期清理内存"""
        if not self.cleanup_scheduled:
            try:
                Clock.schedule_interval(lambda dt: self.cleanup_textures(), self.cleanup_interval)
                self.cleanup_scheduled = True
                logger.debug(f"已启动定期内存清理，间隔: {self.cleanup_interval}秒")
            except Exception as e:
                logger.error(f"启动定期清理失败: {e}")

    def force_cleanup(self):
        """强制执行内存清理"""
        logger.info("执行强制内存清理")
        self.cleanup_textures()
        
        # 额外的深度清理
        try:
            # 清理弱引用字典
            self.texture_cache.clear()
            
            # 多次垃圾回收以确保彻底清理
            for _ in range(3):
                gc.collect()
            
            logger.info("强制内存清理完成")
        except Exception as e:
            logger.error(f"强制清理时出错: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存管理统计信息"""
        with self._lock:
            stats = self.memory_stats.copy()
            stats.update({
                'last_cleanup_time': self.last_cleanup_time,
                'cleanup_scheduled': self.cleanup_scheduled,
                'texture_cache_size': len(self.texture_cache)
            })
            return stats

    def reset_stats(self):
        """重置统计信息"""
        with self._lock:
            self.memory_stats = {
                'texture_cleanups': 0,
                'gc_collections': 0,
                'cache_clears': 0
            }
            logger.debug("内存管理统计信息已重置")

    def set_cleanup_interval(self, interval: int):
        """设置清理间隔
        
        Args:
            interval: 清理间隔（秒）
        """
        if interval > 0:
            self.cleanup_interval = interval
            logger.info(f"内存清理间隔已设置为: {interval}秒")
        else:
            logger.warning("清理间隔必须大于0")

    def add_texture_reference(self, key: str, texture):
        """添加纹理引用到缓存
        
        Args:
            key: 纹理键
            texture: 纹理对象
        """
        try:
            self.texture_cache[key] = texture
            logger.debug(f"已添加纹理引用: {key}")
        except Exception as e:
            logger.debug(f"添加纹理引用失败: {e}")

    def get_texture_reference(self, key: str):
        """获取纹理引用
        
        Args:
            key: 纹理键
            
        Returns:
            纹理对象或None
        """
        return self.texture_cache.get(key)

    def remove_texture_reference(self, key: str):
        """移除纹理引用
        
        Args:
            key: 纹理键
        """
        try:
            if key in self.texture_cache:
                del self.texture_cache[key]
                logger.debug(f"已移除纹理引用: {key}")
        except Exception as e:
            logger.debug(f"移除纹理引用失败: {e}")

    def cleanup_old_references(self, max_age: int = 300):
        """清理旧的引用
        
        Args:
            max_age: 最大存活时间（秒）
        """
        current_time = time.time()
        if current_time - self.last_cleanup_time > max_age:
            self.force_cleanup()

    def get_gc_stats(self) -> Dict[str, Any]:
        """获取垃圾回收统计信息"""
        try:
            return {
                'gc_counts': gc.get_count(),
                'gc_stats': gc.get_stats() if hasattr(gc, 'get_stats') else None,
                'gc_threshold': gc.get_threshold()
            }
        except Exception as e:
            logger.debug(f"获取GC统计信息失败: {e}")
            return {}

    def optimize_gc(self):
        """优化垃圾回收设置"""
        try:
            # 调整垃圾回收阈值以提高性能
            gc.set_threshold(700, 10, 10)
            logger.debug("已优化垃圾回收设置")
        except Exception as e:
            logger.error(f"优化垃圾回收设置失败: {e}")

    def cleanup(self):
        """清理内存管理器资源"""
        try:
            # 取消定期清理
            if self.cleanup_scheduled:
                try:
                    Clock.unschedule(self.cleanup_textures)
                except:
                    pass
                self.cleanup_scheduled = False
            
            # 最后一次清理
            self.force_cleanup()
            
            logger.info("内存管理器已清理")
        except Exception as e:
            logger.error(f"清理内存管理器时出错: {e}")

    def __del__(self):
        """析构函数"""
        try:
            self.cleanup()
        except:
            pass

# 创建全局内存管理器实例
_memory_manager = MemoryManager()

def get_memory_manager() -> MemoryManager:
    """获取全局内存管理器实例"""
    return _memory_manager

def cleanup_textures():
    """清理纹理（便捷函数）"""
    _memory_manager.cleanup_textures()

def force_cleanup():
    """强制清理内存（便捷函数）"""
    _memory_manager.force_cleanup()

def schedule_cleanup():
    """启动定期清理（便捷函数）"""
    _memory_manager.schedule_cleanup()

def get_memory_stats() -> Dict[str, Any]:
    """获取内存统计信息（便捷函数）"""
    return _memory_manager.get_memory_stats()

def optimize_memory():
    """优化内存设置（便捷函数）"""
    _memory_manager.optimize_gc()
    _memory_manager.schedule_cleanup()

# 兼容性：保持原有接口
memory_manager = _memory_manager
