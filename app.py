from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import psycopg2
import os
import json

app = Flask(__name__)

# Функция для подключения к БД
def get_db_connection():
    # Render автоматически создает переменную окружения DATABASE_URL
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

# Функции для работы с данными (заменяют работу с JSON-файлом)
def load_data(year=None, month=None):
    """Загрузка данных из базы. Если указаны год и месяц - фильтрует."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if year and month:
        month_str = f"{year}-{month:02d}"
        cur.execute('SELECT * FROM payments WHERE date LIKE %s', (f'{month_str}-%',))
    else:
        cur.execute('SELECT * FROM payments')
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # Преобразуем в словарь (как раньше был JSON)
    data = {}
    for row in rows:
        data[row[1]] = {  # row[1] = date
            'has_lesson': row[2],
            'paid': row[3],
            'payment_date': row[4] or '',
            'amount': row[5] or 600
        }
    return data

def save_payment(date, has_lesson, paid, payment_date, amount):
    """Сохранение или обновление записи о занятии"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            INSERT INTO payments (date, has_lesson, paid, payment_date, amount)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (date) DO UPDATE 
            SET has_lesson = EXCLUDED.has_lesson,
                paid = EXCLUDED.paid,
                payment_date = EXCLUDED.payment_date,
                amount = EXCLUDED.amount
        ''', (date, has_lesson, paid, payment_date, amount))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка сохранения: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def delete_payment(date):
    """Удаление записи о занятии"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('DELETE FROM payments WHERE date = %s', (date,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка удаления: {e}")
        return False
    finally:
        cur.close()
        conn.close()

# HTML шаблон (ваш исходный HTML - ВСТАВЬТЕ СЮДА ВЕСЬ ВАШ HTML КОД)
# Я сократил его для примера, но вам нужно вставить ВЕСЬ ваш HTML из предыдущей версии
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Учёт оплаты занятий</title>
    <style>
        /* ВАШ ПОЛНЫЙ CSS КОД */
    </style>
</head>
<body>
    <!-- ВАШ ПОЛНЫЙ HTML КОД -->
    <script>
        // ВАШ ПОЛНЫЙ JAVASCRIPT КОД
        // ВАЖНО: в функциях savePayment(), markLesson(), removeLesson()
        // оставьте пути как есть: fetch('/update', ...)
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    # Получаем год и месяц из параметров или используем текущие
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    # Загружаем данные из БД
    data = load_data(year, month)
    
    # Генерируем календарь (нужна функция generate_calendar - она у вас уже есть)
    # Для простоты предположим, что она есть
    cal = generate_calendar(year, month)
    
    # Статистика за месяц
    stats = {'lesson': 0, 'paid': 0, 'not_paid': 0, 'income': 0, 'debt': 0, 'balance': 0}
    
    for date_str, day_data in data.items():
        if day_data.get('has_lesson', False):
            stats['lesson'] += 1
            amount = day_data.get('amount', 0)
            if day_data.get('paid', False):
                stats['paid'] += 1
                stats['income'] += amount
            else:
                stats['not_paid'] += 1
                stats['debt'] += amount
    
    stats['balance'] = stats['income'] - stats['debt']
    
    # Общая статистика по всем данным
    all_data = load_data()
    total_income = 0
    total_debt = 0
    
    for date_str, day_data in all_data.items():
        if day_data.get('has_lesson', False):
            amount = day_data.get('amount', 0)
            if day_data.get('paid', False):
                total_income += amount
            else:
                total_debt += amount
    
    total_balance = total_income - total_debt
    
    # Текущая дата для отображения
    current_date = datetime(year, month, 1).strftime("%B %Y").title()
    # ... перевод на русский ...
    
    return render_template_string(
        HTML_TEMPLATE,
        year=year,
        month=f"{month:02d}",
        calendar=cal,
        data=data,
        stats=stats,
        current_date=current_date,
        today=datetime.now(),
        total_balance=total_balance
    )

@app.route('/update', methods=['POST'])
def update_payment():
    """Обновление информации об оплате"""
    data = request.get_json()
    
    if data.get('has_lesson', True):
        success = save_payment(
            date=data['date'],
            has_lesson=True,
            paid=data['paid'],
            payment_date=data.get('payment_date', ''),
            amount=data.get('amount', 600)
        )
    else:
        success = delete_payment(data['date'])
    
    return jsonify({'success': success})

# Функция generate_calendar должна быть тут
def generate_calendar(year, month):
    import calendar
    cal = calendar.monthcalendar(year, month)
    calendar_list = []
    for week in cal:
        for day in week:
            calendar_list.append(day)
    return calendar_list

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
