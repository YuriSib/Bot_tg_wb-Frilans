import requests

cookies = {
    '_wbauid': '2451425061762531645',
    '_cp': '1',
    'x_wbaas_token': '1.1000.40fb3ff31a7e4d41839c61bf50715be7.MHw5NC4yMzAuMzUuNTN8TW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTM4LjAuMC4wIFlhQnJvd3Nlci8yNS44LjAuMCBTYWZhcmkvNTM3LjM2fDE3NjUwMjMzMDN8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzY0NDE4NTAzfDE=.MEYCIQC03F/Vrly5R58N/JVmPp8kuYcQWkYLJ8ewbQ5O4Hj7TwIhAMEk6fZyJ65oq2U9t4hQl+QeXrs5wp9mRF05Ivu1FGN6',
}

headers = {
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'deviceid': 'site_bf631b5e4bff4512995738aa60ca1914',
    'priority': 'u=1, i',
    'referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%A0%D0%A3%D0%B1%D0%B0%D1%88%D0%BA%D0%B0',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "YaBrowser";v="25.8", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36',
    'x-queryid': 'qid245142506176253164520251122160607',
    'x-requested-with': 'XMLHttpRequest',
    'x-spa-version': '13.14.1',
    'x-userid': '0',
    # 'cookie': '_wbauid=2451425061762531645; _cp=1; x_wbaas_token=1.1000.40fb3ff31a7e4d41839c61bf50715be7.MHw5NC4yMzAuMzUuNTN8TW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTM4LjAuMC4wIFlhQnJvd3Nlci8yNS44LjAuMCBTYWZhcmkvNTM3LjM2fDE3NjUwMjMzMDN8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzY0NDE4NTAzfDE=.MEYCIQC03F/Vrly5R58N/JVmPp8kuYcQWkYLJ8ewbQ5O4Hj7TwIhAMEk6fZyJ65oq2U9t4hQl+QeXrs5wp9mRF05Ivu1FGN6',
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
    'page': '1',
    'query': 'РУбашка',
    'resultset': 'catalog',
    'sort': 'popular',
    'spp': '30',
    'suppressSpellcheck': 'false',
}




if __name__ == "__main__":
    response = requests.get(
        'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    print(response)