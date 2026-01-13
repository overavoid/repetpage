import psycopg2
import os

# Подключение к базе данных
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("Ошибка: DATABASE_URL не установлена!")
    exit(1)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Создание таблицы
cur.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        date VARCHAR(10) UNIQUE NOT NULL,
        has_lesson BOOLEAN NOT NULL,
        paid BOOLEAN NOT NULL,
        payment_date VARCHAR(10),
        amount INTEGER
    );
''')

print("Таблица 'payments' создана или уже существует")

# Создание индекса для быстрого поиска по дате
cur.execute('CREATE INDEX IF NOT EXISTS idx_date ON payments(date);')

conn.commit()
cur.close()
conn.close()
print("База данных успешно инициализирована!")
