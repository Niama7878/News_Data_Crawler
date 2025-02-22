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
    # 获取当前时间并移除微秒
    now = datetime.now().replace(microsecond=0)

    # 使用正则表达式解析相对时间
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

    # 无法解析则返回当前时间
    return now

# Flask 应用和数据库初始化
app = create_app()

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)

# 打开 BBC 网站
url = "https://www.bbc.com/"
driver.get(url)

try:
    # 等待页面的某个元素加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="first-grid"]'))
    )

    # 获取页面的HTML
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # 筛选出文章链接
    parent_divs = soup.find_all('div', {'data-testid': ['first-grid', 'second-grid', 'westminster-article']})
    filtered_links = set()

    for parent_selector in parent_divs:
        a_tags = parent_selector.find_all('a')
        for a_tag in a_tags:
            href = a_tag.get('href', '')
            if href.startswith('/news/articles/'):
                filtered_links.add('https://www.bbc.com' + href)

    # 处理每个文章链接
    for link in filtered_links:
        # 使用 Flask 上下文检查链接是否存在
        with app.app_context():
            existing_article = NewsArticle.query.filter_by(url=link).first()
            if existing_article:
                print(f"链接已存在，跳过: {link}")
                continue

        driver.get(link)  # 导航到文章页面

        # 等待文章内容加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.sc-518485e5-0.bWszMR'))
        )

        # 获取文章页面的HTML
        article_html = driver.page_source
        article_soup = BeautifulSoup(article_html, "html.parser")

        # 提取文章标题、时间和内容
        title = article_soup.find('h1', class_='sc-518485e5-0 bWszMR')
        time_tag = article_soup.find('time', class_='sc-2b5e3b35-2 fkLXLN')
        contents = article_soup.find_all('p', class_='sc-eb7bd5f6-0 fYAfXe')

        # 确保标题、时间和内容都不为空
        if title and time_tag and contents:
            # 转换时间
            relative_time = time_tag.text.strip() if time_tag else ""
            absolute_time = parse_relative_time(relative_time)

            # 使用 Flask 上下文将数据保存到数据库
            with app.app_context():
                article = NewsArticle(
                    title=title.text.strip() if title else "No title",
                    time=absolute_time,  # 使用 DateTime 类型
                    content=' '.join([content.text.strip() for content in contents]),
                    url=link,
                    source="bbc"  # 新增字段，表示来源
                )
                db.session.add(article)
                db.session.commit()

finally:
    driver.quit()  # 关闭浏览器