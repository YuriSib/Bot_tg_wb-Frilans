import requests
from random import choice
import aiohttp
import asyncio
import json
import random


from config import API_KEY
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()


def fetch_data_01(url, proxy, headers, params, cookies):
    return requests.get(url, params=params, cookies=cookies, headers=headers, proxies=proxy)


async def async_fetch_data(url, proxy, query, page):
    cookies = {
        'x_wbaas_token': '1.1000.7a68aba12f83430ba7d90232a69ac049.MHwxNjguMTk2LjIzNy4xODJ8TW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTM4LjAuMC4wIFlhQnJvd3Nlci8yNS44LjAuMCBTYWZhcmkvNTM3LjM2fDE3NjM3NDExODZ8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzYzMTM2Mzg2.MEUCIF2E+AFakALQI8OJJs0UNQwgAbB/lyKIFRfHqWLlQTZeAiEAvj7H/UfhVmrYLAtxyu+Shlfw1jxQITvgjX+qEarpxI0=',
        '_wbauid': '2451425061762531645',
        '_cp': '1',
    }
    headers = {
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9',
        'deviceid': 'site_bf631b5e4bff4512995738aa60ca1914',
        'priority': 'u=1, i',
        'referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=%D1%81%D0%B2%D0%B8%D1%82%D0%B5%D1%80%20%D0%B6%D0%B5%D0%BD%D1%81%D0%BA%D0%B8%D0%B9%20%D0%BE%D0%B2%D0%B5%D1%80%D1%81%D0%B0%D0%B9%D0%B7',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "YaBrowser";v="25.8", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36',
        'x-pow': '2|site_bf631b5e4bff4512995738aa60ca1914|1762584005|6,8,1,6a68bb000000000,4574d00c-7cbf-438c-bbb7-0953dbc38f77,2090ff49-120a-4a68-825b-d06777137b0f,1762584064,1,8wEtv0Uvv8XVXCtcCFsBmgmlnESOZo8RCbgSBbMn32A=,f432eb33ed73dc666aeb2a8b7439a2d5a9b79bd1eb2d65911407d725d4e29c901599595b56c8475c0f872e29eb084ec55b709fdf2cf890b151dcdf09705f6a6d|21',
        'x-queryid': 'qid245142506176253164520251108064014',
        'x-requested-with': 'XMLHttpRequest',
        'x-spa-version': '13.12.0',
        'x-userid': '0',
    }
    params = {
        'ab_testing': [
            'false',
            'false',
        ],
        'appType': '1',
        'curr': 'rub',
        'dest': '-1257786',
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


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status


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



async def test_get(key, count_page):
    url = "https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search"
    rand_proxy = await random_proxy()
    response = await async_fetch_data(url, rand_proxy, query=key, page=count_page)

    return response


if __name__ == '__main__':
    response = asyncio.run(test_get("Рубашка", 2))
    # response = requests.get("https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search")
    print(response.status_code)