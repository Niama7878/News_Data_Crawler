from app import db
from datetime import datetime, timezone

def now_without_microseconds():
    """返回当前 UTC 时间，不带毫秒。"""
    return datetime.now(timezone.utc).replace(microsecond=0)

class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    time = db.Column(db.DateTime, nullable=False, index=True, default=now_without_microseconds)
    content = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True, index=True)
    source = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=now_without_microseconds, nullable=False)
    updated_at = db.Column(db.DateTime, default=now_without_microseconds, onupdate=now_without_microseconds, nullable=False)

    def __repr__(self):
        return f"<NewsArticle {self.title} from {self.source} at {self.time.strftime('%Y-%m-%d %H:%M:%S')}>"