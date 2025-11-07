import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Получаем структуру таблицы users
cursor.execute("PRAGMA table_info(users)")
columns = [column[1] for column in cursor.fetchall()]  # Получаем только имена колонок

# Выполняем запрос для получения последних 5 записей по дате регистрации
cursor.execute("SELECT * FROM users ORDER BY reg_time DESC LIMIT 5")
rows = cursor.fetchall()

# Закрываем соединение
conn.close()

# Выводим данные
print("Колонки:", columns)
print("Последние 5 записей по дате регистрации:")
for row in rows:
    print(dict(zip(columns, row)))  # Преобразуем в словарь для удобства вывода
