from flask import Blueprint, render_template, request
from markupsafe import escape  # 用于防止 XSS 攻击
from app.models import NewsArticle
from sqlalchemy import func

# 创建蓝图对象
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # 获取搜索查询参数并去除空格，防止 XSS 攻击
    search_query = escape(request.args.get('search', '').strip())
    # 获取当前页码，默认为 1
    page = max(request.args.get('page', 1, type=int), 1)
    # 每页显示的文章数量
    articles_per_page = 10

    # 查询文章逻辑
    articles_query = NewsArticle.query
    if search_query:
        articles_query = articles_query.filter(
            NewsArticle.title.contains(search_query) |
            NewsArticle.content.contains(search_query) |
            NewsArticle.source.contains(search_query)
        )

    # 分页处理
    pagination = articles_query.paginate(page=page, per_page=articles_per_page, error_out=False)
    articles = pagination.items

    # 获取趋势图的数据，按日期分组统计文章数量
    trend_data = NewsArticle.query.with_entities(
        func.strftime('%Y-%m-%d', NewsArticle.time).label('date'),  # 使用 strftime 函数格式化日期
        func.count('*').label('count')
    ).group_by(func.strftime('%Y-%m-%d', NewsArticle.time)).order_by('date').all()

    # 如果获取到趋势数据，提取日期和数量
    trend_dates, trend_counts = zip(*[
        (data.date, data.count) for data in trend_data
    ]) if trend_data else ([], [])

    # 渲染模板并返回响应
    return render_template(
        'index.html',
        articles=articles,
        trend_dates=trend_dates,
        trend_counts=trend_counts,
        search_query=search_query,
        pagination=pagination,
    )

@bp.route('/article/<int:article_id>')
def article_details(article_id):
    # 获取指定 ID 的文章，若不存在则返回 404
    article = NewsArticle.query.get_or_404(article_id)
    # 渲染文章详情页面并返回响应
    return render_template('article_details.html', article=article)