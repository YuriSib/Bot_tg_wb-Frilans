from datetime import datetime, timedelta
import re
import pytz
import asyncio
import aiosqlite

import sqliteormmagic as som
from sqliteormmagic import SQLiteDB
from logger import logger


db_users = SQLiteDB('users.db')


# функция получения даты и времени по МСК в текстовом виде
async def get_msk_time() -> str:
    current_date = datetime.now()
    time_now = current_date.strftime('%Y-%m-%d')
    return time_now


async def get_date() -> datetime:
    date_now = datetime.now(pytz.timezone("Europe/Moscow"))
    date_now = date_now.strftime('%Y-%m-%d')
    return date_now


async def get_free_date() -> datetime:
    date_now = datetime.now(pytz.timezone("Europe/Moscow")) + timedelta(days=7)
    date_now = date_now.strftime('%Y-%m-%d')
    print(date_now)
    return date_now


async def upd_pay_date(day) -> datetime.date:
    current_date = datetime.now()
    future_date = current_date + timedelta(days=day)
    return future_date.date()


# функция распарсивания deep-link ссылка бота
async def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None


async def get_basket(vol):
    baskets = {
        'basket-01.wb.ru/': [x for x in range(0, 143 + 1)],
        'basket-02.wb.ru/': [x for x in range(144, 287 + 1)],
        'basket-03.wb.ru/': [x for x in range(288, 431 + 1)],
        'basket-04.wb.ru/': [x for x in range(432, 719 + 1)],
        'basket-05.wb.ru/': [x for x in range(720, 1007 + 1)],
        'basket-06.wb.ru/': [x for x in range(1008, 1061 + 1)],
        'basket-07.wb.ru/': [x for x in range(1062, 1115 + 1)],
        'basket-08.wb.ru/': [x for x in range(1116, 1169 + 1)],
        'basket-09.wb.ru/': [x for x in range(1170, 1313 + 1)],
        'basket-10.wb.ru/': [x for x in range(1314, 1601 + 1)],
        'basket-11.wb.ru/': [x for x in range(1602, 1655 + 1)],
        'basket-12.wb.ru/': [x for x in range(1656, 1919 + 1)],
        'basket-13.wb.ru/': [x for x in range(1920, 2045 + 1)],
        'basket-14.wb.ru/': [x for x in range(2046, 2190 + 1)],
        'basket-15.wb.ru/': [x for x in range(2191, 2406 + 1)],
        'basket-16.wb.ru/': [x for x in range(2407, 2621 + 1)],
        'basket-17.wb.ru/': [x for x in range(2622, 2837 + 1)],
        'basket-18.wb.ru/': [x for x in range(2838, 3053 + 1)],
        'basket-19.wb.ru/': [x for x in range(3054, 3269 + 1)],
        'basket-20.wb.ru/': [x for x in range(3270, 3485 + 1)],
        'basket-21.wb.ru/': [x for x in range(3486, 3700 + 1)],
        'basket-22.wb.ru/': [x for x in range(3702, 3917 + 1)],
        'basket-23.wb.ru/': [x for x in range(3918, 4133 + 1)],
        'basket-24.wb.ru/': [x for x in range(4134, 4349 + 1)],
        'basket-25.wb.ru/': [x for x in range(4350, 4565 + 1)],
        'basket-26.wb.ru/': [x for x in range(4566, 4877 + 1)],
        'basket-27.wb.ru/': [x for x in range(4878, 5189 + 1)],
        'basket-28.wb.ru/': [x for x in range(5190, 5500 + 1)],

        'basket-29.wb.ru/': [x for x in range(5502, 5812 + 1)],
    }

    for key, value in baskets.items():
        if int(vol) in value:
            return key

    return 'basket-30.wb.ru/'
    

async def get_photo_url_by_id(product_id: str):
   
    """Получение изображения товара"""
    print(product_id)
    part = product_id[0:-3]
    vol = part[0:-2]
    basket = await get_basket(vol)
    photo_url_lst = []
    for i in range(1, 4):
        url = f'https://{basket}vol{vol}/part{part}/{product_id}/images/big/{str(i)}.webp'
        photo_url_lst.append(url.replace('.wb.ru', '.wbbasket.ru'))
       
    return photo_url_lst


async def cr_table_users(message):
    await db_users.create_table('users', [
            ("from_user_id", 'INTEGER UNIQUE'), 
            ("from_user_username", 'TEXT'), 
            ("reg_time", 'TEXT'), 
            ("payment_date", 'TEXT'), 
            ("status", 'TEXT'), 
            ("last_period", 'TEXT'), 
            ])
       
    await db_users.ins_unique_row('users', [
            ("from_user_id", message.from_user.id), 
            ("from_user_username", message.from_user.username), 
            ("reg_time", await get_msk_time()),
            ("payment_date", 'None'), 
            ("status", 'new'),             
            ("last_period", '0'),                 
            ])    


async def cr_table_keywords():
    await db_users.create_table('const', [
            ("keyword", 'TEXT'),             
            ("discount_proc", 'TEXT'),               
            ])


async def cr_tmp_table_id():
    await db_users.create_table('tmp_id', [
            ("product_id", 'INTEGER UNIQUE'),             
            ("reg_time", 'TEXT'),    
            ("price", 'TEXT'),    
                        
            ])


async def add_product_id(product_id, price):
    await db_users.ins_unique_row('tmp_id', [
            ("product_id", product_id),             
            ("reg_time", await get_msk_time()),
            ("price", price),   
                                            
            ])    


async def txt_to_lst(words_file: str):
    with open(words_file, mode='r', encoding='utf-8') as words_file:
        print(words_file) 
        text_lst = words_file.read()
        text_lst = text_lst.split('\n')
        print(text_lst)
    return text_lst


async def find_product_id(product_id):
    lst_id = await db_users.find_elements_in_column(table_name='tmp_id',  key_name=product_id, column_name='product_id')
    if len(lst_id) > 0:
        return True
    else:
        return False
    

async def get_user_list():
    query = f"""
    SELECT * FROM users
    """
    res = await som.execute_query_select(query=query, params=[])

    return res 


async def get_user_status(user_id):
    async with aiosqlite.connect('users.db') as connection:
        query = f"""
        SELECT status FROM users WHERE from_user_id = {user_id}
        """
        res = await som.execute_query_select(query=query, params=[])

    return res[0][0]


async def get_last_period(user_id):
    query = f"""
    SELECT last_period FROM users WHERE from_user_id = {user_id}
    """
    res = await som.execute_query_select(query=query, params=[])
    return int(res[0][0]) 


async def upd_push_msg_1(user_id):
    query = f"""
    UPDATE users
    SET "check" = 1
    WHERE from_user_id = ?
    """
    res = await som.execute_query_select(query=query, params=[user_id])


async def upd_push_msg_0(user_id):
    query = f"""
    UPDATE users
    SET "check" = '0'
    WHERE from_user_id = ?
    """
    res = await som.execute_query_select(query=query, params=[user_id])


async def check_push_msg(user_id):
    query = f"""
    SELECT "check" 
    FROM users
    WHERE from_user_id = ?
    """
    res = await som.execute_query_select(query=query, params=[user_id])
    res = res[0][0]
    print(query)
    return res


async def pars_msg_keyword(document_name, message, bot):
    try:
        await som.del_key_words()

        text_lst = await txt_to_lst(document_name)
        print(text_lst)
        for row in text_lst:
            keyword = row.split(' ')[0]
            discount_proc = row.split(' ')[1]
            print(row)
            await db_users.ins_unique_row('const', [
                ("keyword", keyword),
                ("discount_proc", discount_proc),
                    ])
        logger.warning('Ключи обновлены!')
    except Exception as ex:
        logger.critical(f'''При обновлении ключей возникла ошибка "{ex}"''')
        await bot.send_message(chat_id=message.from_user.id, text=f'Чето сломалось...')