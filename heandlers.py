import asyncio
import os
import time

from aiogram import Router, F, Bot, types
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
# from aiogram.types.input_file import FSInputFile
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ParseMode
from aiogram.utils.media_group import MediaGroupBuilder

import utils
import sqliteormmagic as som

from config import TOKEN, ADMIN_LIST, LOG_GROUP, pay_14, pay_30, pay_90, DEVELOPER
from logger import logger
import keybords as kb
import msg
from scrapper import pars, db_users


router = Router()
bot = Bot(TOKEN)


all_media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all_media')


@router.message(F.text == '/start')
async def start_fnc(message: Message):
    # await utils.cr_table_users(message=message)

    media1 = [InputMediaPhoto(type='photo',
                              media=FSInputFile(path=os.path.join(all_media_dir, f'photo_520866262307424674{d}_x.jpg')))
              for d in ['5', '6', '7', '8', '9']]
    media1.insert(0, InputMediaPhoto(type='photo',
                              media=FSInputFile(path=os.path.join(all_media_dir, f'photo_5208662623074246744_x.jpg')),
                              caption=msg.start_msg_user))
    media2 = [InputMediaPhoto(type='photo',
                              media=FSInputFile(path=os.path.join(all_media_dir, f'photo_520866262307424676{d}_y.jpg')))
              for d in ['0', '1', '2', '3', '4']]
    media2.insert(0, InputMediaPhoto(type='photo',
                                media=FSInputFile(path=os.path.join(all_media_dir, f'photo_5208662623074246759_y.jpg')),
                                caption=msg.start_msg_user_2))
    await message.answer_media_group(media=media1)
    await message.answer_media_group(media=media2)

    video_file = FSInputFile(path=os.path.join(all_media_dir, 'IMG_0138.MP4'))
    await message.answer_video(video=video_file, reply_markup=kb.should_sabs,
                               caption=msg.send_video)


@router.message(F.text == '/admin')
async def start_fnc(message):
    if message.from_user.id in ADMIN_LIST:
        await utils.cr_table_users(message=message)
        await utils.cr_table_keywords()
        await utils.cr_tmp_table_id()
        await bot.send_message(chat_id=message.from_user.id, text=msg.start_msg_admin,
                               reply_markup=kb.admin_menu_main)


@router.message(F.video)
async def pay_fnc(message: Message):
    print('Видео получил')
    chat_id = message.chat.id
    video = message.video

    uploaded_video = await bot.send_video(chat_id=chat_id, video=video.file_id)
    uploaded_video_id = uploaded_video.video.file_id
    await bot.send_message(chat_id=message.from_user.id, text=uploaded_video_id)


@router.callback_query(lambda callback_query: callback_query.data.startswith('1_pay'))
async def pay_fnc(message: Message):
    await bot.send_message(chat_id=message.from_user.id, text="Выберите период на который вы хотите оплатить",
                           reply_markup=kb.choice_paydate)


#   админская часть
@router.callback_query(lambda callback_query: callback_query.data.startswith('run_pars'))
async def run_pars(message: Message):
    while True:
        try:
            await pars()
        except Exception as e:
            logger.critical(f"В pars() Произошла ошибка! Бот будет перезапущен автоматически\n{e}")


class Mailing(StatesGroup):
    message = State()


@router.callback_query(lambda callback_query: callback_query.data.startswith('рассылка'))
async def mailing(message: Message, state: FSMContext):
    await state.set_state(Mailing.message)
    await bot.send_message(chat_id=message.from_user.id, text=msg.mailing)


@router.message(Mailing.message)
async def upd_key_words_2(message: Message, state: FSMContext):
    message = message.text
    p_tag_clearing = message.replace('<p>', '').replace('</p>', '')
    ol_tag_clearing = p_tag_clearing.replace('<ol>', '').replace('</ol>', '')
    final_text = ol_tag_clearing.replace('<li>', '').replace('</li>', '')
    
    user_list = await som.get_user_list()
    for user in user_list:
        try:
            await bot.send_message(chat_id=user, text=final_text, parse_mode=ParseMode.HTML)
        except:
            continue


class FileBox(StatesGroup):
    file = State()
    document_name = State()
    file_path = State()


@router.callback_query(lambda callback_query: callback_query.data.startswith('upd_key_words'))
async def upd_key_words(message: Message, state: FSMContext):
    logger.debug('Начал обновление ключей')
    await state.set_state(FileBox.file)
    await bot.send_message(chat_id=message.from_user.id, text=msg.upd_key_words)


@router.message(FileBox.file)
async def upd_key_words_2(message: Message, state: FSMContext):
    await state.update_data(file=message.document)

    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    document_name = message.document.file_name

    await bot.download_file(file_path, document_name)
    await utils.pars_msg_keyword(document_name, message, bot)
    logger.debug(f'Хендлер register_next_step_handler отработал')


@router.callback_query(lambda callback_query: callback_query.data.startswith('report_users'))
async def upd_key_words(message: Message):
    if message.from_user.id in ADMIN_LIST:
        len_of_records = await som.report_users()

        await bot.send_document(chat_id=message.from_user.id, document=FSInputFile(path=f'report.xlsx'),
                                caption=f'Всего {len_of_records} переходов. '
                                        f'Отчет по статистике пользователей в прикрепленном файле')


@router.callback_query(lambda callback_query: callback_query.data.startswith('product_count'))
async def product_count(message: Message):
    cnt_product = await db_users.get_cnt_products()
    await bot.send_message(chat_id=message.from_user.id, text=f"На текущий момент в БД {cnt_product[0][0]} товаров")


# клиентская часть
@router.callback_query(lambda callback_query: callback_query.data.startswith('save_id'))
async def save_id(message: Message):
    if await utils.get_user_status(message.from_user.id) == 'new':
        await db_users.upd_element_in_column(table_name='users', set_upd_par_name='payment_date',
                                             set_key_par_name=utils.get_free_date(), upd_column_name='from_user_id',
                                             key_column_name=message.from_user.id)
        await db_users.upd_element_in_column(table_name='users', set_upd_par_name='status', set_key_par_name='old',
                                             upd_column_name='from_user_id', key_column_name=message.from_user.id)
        # await bot.send_message(chat_id=message.from_user.id, text=msg.save_id_msg)
        # await asyncio.sleep(1)
        # await bot.send_message(chat_id=message.from_user.id, text=msg.info_msg)


class PayApprove(StatesGroup):
    screen_check = State()
    last_period = State()


async def wait_for_media_timeout(callback: types.CallbackQuery, state: FSMContext):
    await asyncio.sleep(60*60)  # Ожидание 1 час
    current_state = await state.get_state()  # Получаем текущее состояние
    if current_state == PayApprove.screen_check:  # Если состояние не изменилось
        await bot.send_message(chat_id=callback.from_user.id,
                               text="Остался <b>1</b> шаг до оформления подписки!🎁"
                                    "\nДля активации пришлите <b>фотографию чека</b> об оплате и все начнет работать📲",
                               parse_mode=ParseMode.HTML)
        await state.clear()  # Сбрасываем состояние после таймаута


@router.callback_query(lambda callback_query: callback_query.data.startswith('paydate'))
async def pay_date(callback: types.CallbackQuery, state: FSMContext):
    last_period = callback.data.split('::')[1]
    if last_period == '14':
        price_day = pay_14
    elif last_period == '30':
        price_day = pay_30
    elif last_period == '90':
        price_day = pay_90
    else:
        price_day = 0

    await state.update_data(last_period=last_period)
    logger.warning(f"Клиент {callback.from_user.username} производит оплату 129 рублей")
    
    user_exists = await db_users.find_elements_in_column('users', callback.from_user.id, 'from_user_id')
    
    if not user_exists:
        await utils.cr_table_users(callback)
        logger.info(f"Добавлен новый пользователь: {callback.from_user.username} (ID: {callback.from_user.id})")

    await db_users.upd_element_in_column(table_name='users', set_upd_par_name='last_period',
                                         set_key_par_name=last_period, upd_column_name='from_user_id',
                                         key_column_name=callback.from_user.id)
    await bot.send_message(chat_id=callback.from_user.id, text=msg.pay_req.format(price=price_day, period=last_period),
                           parse_mode=ParseMode.HTML)
    await state.set_state(PayApprove.screen_check)
    await asyncio.create_task(wait_for_media_timeout(callback, state))


@router.message(F.text == '/pay')
async def pay_fnc(message: Message):
    await bot.send_message(chat_id=message.from_user.id, text="Нажмите на кнопку ниже, чтобы оплатить",
                           reply_markup=kb.pay)


@router.message(PayApprove.screen_check)
async def get_pay_screen(message: Message, state: FSMContext):
    await state.update_data(screen_check=message.photo)

    await db_users.upd_element_in_column(table_name='users', set_upd_par_name='payment_date',
                                         set_key_par_name=utils.get_free_date(), upd_column_name='from_user_id',
                                         key_column_name=message.from_user.id)
    await db_users.upd_element_in_column(table_name='users', set_upd_par_name='status', set_key_par_name='old',
                                         upd_column_name='from_user_id', key_column_name=message.from_user.id)

    last_period = await utils.get_last_period(user_id=message.from_user.id)

    text = f"""Оплата до ⤵️
                Дата {await utils.upd_pay_date(day=last_period)}
                ID {message.from_user.id}
                Username {message.from_user.username}
                """

    photo = message.photo[-1].file_id

    """!!!!"""
    await bot.send_photo(chat_id=LOG_GROUP, photo=photo, caption=text, reply_markup=kb.otmena_pay(message.from_user.id))
    # await bot.send_photo(chat_id=DEVELOPER, photo=photo, caption=text, reply_markup=kb.otmena_pay(message.from_user.id))
    """!!!!"""
    await bot.send_message(chat_id=message.from_user.id, text=msg.pay_confirmation, parse_mode=ParseMode.HTML)
    video_id = 'BAACAgIAAxkDAAEI_fxmmm0jua-VOy0UGH78_m7Gg-qwmwACwVUAAm3B2EhJ5IVbwZYgBzUE'
    # async with ChatActionSender.upload_video(bot=bot, chat_id=message.from_user.id):
    #     await bot.send_video(chat_id=message.from_user.id, video=video_id, caption=msg.pay_success_2)

    await db_users.upd_element_in_column(table_name='users', set_upd_par_name='payment_date',
                                         set_key_par_name=await utils.upd_pay_date(day=last_period),
                                         upd_column_name='from_user_id', key_column_name=message.from_user.id)


@router.callback_query(lambda callback_query: callback_query.data.startswith('otmena_pay'))
async def otmena_pay(message: Message):
    user_id = message.data.split('::')[1]
    await db_users.upd_element_in_column(table_name='users', set_upd_par_name='payment_date', set_key_par_name='None',
                                         upd_column_name='from_user_id', key_column_name=int(user_id))
    text = f"""Оплата для пользователя {user_id} отменена Дата {await utils.get_msk_time()}"""
    await bot.send_message(chat_id=LOG_GROUP, text=text)


@router.callback_query(lambda callback_query: callback_query.data.startswith('back'))
async def back(message: Message):
    await bot.send_message(chat_id=message.from_user.id, text=msg.start_msg_user, reply_markup=kb.user_menu_main())
