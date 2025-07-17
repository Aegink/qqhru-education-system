#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源文件生成脚本
用于在构建过程中自动生成应用图标和启动画面
"""

import os
import sys
from pathlib import Path

def create_default_icon():
    """创建默认应用图标"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("警告: PIL/Pillow未安装，无法生成图标")
        return False
    
    # 确保assets目录存在
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # 创建512x512的图标
    size = 512
    img = Image.new('RGBA', (size, size), (33, 150, 243, 255))  # Material Blue
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的图标设计
    # 外圆
    margin = 50
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(255, 255, 255, 255), outline=(33, 150, 243, 255), width=8)
    
    # 内部文字区域
    text_margin = 120
    draw.rectangle([text_margin, text_margin, size-text_margin, size-text_margin],
                  fill=(33, 150, 243, 255))
    
    # 添加文字 "教务"
    try:
        # 尝试使用系统字体
        font_size = 120
        try:
            # Windows
            font = ImageFont.truetype("msyh.ttc", font_size)
        except:
            try:
                # Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                # 默认字体
                font = ImageFont.load_default()
        
        text = "教务"
        # 计算文字位置使其居中
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 20
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    except Exception as e:
        print(f"添加文字时出错: {e}")
        # 如果文字添加失败，绘制简单的几何图形
        center = size // 2
        draw.ellipse([center-40, center-40, center+40, center+40], 
                    fill=(255, 255, 255, 255))
    
    # 保存图标
    icon_path = assets_dir / "icon.png"
    img.save(icon_path, "PNG")
    print(f"✓ 已创建应用图标: {icon_path}")
    return True

def create_default_presplash():
    """创建默认启动画面"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("警告: PIL/Pillow未安装，无法生成启动画面")
        return False
    
    # 确保assets目录存在
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # 创建启动画面 (推荐尺寸: 1280x1920 或类似比例)
    width, height = 1280, 1920
    img = Image.new('RGB', (width, height), (33, 150, 243))  # Material Blue背景
    draw = ImageDraw.Draw(img)
    
    # 绘制中央logo区域
    logo_size = 300
    logo_x = (width - logo_size) // 2
    logo_y = (height - logo_size) // 2 - 200
    
    # 绘制logo背景圆
    draw.ellipse([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size],
                fill=(255, 255, 255, 255))
    
    # 添加应用名称
    try:
        font_size = 60
        try:
            font = ImageFont.truetype("msyh.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # 主标题
        title = "齐齐哈尔大学"
        bbox = draw.textbbox((0, 0), title, font=font)
        title_width = bbox[2] - bbox[0]
        title_x = (width - title_width) // 2
        title_y = logo_y + logo_size + 80
        draw.text((title_x, title_y), title, fill=(255, 255, 255), font=font)
        
        # 副标题
        subtitle = "教务系统查询工具"
        bbox = draw.textbbox((0, 0), subtitle, font=font)
        subtitle_width = bbox[2] - bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        subtitle_y = title_y + 80
        draw.text((subtitle_x, subtitle_y), subtitle, fill=(255, 255, 255), font=font)
        
        # 版本信息
        version_font_size = 40
        try:
            version_font = ImageFont.truetype("msyh.ttc", version_font_size)
        except:
            version_font = font
        
        version = "v2.0.0"
        bbox = draw.textbbox((0, 0), version, font=version_font)
        version_width = bbox[2] - bbox[0]
        version_x = (width - version_width) // 2
        version_y = subtitle_y + 120
        draw.text((version_x, version_y), version, fill=(200, 200, 200), font=version_font)
        
    except Exception as e:
        print(f"添加文字时出错: {e}")
    
    # 保存启动画面
    presplash_path = assets_dir / "presplash.png"
    img.save(presplash_path, "PNG")
    print(f"✓ 已创建启动画面: {presplash_path}")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("齐齐哈尔大学教务系统查询工具 - 资源生成器")
    print("=" * 50)
    
    success_count = 0
    
    # 检查是否需要创建图标
    if not os.path.exists("assets/icon.png"):
        print("正在创建应用图标...")
        if create_default_icon():
            success_count += 1
    else:
        print("✓ 应用图标已存在")
        success_count += 1
    
    # 检查是否需要创建启动画面
    if not os.path.exists("assets/presplash.png"):
        print("正在创建启动画面...")
        if create_default_presplash():
            success_count += 1
    else:
        print("✓ 启动画面已存在")
        success_count += 1
    
    print("=" * 50)
    if success_count == 2:
        print("✓ 所有资源文件已准备就绪")
        return 0
    else:
        print("⚠ 部分资源文件创建失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
