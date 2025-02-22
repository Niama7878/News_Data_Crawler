import os
import csv
import json
from app import create_app
from app.models import NewsArticle

# 创建文件夹路径
CSV_EXPORT_FOLDER = 'exports/csv_exports'
JSON_EXPORT_FOLDER = 'exports/json_exports'

# 确保文件夹存在
os.makedirs(CSV_EXPORT_FOLDER, exist_ok=True)
os.makedirs(JSON_EXPORT_FOLDER, exist_ok=True)

# 创建 Flask 应用实例
app = create_app()

def export_data_to_csv(source, filename=None):
    if not filename:
        filename = f"{source}_news_data.csv"
    
    file_path = os.path.join(CSV_EXPORT_FOLDER, filename)

    with app.app_context():
        last_exported_id = get_last_exported_id(file_path)
        articles = NewsArticle.query.filter(NewsArticle.source == source, NewsArticle.id > last_exported_id).all()

    if not articles:
        print(f"没有新数据导出到 {file_path}.")
        return

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if os.stat(file_path).st_size == 0:
            writer.writerow(['id', 'title', 'time', 'content', 'url', 'source', 'created_at', 'updated_at'])
        for article in articles:
            writer.writerow([
                article.id,
                article.title,
                article.time.strftime('%Y-%m-%d %H:%M:%S'),
                article.content,
                article.url,
                article.source,
                article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                article.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])

    update_last_exported_id(file_path, articles[-1].id)
    print(f"数据已导出为 {file_path}")

def export_data_to_json(source, filename=None):
    if not filename:
        filename = f"{source}_news_data.json"

    file_path = os.path.join(JSON_EXPORT_FOLDER, filename)

    with app.app_context():
        last_exported_id = get_last_exported_id(file_path)
        articles = NewsArticle.query.filter(NewsArticle.source == source, NewsArticle.id > last_exported_id).all()

    if not articles:
        print(f"没有新数据导出到 {file_path}.")
        return

    if os.path.exists(file_path) and os.stat(file_path).st_size > 0:
        with open(file_path, mode='r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    new_data = [{
        'id': article.id,
        'title': article.title,
        'time': article.time.strftime('%Y-%m-%d %H:%M:%S'),
        'content': article.content,
        'url': article.url,
        'source': article.source,
        'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': article.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    } for article in articles]

    combined_data = existing_data + new_data

    with open(file_path, mode='w', encoding='utf-8') as file:
        json.dump(combined_data, file, ensure_ascii=False, indent=4)

    update_last_exported_id(file_path, articles[-1].id)
    print(f"数据已导出为 {file_path}")

def get_last_exported_id(filename):
    try:
        with open(f"{filename}.last_id", "r") as id_file:
            return int(id_file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def update_last_exported_id(filename, last_id):
    with open(f"{filename}.last_id", "w") as id_file:
        id_file.write(str(last_id))

if __name__ == "__main__":
    export_data_to_csv('bbc')
    export_data_to_json('bbc')

    export_data_to_csv('cnn')
    export_data_to_json('cnn')

    export_data_to_csv('sina')
    export_data_to_json('sina')

    export_data_to_csv('netease')
    export_data_to_json('netease')