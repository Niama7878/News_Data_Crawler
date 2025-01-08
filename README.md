# 新闻仪表盘项目

## 项目概述

这个项目是一个新闻仪表盘，旨在从多个新闻来源抓取新闻数据并展示。用户可以查看新闻列表、趋势图以及新闻的详细内容。项目还支持通过定时任务自动抓取新闻，并导出新闻数据为 CSV 或 JSON 格式。此外，用户可以通过搜索功能查找相关的新闻。

## 功能

- **新闻数据抓取**：从 BBC、CNN、网易、新浪等新闻来源定时抓取新闻。
- **新闻展示**：展示新闻列表和新闻趋势图。
- **新闻搜索**：用户可以通过输入关键词搜索新闻。搜索结果将根据关键词匹配标题、内容等字段。
- **新闻分页**：在新闻列表页面提供分页功能，便于用户浏览大量新闻。
- **新闻详情**：用户可以查看每条新闻的详细内容。
- **趋势图**：使用 ECharts 绘制新闻趋势图，展示新闻数量随时间变化的趋势。
- **数据导出**：支持将新闻数据导出为 CSV 和 JSON 格式，确保每次导出时只包含新增数据。

## 安装依赖

1. 克隆项目并进入项目目录。
2. 使用以下命令安装所需的 Python 库：

   ```bash
   pip install requests beautifulsoup4 selenium flask Flask-SQLAlchemy Flask-Migrate apscheduler

## 使用教程

[YouTube](https://youtu.be/NNNc-X5SoCs) [Bilibili](https://www.bilibili.com/video/BV1JBrVYSECM)