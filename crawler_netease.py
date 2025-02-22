from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from app import create_app, db
from app.models import NewsArticle
import re

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument('--headless')  # 启用无头模式
chrome_options.add_argument('--disable-gpu')  # 禁用GPU硬件加速
chrome_options.add_argument('--no-sandbox')  # 提高兼容性
chrome_options.add_argument('--disable-extensions')  # 禁用扩展
chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 禁用图片加载

# 时间解析函数
def parse_relative_time(relative_time):
    """将相对时间转换为绝对时间"""
    now = datetime.now().replace(microsecond=0)  # 当前时间去掉微秒
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

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)

# 打开网易新闻首页
base_url = "https://news.163.com/"
driver.get(base_url)

# 初始化 Flask 应用
app = create_app()

try:
    # 等待页面加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "js_top_news"))
    )

    # 获取页面HTML
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # 筛选出文章链接
    parent_div = soup.find('div', {'id': 'js_top_news'})
    unique_urls = set()

    if parent_div:
        a_tags = parent_div.find_all('a', href=True)
        for a_tag in a_tags:
            href = a_tag['href']
            if '/news/article/' in href:  # 检查链接中是否包含 /news/article/
                unique_urls.add(href)  # 将链接加入集合

    # 遍历每个文章链接并提取内容
    for url in unique_urls:
        # 使用 Flask 上下文检查链接是否存在
        with app.app_context():
            existing_article = NewsArticle.query.filter_by(url=url).first()
            if existing_article:
                print(f"链接已存在，跳过: {url}")
                continue

        driver.get(url)  # 导航到文章页面

        # 等待文章内容加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.post_title'))
        )

        # 获取文章页面HTML
        article_html = driver.page_source
        article_soup = BeautifulSoup(article_html, "html.parser")

        # 提取标题、时间和内容
        title = article_soup.find('h1', class_='post_title')
        time_tag = article_soup.find('div', class_='post_info')
        content_div = article_soup.find('div', class_='post_body')

        # 确保标题、时间和内容都不为空
        if title and time_tag and content_div:
            # 处理文章内容和时间
            title_text = title.text.strip() if title else "No Title"
            time_text = time_tag.text.strip() if time_tag else "Unknown Time"
            content_text = ' '.join(
                [p.text.strip() for p in content_div.find_all('p')] if content_div else []
            )

            # 解析时间字段
            absolute_time = parse_relative_time(time_text)

            # 使用 Flask 上下文将数据保存到数据库
            with app.app_context():
                # 保存新文章
                article = NewsArticle(
                    title=title_text,
                    time=absolute_time,
                    content=content_text,
                    url=url,
                    source="netease"  # 来源为网易
                )
                db.session.add(article)
                db.session.commit()

finally:
    driver.quit()  # 关闭浏览器