# -*- coding: utf-8 -*-
import pandas as pd
import sys
import msg
import os
import keybords
import aiohttp
import json
import random
import datetime
import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import ClientConnectorError

import utils
from sqliteormmagic import SQLiteDB
import sqliteormmagic as som

from config import TOKEN, ADMIN_LIST, LOG_GROUP, PAUSE_START, PAUSE_END, pay_14, pay_30, pay_90, API_KEY, DEVELOPER
from logger import logger


"""
    1. После обновления ключей перезапускать цикл и начинать итерацию с первого ключа.
    2. Оптимизировать отправление сообщений пользователям, убрать лишние действия с БД.
    3. Сделать связь между ключами и товарами, при обновлении ключей, удалать товары, которые остались без связи с ключем.
"""


headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://www.wildberries.ru',
    'Referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D1%82%D0%BE%D1%80%20%D0%B1%D0%B5%D0%BD%D0%B7%D0%B8%D0%BD%D0%BE%D0%B2%D1%8B%D0%B9',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="118", "YaBrowser";v="23.11", "Not=A?Brand";v="99", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'x-queryid': 'qid166042518169737901020240607174105',
}

db_users = SQLiteDB('users.db')
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status


async def wb_fetch_data(url, proxy):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
        async with session.get(url=url, proxy=proxy, headers=headers) as response:
            if response.status == 200:
                response_data = await response.text()

                return json.loads(response_data), response.status


async def random_proxy():
    response = await fetch_data(f"https://api.proxy6.net/{API_KEY}/getproxy")
    print(response[1])
    if response[1] != 200:
        return response[1]
    proxy_list = []
    for item in response[0]['list'].values():
        if item["ip"] == '194.67.216.135':
            continue
        proxy_list.append({
            'server': f'{item["ip"]}:{item["port"]}',
            'username': item['user'],
            'password': item['pass']
        })

    rand_proxy = random.choice(proxy_list)
    proxy = f"http://{rand_proxy['username']}:{rand_proxy['password']}@{rand_proxy['server']}"

    proxies = {
        'http': proxy,
        'https': proxy
    }

    return proxies


async def pars():
    while True:
        lst_keyword = await db_users.find_table_or_column(table_name='const', column_name='*')
        random.shuffle(lst_keyword)

        logger.warning("Цикл по всем ключам начался....")
        quant_keys = len(lst_keyword)
        current_keys_num = 1
        users_ignoring_bot = []
        cnt_keywords = 1
        logger.debug(f"Начинаю цикличный перебор по ключам. Количество ключей - {len(lst_keyword)}")
        for row in lst_keyword:
            logger.debug(f"Ключ №{cnt_keywords} - {row[0]}")
            current_quantity_keys = await som.get_cnt_keyword()
            logger.debug(f"Текущее количество ключей - {current_quantity_keys}")

            if quant_keys != current_quantity_keys[0][0]:
                logger.warning(f'Количество ключей в БД было изменено. Ключей при начале цикла - {quant_keys}, сейчаc - {current_quantity_keys[0][0]} Сбрасываю цикл.')
                break

            if (cnt_keywords % 10) == 0:
                logger.warning(f'Текущий ключ {current_keys_num} из {quant_keys}')
            cnt_keywords += 1

            current_keys_num += 1
            KEY_WORD = row[0]
            DISCOUNT_PROC = row[1]

            count_active_users = 0
            connector_error_cnt = 0
            get_prox_err = 0
            for count_page in range(1, 5):
                logger.debug(f"Готовлю get-запрос к {count_page}-й странице ключа {KEY_WORD}")
                try:
                    rand_proxy = await random_proxy()
                except Exception as e:
                    if get_prox_err < 100:
                            logger.error(f"Слишком много попыток получить прокси. Ошибка: {e}")
                    continue
                constructor_url = (f"https://search.wb.ru/exactmatch/ru/common/v5/search?ab_testing=false&appType=1&"
                                    f"curr=rub&dest=-1257786&page={count_page}&query={KEY_WORD}"
                                    f"&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false")
                try:
                    response = await wb_fetch_data(constructor_url, rand_proxy['http'])
                    try:
                        data_all, status = response[0], response[1]
                    except Exception as e:
                        logger.info(f'В строке data_all = data_all.json() произошла ошибка \n{e}')
                        continue

                    except ClientConnectorError:
                        connector_error_cnt += 1
                        if connector_error_cnt < 100:
                            logger.error(f"Ошибка подключения к хосту. Прокси - {rand_proxy['http']}")
                        continue
                except Exception as e:
                    logger.error(f'Ошибка "{e}" произошла при запросе')
                    if type(e) == 'ProxyError':
                        logger.warning(f"ProxyError: {rand_proxy['http']}")
                    continue
                else:
                    pause = random.uniform(3, 8)
                    await asyncio.sleep(pause)
                    if status != 200:
                        logger.error(f"Меня забанили, код {status}, подключаюсь через другой прокси! "
                                     f"\n текущий прокси:{rand_proxy['http']}")
                        await asyncio.sleep(60)
                        continue
                    try:
                        if data_all.get("data"):
                            products_list = data_all["data"]["products"]
                            logger.debug(f'Получено {len(products_list)} товаров')
                        else:
                            logger.debug(f'Не получил товары по даной странице')
                            
                    except Exception as e:
                        logger.critical(f"Произошла ошибка {e} при попытке достать данные из словаря. \n"
                                        f"{datetime.datetime.now().ctime()} \nСтраница:{count_page}, Ключ:{KEY_WORD}, "
                                        f"Прокси{rand_proxy['http']} \n")
                        continue
                    logger.debug(f'Начинаю итерироваться по полученным товарам.')
                    for product in products_list:
                        product_id = product['id']
                        product_in_db = await utils.find_product_id(product_id=product['id'])
                        """Если товара нет в БД, добавляем туда его, начинаем новую итерацию для другого товара"""
                        if not product_in_db:
                            try:
                                if product.get('price'):
                                    await utils.add_product_id(product_id=product['id'], price=product['price']['product'])
                                else:
                                    await utils.add_product_id(product_id=product['id'], price=product['sizes'][0]['price']['product'])
                            except Exception as ex:
                                logger.error(f'Ошибка при добавлении в БД sku: {product_id} {ex}')
                        elif product_in_db:
                            """Если товар уже есть в БД"""
                            if not product['sizes']:
                                logger.warning(f'Не удалось найти информацию о товаре {product_id}')
                                continue
                            # Получаем его данные
                            lst_id = await db_users.find_elements_in_column(table_name='tmp_id',  key_name=product_id,
                                                                            column_name='product_id')
                            lst_id = lst_id[0]

                            last_price = float(lst_id[2])
                            last_price = round(last_price)
                            new_price = float(product['sizes'][0]['price']['product'])
                            new_price = round(new_price)
                            disc_proc = (last_price - new_price) / last_price * 100
                            disc_proc = round(disc_proc)
                            if disc_proc > 20:
                                logger.debug(f'last_price-{last_price/100} new_price-{new_price/100} '
                                             f'disc_proc-{disc_proc} DISCOUNT_PROC-{DISCOUNT_PROC}')

                            if disc_proc > float(DISCOUNT_PROC):

                                # выводим здесь сообщение в боте у тех у кого подписка
                                # товар добавляем в стоп лист чтобы бот ботом не выводил больше на него сообщения или ставим цену в лям
                                # у тех у кого закончилась подписка отправляем сообщения что деньгов у них нет и удаляем из базы рассылки
                                logger.info(f"Найдена скидка. 'produc_id': {product['id']} 'new_price': {new_price}, "
                                            f"'last_price': {last_price} Ключ {KEY_WORD} {current_keys_num} из {quant_keys}")

                                user_list = await utils.get_user_list()


                                cnt_end_subs = 0
                                cnt_active_subs = 0
                                logger.debug(f'Начинаю итерироваться по списку пользователей, '
                                             f'в поисках тех у кого активна подписка')
                                for user in user_list:
                                    if user[0] in users_ignoring_bot:
                                        continue

                                    if user[3] != 'None':
                                        payment_date = datetime.datetime.strptime(user[3], '%Y-%m-%d')
                                        user_id, user_name = user[0], user[1]
                                        if datetime.datetime.now() > payment_date:
                                            cnt_end_subs += 1
                                            # удаляем юзера из базы
                                            res = await utils.check_push_msg(user_id=user_id)
                                            if str(res) == '0':
                                                try:
                                                    await asyncio.sleep(2)
                                                    await bot.send_message(chat_id=user_id, text=msg.pay_msg)
                                                    await bot.send_message(chat_id=DEVELOPER,
                                                                           text=f'Пользователю {user_name} направлено '
                                                                                f'сообщение об окончании подписки')
                                                except Exception as ex:
                                                    logger.error(f"Ошибка при отправке сообщения {user_id} {ex}")
                                                await utils.upd_push_msg_1(user_id=user_id)
                                            # db_users.upd_element_in_column(table_name='tmp_id', set_upd_par_name='price', set_key_par_name='1', upd_column_name='product_id', key_column_name=product['id'])

                                        else:
                                            cnt_active_subs += 0
                                            logger.info(f"Отправляю сообщение пользователю {user[1]}")

                                            #отправляем сообщение о скидке
                                            # try:
                                            url_photo_lst = await utils.get_photo_url_by_id(product_id=str(product['id']))

                                            text = f"""
🎁 <a href="https://www.wildberries.ru/catalog/{product['id']}/detail.aspx">{product['name']}</a>

🙅‍♀ Старая цена: <s>{round(last_price/100)}</s> р.
👍 Цена со скидкой: {round(new_price/100)} р.
📉 Скидка: {disc_proc}%
    """
                                            try:
                                                await asyncio.sleep(2)
                                                await bot.send_photo(chat_id=user_id, caption=text, photo=url_photo_lst[0])
                                                logger.info(f"Отправлено!")
                                                # await bot.send_message(chat_id=user_id, text=text)
                                                count_active_users += 1
                                            except Exception as ex:
                                                if 'bot was blocked by the user' in str(ex):
                                                    users_ignoring_bot.append(user_id)
                                                logger.error(f"Ошибка при отправке сообщения {user_id},{user_name}"
                                                            f"\n{ex}\nphoto={url_photo_lst[0]}\n")
                                                continue

                                logger.info(f"Количество пользователей с активной подпиской - {cnt_active_subs}, "
                                            f"с истекшей - {cnt_end_subs}")

                                            # except Exception as ex:
                                            #     bot.send_message(chat_id=LOG_GROUP, caption=ex)
                                            #     print(ex)

                                await db_users.upd_element_in_column(table_name='tmp_id', set_upd_par_name='price',
                                                                     set_key_par_name='1', upd_column_name='product_id',
                                                                     key_column_name=product_id)

        await bot.send_message(chat_id=LOG_GROUP, text="Цикл по всем ключам завершен")


if __name__ == "__main__":
    pass

    