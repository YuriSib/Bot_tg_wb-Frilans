from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_menu_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Запустить", callback_data="run_pars")],
    [InlineKeyboardButton(text="Обновить ключевые слова и скидки", callback_data="upd_key_words")],
    [InlineKeyboardButton(text="Отчет", callback_data="report_users")],
    [InlineKeyboardButton(text="Количество товаров в БД", callback_data="product_count")],
    [InlineKeyboardButton(text="Написать сообщение для рассылки", callback_data="рассылка")]
])

should_sabs = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Хочу подписку!", callback_data="paydate::30")],
])

user_menu_main = InlineKeyboardMarkup(inline_keyboard=[
    # [InlineKeyboardButton(text="Сохранить ID", callback_data="save_id")],
    [InlineKeyboardButton(text="Оплатить", callback_data="1_pay")],
    [InlineKeyboardButton(text="Помощь", url="https://t.me/Wberry_Admin")]
])

pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Оплатить", callback_data="1_pay")],
])

choice_paydate = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить 30 дней", callback_data="paydate::30")]
    ])

back = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back")],
    ])


def otmena_pay(user_id) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="отменить", callback_data=f"otmena_pay::{user_id}")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)