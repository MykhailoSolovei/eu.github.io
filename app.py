from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('forum.db')
    conn.row_factory = sqlite3.Row
    return conn

# Главная страница со списком тем
@app.route('/')
def index():
    conn = get_db_connection()
    topics = conn.execute('SELECT * FROM topics').fetchall()
    conn.close()
    return render_template('index.html', topics=topics)

# Страница создания новой темы
@app.route('/create_topic', methods=('GET', 'POST'))
def create_topic():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        # Добавление новой темы в базу данных
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO topics (title, author, created_at) VALUES (?, ?, ?)', 
            (title, author, datetime.now())
        )
        conn.commit()
        conn.close()

        # Возврат на главную страницу после создания темы
        return redirect('/')
    
    # Отображение страницы с формой для создания новой темы
    return render_template('create_topic.html')

# Страница темы
@app.route('/topic/<int:topic_id>')
def topic(topic_id):
    conn = get_db_connection()
    topic = conn.execute('SELECT * FROM topics WHERE id = ?', (topic_id,)).fetchone()
    posts = conn.execute('SELECT * FROM posts WHERE topic_id = ?', (topic_id,)).fetchall()
    conn.close()
    return render_template('topic.html', topic=topic, posts=posts)

@app.route('/clear_data', methods=['POST'])
def clear_data():
    conn = get_db_connection()
    # Удаляем все комментарии
    conn.execute('DELETE FROM posts')
    # Удаляем все темы
    conn.execute('DELETE FROM topics')
    conn.commit()
    conn.close()
    
    return redirect('/')


# Добавление нового сообщения в тему
@app.route('/topic/<int:topic_id>/add_post', methods=('POST',))
def add_post(topic_id):
    author = request.form['author']
    content = request.form['content']
    
    # Получаем текущее время
    created_at = datetime.now()

    # Добавление нового сообщения в базу данных
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO posts (topic_id, author, content, created_at) VALUES (?, ?, ?, ?)', 
        (topic_id, author, content, created_at)
    )
    conn.commit()
    conn.close()

    # Возврат на страницу темы
    return redirect(f'/topic/{topic_id}')

# Запуск сервера
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)

