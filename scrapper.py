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
import requests
from concurrent.futures import ThreadPoolExecutor

import utils
from sqliteormmagic import SQLiteDB
import sqliteormmagic as som

from config import TOKEN, ADMIN_LIST, LOG_GROUP, PAUSE_START, PAUSE_END, pay_14, pay_30, pay_90, API_KEY, DEVELOPER
from logger import logger


executor = ThreadPoolExecutor()

"""
    1. После обновления ключей перезапускать цикл и начинать итерацию с первого ключа.
    2. Оптимизировать отправление сообщений пользователям, убрать лишние действия с БД.
    3. Сделать связь между ключами и товарами, при обновлении ключей, удалать товары, которые остались без связи с ключем.
"""


db_users = SQLiteDB('users.db')
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status


def fetch_data_01(url, proxy, headers, params, cookies):
    return requests.get(url, params=params, cookies=cookies, headers=headers, proxies=proxy)


async def async_fetch_data(url, proxy, query, page):
    cookies = {
    '_wbauid': '2451425061762531645',
    'wbx-validation-key': 'd3057d4d-0d12-406b-aa8a-e00a427a2329',
    'feedbacks_link_accepted': '1',
    'x_wbaas_token': '1.1000.e79f25e5ae0348e5a33c2e72080f8fb9.MHw5NS43MS4zMi4xMTd8TW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTM4LjAuMC4wIFlhQnJvd3Nlci8yNS44LjAuMCBTYWZhcmkvNTM3LjM2fDE3NzU1MDEyNzR8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzc0ODk2NDc0fDE=.MEUCIQD1pBnHojrrvlVzIxmeywCnRqvA1ssr2UxBFmd0E5tolgIgBRYOAYoAr3Q/KKrd1I44Q+H9zzyBtaWmu+7ZbYYLZgA=',
    'routeb': '1774291677.186.64.312767|74ada48fd20445fe87ec57de1fe798ac',
}

    headers = {
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NzQyOTE2NzYsInVzZXIiOiIzNzU0MDUyMCIsInNoYXJkX2tleSI6IjciLCJjbGllbnRfaWQiOiJ3YiIsInNlc3Npb25faWQiOiIzMDRkMDhlNGJlZTU0NDdjYmJiMjczNmE1MzNkOGQzNCIsInBob25lIjoiOEhjNVAvZDkxbVZ2MG1Nenhqdng5Zz09IiwidmFsaWRhdGlvbl9rZXkiOiI3MjUyOGY5MTExZjZhYjk5YTcxYTlkOTc0MzhlMjgxOWFiMTM2YjNmNzQzYTk3OTM5ODUzMTMxYThkZWRiZjlhIiwidXNlcl9yZWdpc3RyYXRpb25fZHQiOjE2NzExMDk1OTgsInZlcnNpb24iOjJ9.GAYgR5gU2wuEJIURl_A3rWl7VAIyFNHL-es6anMDjXs6H94Pi9kua8NzxEWg0WMYT8z31lvKGMMgVGBjWEq83VgQWwse-S3RvpM0C_PHyvmbAMZD183vm8jP1JY2B5bk81Qa8XG_ZjjOV3teepIceag5x0OxnVL5tisTWDDeIvt9ZQXe0Aid0n2wJuLdP3JyHpvqavWTt167R-0Eo4TKzgPiP2C5QcPgE9LFeP5yuKN0Livy-0_H1FWJ6pcqb78vFcLKS9CK_awScek1fU7iW9QR04NU0P7i_Z62QzHuxPvD1kgPtHUr72WEct6VstkBxyd6e0Ie45Xc3olFObZpwg',
    'deviceid': 'site_bf631b5e4bff4512995738aa60ca1914',
    'priority': 'u=1, i',
    'referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=%D1%8D%D0%BB%D0%B5%D0%BA%D1%82%D1%80%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F%20%D1%82%D1%83%D1%80%D0%BA%D0%B0',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "YaBrowser";v="25.8", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36',
    'x-queryid': 'qid245142506176253164520260323184908',
    'x-requested-with': 'XMLHttpRequest',
    'x-spa-version': '14.2.4',
    'x-userdata': 'AQYAAQIAAQIBAAIEAAMDAAoCAAEAEqgDrYgjiaSwqtCp8aeJKTKnGqBHpMgxra5hK-Ao4amnLfGs26qrracfAaOirEenlquitp6j1B71IWMqnizPquml0qvgoNUgkScOrZWqVCKeom2t0qIKJDqnGjA6qYKjGqgVMz-oyBTIqvWt8axspp6q9ad9pWOnu64QpVGqL6SLKIunryMBJtAwl6nlFOGoTa55Lfiswq_UKZuuxKpUrKohjq1dLLYykrJILHKtabM_JE0sDyl8JW-yLyarpBupOKxNroajfbBNptyqxKmhoRMrGqqGKDQe6a2OjPQqKSXrnKMVOCfUKNufxzByJycpabcanKqkkSMnq6KtEylKrHgACi4fqb4rBJ4Fo8akAq53oReiox7HJ3cnq6VVKHCmQij0plQpMi1VLAuuS6yBJaQr8rAyHxYff7A3ra2ZtqIoL1ytvqMnIW-qx6RnLdkwE6WSqzCtpKIorC4sOzAYrdCnmqRwq2WdkqjZKP2pOqnQKl2qVClvKCEfkacfJx8v-y2trx-m4RAhnTKwC6DiMLarUyjZIA-jvacwqK0kISC2nOIpm6xwKNEs0aVeK9etXqnzKjqnMKxErEQtQyJCKRenSzmSromtvieRpPQhx6aAMC6hvi9_Kjoi-yMfr7QmvgOGoDKw0aleoAYjfzHqKTIrBKa-La2fZS2KLLabmq4FKJwxcgFIBbT2OeijNi2nNY0A',
    'x-userid': '37540520',
    # 'cookie': '_wbauid=2451425061762531645; wbx-validation-key=d3057d4d-0d12-406b-aa8a-e00a427a2329; feedbacks_link_accepted=1; x_wbaas_token=1.1000.e79f25e5ae0348e5a33c2e72080f8fb9.MHw5NS43MS4zMi4xMTd8TW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTM4LjAuMC4wIFlhQnJvd3Nlci8yNS44LjAuMCBTYWZhcmkvNTM3LjM2fDE3NzU1MDEyNzR8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzc0ODk2NDc0fDE=.MEUCIQD1pBnHojrrvlVzIxmeywCnRqvA1ssr2UxBFmd0E5tolgIgBRYOAYoAr3Q/KKrd1I44Q+H9zzyBtaWmu+7ZbYYLZgA=; routeb=1774291677.186.64.312767|74ada48fd20445fe87ec57de1fe798ac',
}

    params = {
        'ab_testing': [
            'false',
            'false',
        ],
        'appType': '1',
        'curr': 'rub',
        'dest': '-1255987',
        'hide_dtype': '11',
        'inheritFilters': 'false',
        'lang': 'ru',
        'page': str(page),
        'query': query,
        'resultset': 'catalog',
        'sort': 'popular',
        'spp': '30',
        'suppressSpellcheck': 'false',
    }
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, fetch_data_01, url, proxy, headers, params, cookies)


async def random_proxy():
    response = await fetch_data(f"https://px6.me/api/{API_KEY}/getproxy")
    if response[1] != 200:
        return response[1]
    proxy_list = []
    for item in response[0]['list'].values():
        proxy_list.append({
            'server': f'{item["ip"]}:{item["port"]}',
            'username': item['user'],
            'password': item['pass']
        })

    return random.choice(proxy_list)


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
            logger.info(f"Ключ №{cnt_keywords} - {row[0]}")
            current_quantity_keys = await som.get_cnt_keyword()
            logger.info(f"Текущее количество ключей - {current_quantity_keys}")

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
                logger.info(f"Готовлю get-запрос к {count_page}-й странице ключа {KEY_WORD}")
                try:
                    rand_proxy = await random_proxy()
                except Exception as e:
                    if get_prox_err < 100:
                            logger.error(f"Слишком много попыток получить прокси. Ошибка: {e}")
                    continue

                url = "https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search"
                for attempt in range(3):
                    try:
                        response = await async_fetch_data(url, rand_proxy, query=KEY_WORD, page=count_page)
                        status = response.status_code
                        if status == 200:
                            data_all = response.json()
                        else:
                            logger.info("Статус != 200")
                            continue
                    except ConnectionResetError:
                        logger.warning(f'Удалённый сервер принудительно закрыл соединение. Запрос будет повторен.')
                        await asyncio.sleep(3)
                        continue
                    except ClientConnectorError:
                        connector_error_cnt += 1
                        if connector_error_cnt < 100:
                            logger.error(f"Ошибка подключения к хосту. Прокси - {rand_proxy['http']}")
                        continue
                    except Exception as e:
                        if "'NoneType' object is not subscriptable" in str(e):
                            logger.info(f'None при распаковке ответа. url - {url}'
                                        f'\nПовторяю попытку {attempt} из 3')
                        else:
                            logger.info(f'Неизвестная ошибка - {e}')
                        await asyncio.sleep(3)
                        continue

                    pause = random.uniform(3, 8)
                    await asyncio.sleep(pause)
                    if status != 200:
                        logger.error(f"Меня забанили, код {status}, подключаюсь через другой прокси! "
                                     f"\n текущий прокси:{rand_proxy['http']}")
                        await asyncio.sleep(60)
                        continue
                    try:
                        if data_all.get("products"):
                            products_list = data_all["products"]
                            logger.info(f'Получено {len(products_list)} товаров')
                        else:
                            logger.info(f'Не получил товары по данной странице')

                    except Exception as e:
                        logger.critical(f"Произошла ошибка {e} при попытке достать данные из словаря. \n"
                                        f"{datetime.datetime.now().ctime()} \nСтраница:{count_page}, Ключ:{KEY_WORD}")
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
                                logger.info(f'Начинаю итерироваться по списку пользователей, '
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
                                                logger.debug(f"Отправлено!")
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
    asyncio.run(pars())

