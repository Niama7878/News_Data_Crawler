class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///news_data.db'  # 配置数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用 SQLAlchemy 的修改追踪