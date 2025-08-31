
"""
Приложение  для отображения курса криптовалют
Конвертирует криптовалюты в обычные валюты через API CoinGecko
"""

from tkinter import * 
from tkinter import ttk #модуль с современ виджетами
from tkinter import messagebox as mb 
import requests 

# Словарь кодов криптовалют и их полных названий
crypto_currencies = {
    "BTC": "Bitcoin (BTC)",
    "ETH": "Ethereum (ETH)",
    "XRP": "XRP (XRP)",
    "USDT": "Tether (USDT)",
    "SOL": "Solana (SOL)",
    "BNB": "Binance Coin (BNB)",
    "DOGE": "Dogecoin (DOGE)",
    "ADA": "Cardano (ADA)"
}

# Словарь соответствия кодов и ID для CoinGecko API 
crypto_ids = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XRP": "ripple",
    "USDT": "tether",
    "SOL": "solana",
    "BNB": "binancecoin",
    "DOGE": "dogecoin",
    "ADA": "cardano"
}

# Словарь кодов валют и их полных названий
currencies = {
    "USD": "Американский доллар",
    "EUR": "Евро",
    "JPY": "Японская йена",
    "GBP": "Британский фунт стерлингов",
    "AUD": "Австралийский доллар",
    "CAD": "Канадский доллар",
    "CHF": "Швейцарский франк",
    "CNY": "Китайский юань",
    "RUB": "Российский рубль",
    "KZT": "Казахстанский тенге",
    "UZS": "Узбекский сум"
}

# def center_window(window, width, height):
#     """Центрирует окно на экране"""
#     # Получаем размеры экрана
#     screen_width = window.winfo_screenwidth()
#     screen_height = window.winfo_screenheight()
    
#     # Вычисляем координаты для центрирования
#     x = (screen_width - width) // 2
#     y = (screen_height - height) // 2
    
#     # Устанавливаем позицию окна
#     window.geometry(f"{width}x{height}+{x}+{y}")

def update_base_label(event):
    """Обновляет метку криптовалюты"""
    code = base_combobox.get()
    if code in crypto_currencies:
        name = crypto_currencies[code]
        base_label.config(text=name)
    # Автоматически получаем курс при выборе
    if target_combobox.get():
        exchange()

def update_target_label(event):
    """Обновляет метку целевой валюты"""
    code = target_combobox.get()
    if code in currencies:
        name = currencies[code]
        target_label.config(text=name)
    # Автоматически получаем курс при выборе
    if base_combobox.get():
        exchange()

def validate_amount(P): #валидация ввода, что мы ввели число или точку
    """Проверяет ввод только цифр и точки"""
    if P == "" or P == ".":
        return True
    try:
        float(P)
        return True
    except ValueError:
        return False

def on_crypto_amount_change(event): #очищаем окно ввода
    """Обработчик изменения количества криптовалюты"""
    if crypto_amount_entry.get():
        currency_amount_entry.delete(0, END)
    # Автоматический перерасчет
    # if base_combobox.get() and target_combobox.get():
    #     exchange()

def on_currency_amount_change(event):
    """Обработчик изменения количества валюты"""
    if currency_amount_entry.get():
        crypto_amount_entry.delete(0, END)
    # Автоматический перерасчет
    if base_combobox.get() and target_combobox.get():
        exchange()
    
def exchange(): #обменник В этой функции большая вложенность. Нарушаем принцип SINGLE
    """Получает курс обмена криптовалюты на валюту"""
    target_code = target_combobox.get() 
    base_code = base_combobox.get() 
    
    if not target_code or not base_code: #проверяем что выбрано оба параметра
        result_label.config(text="Выберите криптовалюту и валюту")
        return
    
    # Получаем количество единиц
    try: #обработчик ошибок
        crypto_amount = float(crypto_amount_entry.get() or "1")
        currency_amount = float(currency_amount_entry.get() or "1")
    except ValueError:
        result_label.config(text="Введите корректное количество")
        return
    
    result_label.config(text="Загрузка курса...")
    window.update()
    
    try:
        # Используем CoinGecko API для криптовалют
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        } # Строка идетификатор приложения
        
        # Получаем правильный ID для API
        crypto_id = crypto_ids.get(base_code)
        if not crypto_id:
            result_label.config(text=f"Криптовалюта {base_code} не поддерживается")
            return
        
        # Получаем курс криптовалюты в USD
        crypto_url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd'
        response = requests.get(crypto_url, headers=headers, timeout=15)
        response.raise_for_status() 
        crypto_data = response.json()
        
        if crypto_id in crypto_data and 'usd' in crypto_data[crypto_id]:
            crypto_usd_rate = crypto_data[crypto_id]['usd'] #Извлекаем данные о курсе
            
            # Получаем курс USD к целевой валюте
            if target_code == 'USD':
                exchange_rate = crypto_usd_rate #Прямой курск крипты к долларам
            else:
                currency_url = f'https://open.er-api.com/v6/latest/USD'
                currency_response = requests.get(currency_url, headers=headers, timeout=10)
                currency_response.raise_for_status()
                currency_data = currency_response.json() #запрос курсов других валют, ответ в json
                
                #проверяем наличие валюты в списке, делаем расчет. Если валюты нет, выводим ошибку
                if target_code in currency_data['rates']:
                    usd_to_target_rate = currency_data['rates'][target_code]
                    exchange_rate = crypto_usd_rate * usd_to_target_rate
                else:
                    result_label.config(text=f"Валюта {target_code} не найдена")
                    return
            #Выводим название валюты по ее коду
            base_name = crypto_currencies[base_code]
            target_name = currencies[target_code]
            
            # Рассчитываем результат с учетом количества
            if crypto_amount_entry.get():  # Если введено количество криптовалюты
                total_result = crypto_amount * exchange_rate
                result_text = f"{crypto_amount} {base_name} = {total_result:.4f} {target_name}"
            elif currency_amount_entry.get():  # Если введено количество валюты
                # Рассчитываем обратный курс
                reverse_rate = 1 / exchange_rate
                total_result = currency_amount * reverse_rate
                result_text = f"{currency_amount} {target_name} = {total_result:.4f} {base_name}"
            else:  # Если оба поля пустые, используем 1 единицу для крипты
                total_result = 1 * exchange_rate
                result_text = f"1 {base_name} = {total_result:.4f} {target_name}"
            
            result_label.config(text=result_text)
        else:
            result_label.config(text=f"Криптовалюта {base_code} не найдена в API")

    except requests.RequestException as e:
        result_label.config(text=f"Ошибка сети: {e}")
    except Exception as e:
        result_label.config(text=f"Произошла ошибка: {e}")
#можно назвать атавизмом, осталась от вывода курса в новом окне. Оставил тк делает перерасчет
def on_enter(event):
    """Обработчик нажатия Enter"""
    exchange()

# Создание графического интерфейса
window = Tk() 
window.title("Convertere")
window.geometry("800x450")

# Центрируем окно на экране
# center_window(window, 800, 450)

# Заголовок
title_label = Label(window, text="Конвертер криптовалют", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Создаем фрейм для всех элементов
main_frame = Frame(window)
main_frame.pack(pady=20)

# Группа 1: Количество и криптовалюта
crypto_group = Frame(main_frame)
crypto_group.pack(side=LEFT, padx=10)

# Количество криптовалюты
Label(crypto_group, text="Количество:", font=("Arial", 10)).pack()
crypto_amount_entry = ttk.Entry(crypto_group, width=8, validate="key", 
                               validatecommand=(window.register(validate_amount), '%P'))
crypto_amount_entry.pack(pady=2)
crypto_amount_entry.bind('<KeyRelease>', on_crypto_amount_change)

# Криптовалюта
Label(crypto_group, text="Криптовалюта:", font=("Arial", 10)).pack()
base_combobox = ttk.Combobox(crypto_group, values=list(crypto_currencies.keys()), width=10)
base_combobox.pack(pady=2)
base_combobox.bind("<<ComboboxSelected>>", update_base_label) 

# Метка под криптовалютой
base_label = ttk.Label(crypto_group, text="", font=("Arial", 9))
base_label.pack()

# Стрелка
arrow_label = Label(main_frame, text="→", font=("Arial", 16, "bold"))
arrow_label.pack(side=LEFT, padx=20, pady=20)

# Группа 2: Количество и валюта
currency_group = Frame(main_frame)
currency_group.pack(side=LEFT, padx=10)

# Количество валюты
Label(currency_group, text="Количество:", font=("Arial", 10)).pack()
currency_amount_entry = ttk.Entry(currency_group, width=8, validate="key", 
                                 validatecommand=(window.register(validate_amount), '%P'))
currency_amount_entry.pack(pady=2)
currency_amount_entry.bind('<KeyRelease>', on_currency_amount_change)

# Целевая валюта
Label(currency_group, text="Валюта:", font=("Arial", 10)).pack()
target_combobox = ttk.Combobox(currency_group, values=list(currencies.keys()), width=10)
target_combobox.pack(pady=2)
target_combobox.bind("<<ComboboxSelected>>", update_target_label) 

# Метка под валютой
target_label = ttk.Label(currency_group, text="", font=("Arial", 9))
target_label.pack()

# Поле для вывода результата
result_frame = Frame(window)
result_frame.pack(pady=20)

result_label = Label(result_frame, text="Выберите криптовалюту и валюту", 
                    font=("Arial", 12), fg="#333333", wraplength=700)
result_label.pack()

# Привязываем Enter к окну
window.bind('<Return>', on_enter)

# Привязываем Enter к комбобоксам и полям ввода
base_combobox.bind('<Return>', on_enter)
target_combobox.bind('<Return>', on_enter)
crypto_amount_entry.bind('<Return>', on_enter)
currency_amount_entry.bind('<Return>', on_enter)

window.mainloop()
