# api/update.py
import json

def load_data():
    """Загрузка данных из файла"""
    try:
        with open('/tmp/payments.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    """Сохранение данных в файл"""
    with open('/tmp/payments.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def handler(request):
    """Основная функция, которую вызывает Vercel"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return {'statusCode': 400, 'body': 'Invalid JSON'}
        
        all_data = load_data()
        date_str = data['date']
        amount = data.get('amount', 600)
        
        if data.get('has_lesson', True):
            all_data[date_str] = {
                'has_lesson': True,
                'paid': data['paid'],
                'payment_date': data.get('payment_date', ''),
                'amount': amount
            }
        else:
            if date_str in all_data:
                del all_data[date_str]
        
        save_data(all_data)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': True})
        }
    else:
        return {'statusCode': 405, 'body': 'Method Not Allowed'}
