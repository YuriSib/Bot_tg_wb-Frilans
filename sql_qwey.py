import sqlite3
from sqlite3 import Error


# BD_PATH = r'/bot/users.db'
BD_PATH = r'C:\Users\User\PycharmProjects\Tg_wb_bot\users.db'


def get_cnt_products(BD_PATH):
    conn = sqlite3.connect(BD_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM tmp_id WHERE price IS NOT NULL")
    count = cursor.fetchall()
    conn.close()

    return count


if __name__ == "__main__":
    print(get_cnt_products(BD_PATH))