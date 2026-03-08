#!/usr/bin/env python3
"""
日志模块 - 统一日志管理
"""

import os
import logging
from datetime import datetime
from pathlib import Path

def setup_logger(log_dir='logs', level=logging.INFO):
    """
    配置日志系统
    
    Args:
        log_dir: 日志目录
        level: 日志级别
    
    Returns:
        logger: 配置好的日志对象
    """
    # 创建日志目录
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # 日志文件名（按日期）
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 创建 logger
    logger = logging.getLogger('CryptoEmperor')
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def cleanup_old_logs(log_dir='logs', max_files=30):
    """
    清理旧日志文件
    
    Args:
        log_dir: 日志目录
        max_files: 保留最近N个文件
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    
    # 获取所有日志文件，按修改时间排序
    log_files = sorted(log_path.glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    # 删除超出数量的旧文件
    for old_file in log_files[max_files:]:
        try:
            old_file.unlink()
        except Exception as e:
            print(f"清理日志失败 {old_file}: {e}")
