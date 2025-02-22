from app import create_app
from app.app import setup_scheduler 

# 创建 Flask 应用实例
app = create_app()

# 在启动 Flask 应用后调用调度器
setup_scheduler()

if __name__ == '__main__':
    app.run(debug=True)