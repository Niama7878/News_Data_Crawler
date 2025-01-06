import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from app import create_app, db
from app.models import NewsArticle
import re

# 时间解析函数
def parse_relative_time(relative_time):
    """将相对时间转换为绝对时间"""
    now = datetime.now().replace(microsecond=0)

    match = re.search(r'(\d+)\s*(minute|hour|day|week)s?\s*ago', relative_time)
    if match:
        value = int(match.group(1))
        unit = match.group(2)

        if unit == 'minute':
            return now - timedelta(minutes=value)
        elif unit == 'hour':
            return now - timedelta(hours=value)
        elif unit == 'day':
            return now - timedelta(days=value)
        elif unit == 'week':
            return now - timedelta(weeks=value)

    return now

# Flask 应用和数据库初始化
app = create_app()

# 目标网址
base_url = "https://edition.cnn.com/"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, "html.parser")

# 筛选出文章链接
unique_urls = set()
for parent_class in ['zone__items layout--5-4-3', 'zone__items layout--wide-left-balanced-2']:
    parent_div = soup.find('div', class_=parent_class)
    if parent_div:
        a_tags = parent_div.find_all('a', href=True)
        for a_tag in a_tags:
            href = a_tag['href']
            if href.endswith('/index.html'):
                unique_urls.add(base_url.rstrip('/') + href)

# 处理每个文章链接
for url in unique_urls:
    # 使用 Flask 上下文检查链接是否存在
    with app.app_context():
        existing_article = NewsArticle.query.filter_by(url=url).first()
        if existing_article:
            print(f"链接已存在，跳过: {url}")
            continue

    article_response = requests.get(url)
    article_soup = BeautifulSoup(article_response.text, "html.parser")

    # 提取文章标题、时间和内容
    title = article_soup.find('h1', class_='headline__text inline-placeholder vossi-headline-text')
    time_tag = article_soup.find('div', class_='timestamp vossi-timestamp')
    contents = article_soup.find_all('p', class_='paragraph inline-placeholder vossi-paragraph')

    # 确保标题、时间和内容都不为空
    if title and time_tag and contents:
        # 转换时间
        relative_time = time_tag.text.strip() if time_tag else ""
        absolute_time = parse_relative_time(relative_time)

        # 使用 Flask 上下文将数据保存到数据库
        with app.app_context():
            article = NewsArticle(
                title=title.text.strip() if title else "No title",
                time=absolute_time,
                content=' '.join([content.text.strip() for content in contents]),
                url=url,
                source="cnn"  # 新增字段，表示来源
            )
            db.session.add(article)
            db.session.commit()