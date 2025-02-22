from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 初始化数据库和迁移
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # 加载配置

    # 初始化数据库和迁移工具
    db.init_app(app)
    migrate.init_app(app, db)

    # 导入 routes 中的 bp 蓝图，并注册蓝图
    from app.routes import bp  # 从 app.routes 导入 bp
    app.register_blueprint(bp)  # 注册蓝图

    return app