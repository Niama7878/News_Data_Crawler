from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import subprocess
import os
import sys
from datetime import datetime
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 设置定时任务
def run_spider(script_name):
    try:
        # 获取当前文件（app.py所在文件）的上一级目录
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # 拼接目标脚本的完整路径
        script_path = os.path.join(base_path, script_name)
        
        # 检查目标脚本是否存在
        if not os.path.isfile(script_path):
            raise FileNotFoundError(f"Script {script_name} does not exist at {script_path}")
        
        # 调试信息
        logging.info(f"Resolved path for {script_name}: {script_path}")
        
        # 使用 subprocess 执行脚本
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        
        # 打印脚本执行的输出和错误信息
        if result.returncode == 0:
            logging.info(f"Successfully ran {script_name} at {datetime.now()}")
        else:
            logging.error(f"Error running {script_name}: {result.stderr}")
    
    except Exception as e:
        logging.error(f"An error occurred while running {script_name}: {e}")

# 定义调度任务
def setup_scheduler():
    scheduler = BackgroundScheduler()

    # 初始化运行所有任务
    for script in ['crawler_bbc.py', 'crawler_cnn.py', 'crawler_netease.py', 'crawler_sina.py', 'data_export.py']:
        run_spider(script)

    # 定时任务
    scheduler.add_job(lambda: run_spider('crawler_bbc.py'), 'cron', minute=0)
    scheduler.add_job(lambda: run_spider('crawler_cnn.py'), 'cron', minute=0)
    scheduler.add_job(lambda: run_spider('crawler_netease.py'), 'cron', minute=0)
    scheduler.add_job(lambda: run_spider('crawler_sina.py'), 'cron', minute=0)
    scheduler.add_job(lambda: run_spider('data_export.py'), 'cron', minute=0)

    # 启动调度器
    scheduler.start()

    # 监听任务事件
    def job_listener(event):
        if event.exception:
            logging.error(f"Job {event.job_id} failed")
        else:
            logging.info(f"Job {event.job_id} completed successfully")

    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # 在 Flask 应用关闭时优雅地关闭调度器
    import atexit
    atexit.register(lambda: scheduler.shutdown())

    logging.info("Scheduler setup complete.")

# 在应用启动时设置定时任务
setup_scheduler()

if __name__ == '__main__':
    app.run(debug=True)