#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卡片组件模块
提供现代化的卡片容器组件
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from ..themes import get_theme_color, responsive_size

class ModernCard(BoxLayout):
    """现代化卡片组件"""
    
    def __init__(self, elevation=2, background_color=None, corner_radius=12, **kwargs):
        super(ModernCard, self).__init__(**kwargs)
        
        self.elevation = elevation
        self.background_color = background_color or get_theme_color('surface')
        self.corner_radius = corner_radius
        
        # 创建背景
        with self.canvas.before:
            # 阴影效果
            if elevation > 0:
                Color(*get_theme_color('shadow'))
                self.shadow = RoundedRectangle(
                    pos=(self.x + responsive_size(elevation), self.y - responsive_size(elevation)),
                    size=self.size,
                    radius=[responsive_size(corner_radius)]
                )
            
            # 背景
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[responsive_size(corner_radius)]
            )
        
        # 绑定位置和大小变化
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        """更新图形"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
            
        if hasattr(self, 'shadow') and self.elevation > 0:
            self.shadow.pos = (self.x + responsive_size(self.elevation), 
                             self.y - responsive_size(self.elevation))
            self.shadow.size = self.size
