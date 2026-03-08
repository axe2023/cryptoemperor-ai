#!/usr/bin/env python3
"""
定时任务调度器 - 自动运行信号扫描和日报生成
"""

import schedule
import time
from datetime import datetime
import subprocess
import os

class Scheduler:
    """任务调度器"""
    
    def __init__(self, config):
        """
        初始化调度器
        
        Args:
            config: 调度配置字典
        """
        self.config = config
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
    
    def run_scan(self):
        """运行信号扫描"""
        print(f"[{datetime.now()}] 开始运行信号扫描...")
        try:
            result = subprocess.run(
                ['python3', 'main.py'],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"[{datetime.now()}] ✅ 信号扫描完成")
            else:
                print(f"[{datetime.now()}] ❌ 信号扫描失败: {result.stderr}")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ 运行异常: {e}")
    
    def run_daily_report(self):
        """生成并推送日报"""
        print(f"[{datetime.now()}] 开始生成日报...")
        try:
            # 运行主程序（会自动生成日报）
            result = subprocess.run(
                ['python3', 'main.py'],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"[{datetime.now()}] ✅ 日报生成完成")
                
                # 推送到 Telegram
                if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
                    from telegram_bot import TelegramBot
                    bot = TelegramBot()
                    report_file = f"reports/report_{datetime.now().strftime('%Y-%m-%d')}.md"
                    bot.send_daily_report(report_file)
            else:
                print(f"[{datetime.now()}] ❌ 日报生成失败: {result.stderr}")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ 运行异常: {e}")
    
    def setup_schedules(self):
        """设置定时任务"""
        # 信号扫描任务
        scan_times = self.config.get('scan_times', ['09:00', '12:00', '15:00', '18:00', '21:00'])
        for scan_time in scan_times:
            schedule.every().day.at(scan_time).do(self.run_scan)
            print(f"✅ 已设置信号扫描任务: 每天 {scan_time}")
        
        # 日报任务
        report_time = self.config.get('report_time', '22:00')
        schedule.every().day.at(report_time).do(self.run_daily_report)
        print(f"✅ 已设置日报任务: 每天 {report_time}")
    
    def run(self):
        """启动调度器"""
        print("=" * 60)
        print("CryptoEmperor AI 调度器启动")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.setup_schedules()
        
        print("\n等待任务执行...")
        print("按 Ctrl+C 停止调度器\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            print("\n\n调度器已停止")

def main():
    """主函数"""
    # 默认配置
    config = {
        'scan_times': ['09:00', '12:00', '15:00', '18:00', '21:00'],  # 每天5次扫描
        'report_time': '22:00'  # 每天22:00生成日报
    }
    
    scheduler = Scheduler(config)
    scheduler.run()

if __name__ == '__main__':
    main()
