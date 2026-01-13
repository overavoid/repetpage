from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

# Файл для хранения данных
DATA_FILE = 'payments.json'

# HTML шаблон
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Отслеживание оплаты занятий</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .container { 
            display: flex; 
            gap: 30px; 
            flex-wrap: wrap;
        }
        .calendar { 
            flex: 1; 
            min-width: 350px;
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .controls { 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            margin-bottom: 25px;
        }
        .month-nav {
            display: flex;
            gap: 10px;
        }
        .month-nav button {
            padding: 8px 15px;
            border: none;
            background: #007bff;
            color: white;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        .month-nav button:hover {
            background: #0056b3;
            transform: translateY(-2px);
        }
        .days-grid { 
            display: grid; 
            grid-template-columns: repeat(7, 1fr);
            gap: 8px;
            margin-bottom: 25px;
        }
        .day-header { 
            text-align: center; 
            padding: 12px; 
            font-weight: bold;
            background: #4a6fa5;
            color: white;
            border-radius: 8px;
            font-size: 14px;
        }
        .day { 
            padding: 12px; 
            text-align: center; 
            border: 2px solid #e0e0e0;
            cursor: pointer;
            background: white;
            transition: all 0.3s;
            border-radius: 8px;
            font-weight: bold;
            position: relative;
            min-height: 60px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .day:hover { 
            background: #f0f8ff; 
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .day.today { 
            background: #e3f2fd; 
            border: 2px solid #2196f3;
            box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
        }
        .day.lesson { 
            background: #fff3cd; 
            border: 2px solid #ffc107;
            box-shadow: 0 0 0 2px rgba(255, 193, 7, 0.2);
        }
        .day.paid { 
            background: #d4edda; 
            border: 2px solid #28a745;
            box-shadow: 0 0 0 2px rgba(40, 167, 69, 0.2);
        }
        .day.not-paid { 
            background: #f8d7da; 
            border: 2px solid #dc3545;
            box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.2);
        }
        .day-header, .day {
            min-height: 55px;
        }
        .day-amount {
            font-size: 11px;
            margin-top: 3px;
            font-weight: normal;
            padding: 2px 5px;
            border-radius: 3px;
            background: rgba(255,255,255,0.8);
        }
        .day.paid .day-amount {
            background: rgba(212, 237, 218, 0.9);
            color: #155724;
        }
        .day.not-paid .day-amount {
            background: rgba(248, 215, 218, 0.9);
            color: #721c24;
        }
        .day.lesson .day-amount {
            background: rgba(255, 243, 205, 0.9);
            color: #856404;
        }
        .details { 
            flex: 1; 
            min-width: 350px;
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .selected-date { 
            font-size: 26px; 
            margin-bottom: 25px;
            color: #2c3e50;
            font-weight: bold;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }
        .payment-controls {
            margin-bottom: 25px;
        }
        .switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        .switch input { 
            opacity: 0;
            width: 0;
            height: 0;
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
        }
        input:checked + .slider {
            background-color: #28a745;
        }
        input:checked + .slider:before {
            transform: translateX(26px);
        }
        .slider.round {
            border-radius: 34px;
        }
        .slider.round:before {
            border-radius: 50%;
        }
        .payment-status {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .payment-date {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        .stats {
            margin-top: 25px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .stats h3 {
            margin-bottom: 15px;
            font-size: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stats p {
            margin: 8px 0;
            font-size: 16px;
            display: flex;
            justify-content: space-between;
        }
        .month-year {
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            flex-grow: 1;
        }
        .empty-day {
            background: transparent;
            border: none;
            cursor: default;
        }
        .empty-day:hover {
            background: transparent;
            transform: none;
            box-shadow: none;
        }
        .status-text {
            font-weight: bold;
            font-size: 18px;
        }
        .paid-text { color: #28a745; }
        .not-paid-text { color: #dc3545; }
        .lesson-text { color: #ffc107; }
        button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
            margin: 5px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .lesson-controls {
            margin-bottom: 20px;
        }
        .lesson-toggle {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .controls-row {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .delete-btn {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .delete-btn:hover {
            background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
        }
        .lesson-btn {
            background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
            color: #212529;
        }
        .lesson-btn:hover {
            background: linear-gradient(135deg, #fda085 0%, #f6d365 100%);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 25px;
            text-align: center;
            font-size: 32px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .amount-selector {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #4a6fa5;
        }
        .amount-options {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        .amount-option {
            padding: 12px 20px;
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
            text-align: center;
            flex: 1;
            min-width: 120px;
        }
        .amount-option:hover {
            border-color: #007bff;
            transform: translateY(-2px);
        }
        .amount-option.selected {
            border-color: #28a745;
            background: #d4edda;
            color: #155724;
        }
        .custom-amount {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        .amount-display {
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
        }
        .income-amount {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            color: #155724;
            border: 2px solid #28a745;
        }
        .debt-amount {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            color: #721c24;
            border: 2px solid #dc3545;
        }
        .financial-summary {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-top: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .financial-summary h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .financial-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
            font-size: 17px;
        }
        .financial-item:last-child {
            border-bottom: none;
            font-weight: bold;
            font-size: 20px;
            color: #2c3e50;
            margin-top: 10px;
            padding-top: 20px;
            border-top: 2px solid #eee;
        }
        .amount-positive {
            color: #28a745;
            font-weight: bold;
        }
        .amount-negative {
            color: #dc3545;
            font-weight: bold;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin-left: 10px;
        }
        .badge-paid {
            background: #d4edda;
            color: #155724;
        }
        .badge-debt {
            background: #f8d7da;
            color: #721c24;
        }
        .badge-lesson {
            background: #fff3cd;
            color: #856404;
        }
        .summary-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .summary-label {
            font-weight: 600;
            color: #495057;
        }
        .summary-value {
            font-weight: bold;
            font-size: 18px;
        }
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 20px;
        }
        .total-display {
            background: linear-gradient(135deg, #4a6fa5 0%, #2c3e50 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            min-width: 250px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .total-amount {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .total-label {
            font-size: 14px;
            opacity: 0.9;
        }
        @media (max-width: 1200px) {
            .container {
                flex-direction: column;
            }
            .calendar, .details {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header-container">
        <h1>📊 Учёт оплаты занятий</h1>
        <div class="total-display">
            <div class="total-label">БАЛАНС</div>
            <div class="total-amount">{{ total_balance }} ₽</div>
            <div style="font-size: 12px; opacity: 0.8;">Доход - Долги</div>
        </div>
    </div>

    <div class="container">
        <div class="calendar">
            <div class="controls">
                <div class="month-nav">
                    <button onclick="changeMonth(-1)">← Предыдущий</button>
                    <span class="month-year" id="current-month">{{ current_date }}</span>
                    <button onclick="changeMonth(1)">Следующий →</button>
                </div>
            </div>
            <div class="days-grid">
                <div class="day-header">Пн</div>
                <div class="day-header">Вт</div>
                <div class="day-header">Ср</div>
                <div class="day-header">Чт</div>
                <div class="day-header">Пт</div>
                <div class="day-header">Сб</div>
                <div class="day-header">Вс</div>
                {% for day in calendar %}
                    {% if day == 0 %}
                        <div class="day empty-day"></div>
                    {% else %}
                        {% set date_str = (year ~ '-' ~ month ~ '-' ~ day)|replace(' ', '') %}
                        {% set day_data = data.get(date_str, {}) %}
                        {% set has_lesson = day_data.get('has_lesson', False) %}
                        {% set is_paid = day_data.get('paid', False) %}
                        {% set amount = day_data.get('amount', 0) %}

                        <div class="day 
                            {% if day == today.day and month == today.month and year == today.year %}today{% endif %}
                            {% if has_lesson and is_paid %}paid{% endif %}
                            {% if has_lesson and not is_paid %}not-paid{% endif %}
                            {% if has_lesson %}lesson{% endif %}"
                            onclick="selectDate('{{ year }}-{{ month }}-{{ day }}')"
                            title="{% if has_lesson %}{% if is_paid %}Оплачено{% else %}Долг{% endif %}{% endif %}">
                            {{ day }}
                            {% if has_lesson and amount > 0 %}
                                <div class="day-amount">{{ amount }} ₽</div>
                            {% endif %}
                        </div>
                    {% endif %}
                {% endfor %}
            </div>
            <div class="stats">
                <h3>📈 Статистика за месяц</h3>
                <div class="summary-item">
                    <span class="summary-label">Занятий проведено:</span>
                    <span class="summary-value">{{ stats.lesson }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Оплачено занятий:</span>
                    <span class="summary-value" style="color: #28a745;">{{ stats.paid }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Не оплачено:</span>
                    <span class="summary-value" style="color: #dc3545;">{{ stats.not_paid }}</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Доход:</span>
                    <span class="summary-value" style="color: #28a745;">{{ stats.income }} ₽</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Долги:</span>
                    <span class="summary-value" style="color: #dc3545;">{{ stats.debt }} ₽</span>
                </div>
            </div>
        </div>

        <div class="details">
            <div class="selected-date" id="selected-date">Выберите дату</div>
            <div id="payment-info">
                <p style="color: #6c757d; font-style: italic;">Выберите день в календаре для управления занятиями и оплатой.</p>
            </div>
        </div>
    </div>

    <div class="financial-summary">
        <h3>💼 Финансовый отчёт за {{ current_date }}</h3>
        <div class="financial-item">
            <span>Общий доход (оплаченные занятия):</span>
            <span class="amount-positive">+{{ stats.income }} ₽</span>
        </div>
        <div class="financial-item">
            <span>Общая сумма долгов:</span>
            <span class="amount-negative">-{{ stats.debt }} ₽</span>
        </div>
        <div class="financial-item">
            <span>Итоговый баланс:</span>
            <span class="{% if stats.balance >= 0 %}amount-positive{% else %}amount-negative{% endif %}">
                {{ stats.balance }} ₽
            </span>
        </div>
    </div>

    <script>
        let currentDate = new Date('{{ year }}-{{ month }}-01');
        let selectedDate = null;
        let paymentData = {{ data|tojson|safe }};
        let selectedAmount = 600;

        function changeMonth(delta) {
            currentDate.setMonth(currentDate.getMonth() + delta);
            const year = currentDate.getFullYear();
            const month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
            window.location.href = `/?year=${year}&month=${month}`;
        }

        function selectDate(date) {
            selectedDate = date;
            document.getElementById('selected-date').textContent = formatDate(date);

            const dayData = paymentData[date] || { has_lesson: false, paid: false, payment_date: '', amount: 0 };

            let html = '';

            if (dayData.has_lesson) {
                // День с занятием
                if (dayData.paid) {
                    // Оплачено
                    html = `
                        <div class="lesson-controls">
                            <div class="amount-display income-amount">
                                +${dayData.amount} ₽
                                <div style="font-size: 16px; margin-top: 5px;">✅ Оплачено</div>
                            </div>

                            <div class="payment-status">
                                <span class="status-text paid-text" style="font-size: 20px;">
                                    Занятие оплачено
                                </span>
                            </div>

                            <div class="amount-selector">
                                <label style="font-weight: bold; display: block; margin-bottom: 10px;">Сумма занятия:</label>
                                <div class="amount-options">
                                    <div class="amount-option ${dayData.amount == 600 ? 'selected' : ''}" onclick="selectAmountOption(600)">600 ₽</div>
                                    <div class="amount-option ${dayData.amount == 1500 ? 'selected' : ''}" onclick="selectAmountOption(1500)">1500 ₽</div>
                                    <div class="amount-option ${dayData.amount != 600 && dayData.amount != 1500 ? 'selected' : ''}" 
                                         onclick="showCustomAmount()">Другая сумма</div>
                                </div>
                                ${dayData.amount != 600 && dayData.amount != 1500 ? `
                                    <input type="number" id="custom-amount" class="custom-amount" 
                                           value="${dayData.amount}" placeholder="Введите сумму" onchange="updateCustomAmount(this.value)">
                                ` : ''}
                            </div>

                            <div>
                                <label style="font-weight: bold; display: block; margin-bottom: 10px;">Дата оплаты:</label>
                                <input type="date" id="payment-date" class="payment-date" 
                                       value="${dayData.payment_date || getTodayDate()}">
                            </div>

                            <div class="controls-row">
                                <button onclick="savePayment()">Сохранить изменения</button>
                                <button class="delete-btn" onclick="removeLesson()">Удалить занятие</button>
                            </div>

                            <p style="margin-top: 15px; color: #6c757d; font-size: 14px;">
                                💡 Можно изменить сумму или дату оплаты
                            </p>
                        </div>
                    `;
                } else {
                    // Не оплачено (долг)
                    html = `
                        <div class="lesson-controls">
                            <div class="amount-display debt-amount">
                                -${dayData.amount} ₽
                                <div style="font-size: 16px; margin-top: 5px;">❌ Долг</div>
                            </div>

                            <div class="payment-status">
                                <label class="switch">
                                    <input type="checkbox" id="paid-toggle" ${dayData.paid ? 'checked' : ''} 
                                           onchange="togglePayment()">
                                    <span class="slider round"></span>
                                </label>
                                <span class="status-text not-paid-text" id="status-text">
                                    Отметить как оплаченное
                                </span>
                            </div>

                            <div class="amount-selector">
                                <label style="font-weight: bold; display: block; margin-bottom: 10px;">Сумма долга:</label>
                                <div class="amount-options">
                                    <div class="amount-option ${dayData.amount == 600 ? 'selected' : ''}" onclick="selectAmountOption(600)">600 ₽</div>
                                    <div class="amount-option ${dayData.amount == 1500 ? 'selected' : ''}" onclick="selectAmountOption(1500)">1500 ₽</div>
                                    <div class="amount-option ${dayData.amount != 600 && dayData.amount != 1500 ? 'selected' : ''}" 
                                         onclick="showCustomAmount()">Другая сумма</div>
                                </div>
                                ${dayData.amount != 600 && dayData.amount != 1500 ? `
                                    <input type="number" id="custom-amount" class="custom-amount" 
                                           value="${dayData.amount}" placeholder="Введите сумму" onchange="updateCustomAmount(this.value)">
                                ` : ''}
                            </div>

                            <div id="payment-date-section" style="display: none;">
                                <label style="font-weight: bold; display: block; margin-bottom: 10px;">Дата оплаты:</label>
                                <input type="date" id="payment-date" class="payment-date" 
                                       value="${getTodayDate()}">
                            </div>

                            <div class="controls-row">
                                <button onclick="savePayment()">Сохранить</button>
                                <button class="delete-btn" onclick="removeLesson()">Удалить занятие</button>
                            </div>
                        </div>
                    `;
                }
                selectedAmount = dayData.amount || 600;
            } else {
                // День без занятия
                html = `
                    <div class="lesson-controls">
                        <p style="color: #6c757d; margin-bottom: 20px; font-size: 16px;">
                            На этот день занятие не отмечено. Отметьте занятие и укажите сумму.
                        </p>

                        <div class="amount-selector">
                            <label style="font-weight: bold; display: block; margin-bottom: 10px; font-size: 18px;">
                                Выберите сумму занятия:
                            </label>
                            <div class="amount-options">
                                <div class="amount-option selected" onclick="selectAmountOption(600)">600 ₽</div>
                                <div class="amount-option" onclick="selectAmountOption(1500)">1500 ₽</div>
                                <div class="amount-option" onclick="showCustomAmount()">Другая сумма</div>
                            </div>
                            <input type="number" id="custom-amount" class="custom-amount" 
                                   style="display: none;" placeholder="Введите сумму" onchange="updateCustomAmount(this.value)">
                        </div>

                        <button class="lesson-btn" onclick="markLesson()" style="margin-top: 20px; width: 100%; padding: 15px;">
                            ✅ Отметить проведение занятия
                        </button>
                    </div>
                `;
                selectedAmount = 600;
            }

            document.getElementById('payment-info').innerHTML = html;
        }

        function selectAmountOption(amount) {
            selectedAmount = amount;

            // Обновляем UI для выбора суммы
            const options = document.querySelectorAll('.amount-option');
            options.forEach(opt => {
                if (parseInt(opt.textContent) === amount) {
                    opt.classList.add('selected');
                } else if (opt.textContent.includes('Другая')) {
                    opt.classList.remove('selected');
                } else {
                    opt.classList.remove('selected');
                }
            });

            // Скрываем поле для ввода своей суммы
            const customInput = document.getElementById('custom-amount');
            if (customInput) {
                customInput.style.display = 'none';
            }
        }

        function showCustomAmount() {
            selectedAmount = 0;

            // Обновляем UI
            const options = document.querySelectorAll('.amount-option');
            options.forEach(opt => {
                if (opt.textContent.includes('Другая')) {
                    opt.classList.add('selected');
                } else {
                    opt.classList.remove('selected');
                }
            });

            // Показываем поле для ввода
            let customInput = document.getElementById('custom-amount');
            if (!customInput) {
                // Создаем поле если его нет
                const amountSelector = document.querySelector('.amount-selector');
                customInput = document.createElement('input');
                customInput.type = 'number';
                customInput.id = 'custom-amount';
                customInput.className = 'custom-amount';
                customInput.placeholder = 'Введите сумму';
                customInput.onchange = function() { updateCustomAmount(this.value); };
                amountSelector.appendChild(customInput);
            }
            customInput.style.display = 'block';
            customInput.focus();
        }

        function updateCustomAmount(value) {
            selectedAmount = parseInt(value) || 0;
        }

        function togglePayment() {
            const dateInputSection = document.getElementById('payment-date-section');
            const statusText = document.getElementById('status-text');
            const toggle = document.getElementById('paid-toggle');

            if (toggle.checked) {
                if (dateInputSection) dateInputSection.style.display = 'block';
                statusText.textContent = 'Отметить как оплаченное';
                statusText.className = 'status-text paid-text';
            } else {
                if (dateInputSection) dateInputSection.style.display = 'none';
                statusText.textContent = 'Отметить как оплаченное';
                statusText.className = 'status-text not-paid-text';
            }
        }

        function savePayment() {
            if (!selectedDate) return;

            const dayData = paymentData[selectedDate] || { has_lesson: true, paid: false, payment_date: '', amount: selectedAmount };
            const isPaid = document.getElementById('paid-toggle') ? document.getElementById('paid-toggle').checked : dayData.paid;

            // Получаем сумму
            let amount = selectedAmount;
            if (amount === 0) {
                // Пытаемся получить из кастомного поля
                const customInput = document.getElementById('custom-amount');
                if (customInput && customInput.value) {
                    amount = parseInt(customInput.value) || 600;
                } else {
                    amount = dayData.amount || 600;
                }
            }

            const paymentDate = isPaid ? (document.getElementById('payment-date') ? document.getElementById('payment-date').value : getTodayDate()) : '';

            fetch('/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: selectedDate,
                    has_lesson: true,
                    paid: isPaid,
                    payment_date: paymentDate,
                    amount: amount
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Сохранено!');
                    location.reload();
                }
            });
        }

        function markLesson() {
            if (!selectedDate) return;

            // Получаем сумму
            let amount = selectedAmount;
            if (amount === 0) {
                const customInput = document.getElementById('custom-amount');
                if (customInput && customInput.value) {
                    amount = parseInt(customInput.value) || 600;
                }
            }

            fetch('/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    date: selectedDate,
                    has_lesson: true,
                    paid: false,
                    payment_date: '',
                    amount: amount
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Занятие отмечено! Сумма: ' + amount + ' ₽');
                    location.reload();
                }
            });
        }

        function removeLesson() {
            if (!selectedDate) return;

            if (confirm('Удалить отметку о занятии и всю финансовую информацию?')) {
                fetch('/update', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        date: selectedDate,
                        has_lesson: false,
                        paid: false,
                        payment_date: '',
                        amount: 0
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Занятие удалено!');
                        location.reload();
                    }
                });
            }
        }

        function formatDate(dateStr) {
            const date = new Date(dateStr);
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            return date.toLocaleDateString('ru-RU', options);
        }

        function getTodayDate() {
            const today = new Date();
            return today.toISOString().split('T')[0];
        }

        // Выбираем сегодняшнюю дату при загрузке
        window.onload = function() {
            const today = new Date();
            const todayStr = today.toISOString().split('T')[0];
            selectDate(todayStr);
        };
    </script>
</body>
</html>
'''


def load_data():
    """Загрузка данных из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_data(data):
    """Сохранение данных в файл"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_calendar(year, month):
    """Генерация календаря для указанного месяца"""
    import calendar

    cal = calendar.monthcalendar(year, month)
    calendar_list = []

    # Преобразуем в плоский список с нулями для пустых дней
    for week in cal:
        for day in week:
            calendar_list.append(day)

    return calendar_list


@app.route('/')
def index():
    # Получаем год и месяц из параметров или используем текущие
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))

    # Загружаем данные
    data = load_data()

    # Генерируем календарь
    cal = generate_calendar(year, month)

    # Статистика за месяц
    stats = {'lesson': 0, 'paid': 0, 'not_paid': 0, 'income': 0, 'debt': 0, 'balance': 0}
    month_str = f"{year}-{month:02d}"

    # Общая статистика по всем данным
    total_income = 0
    total_debt = 0

    for date_str, day_data in data.items():
        amount = day_data.get('amount', 0)

        if day_data.get('has_lesson', False):
            if day_data.get('paid', False):
                total_income += amount
            else:
                total_debt += amount

        # Статистика для текущего месяца
        if date_str.startswith(month_str):
            if day_data.get('has_lesson', False):
                stats['lesson'] += 1
                if day_data.get('paid', False):
                    stats['paid'] += 1
                    stats['income'] += amount
                else:
                    stats['not_paid'] += 1
                    stats['debt'] += amount

    stats['balance'] = stats['income'] - stats['debt']
    total_balance = total_income - total_debt

    # Текущая дата для отображения
    current_date = datetime(year, month, 1).strftime("%B %Y").title()
    current_date = current_date.replace('January', 'Январь').replace('February', 'Февраль').replace('March', 'Март') \
        .replace('April', 'Апрель').replace('May', 'Май').replace('June', 'Июнь') \
        .replace('July', 'Июль').replace('August', 'Август').replace('September', 'Сентябрь') \
        .replace('October', 'Октябрь').replace('November', 'Ноябрь').replace('December', 'Декабрь')

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

    # Загружаем текущие данные
    all_data = load_data()

    date_str = data['date']
    amount = data.get('amount', 600)

    if data.get('has_lesson', True):
        # Добавляем или обновляем запись
        all_data[date_str] = {
            'has_lesson': True,
            'paid': data['paid'],
            'payment_date': data.get('payment_date', ''),
            'amount': amount
        }
    else:
        # Удаляем запись о занятии
        if date_str in all_data:
            del all_data[date_str]

    # Сохраняем
    save_data(all_data)

    return jsonify({'success': True})


if __name__ == '__main__':
    # Создаём файл данных если его нет
    if not os.path.exists(DATA_FILE):
        save_data({})

    app.run(debug=True, host='0.0.0.0', port=5000)
