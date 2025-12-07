import os
from loguru import logger
# from notifiers.logging import NotificationHandler
from dotenv import load_dotenv
from config import TOKEN, LOG_GROUP


path_to_logs = fr"/home/user/PycharmProjects/TG_bot/logs"
# path_to_logs = rf"C:\Users\User\PycharmProjects\BIK_monitoring\logs"

logger.add(f'{path_to_logs}/log.log', rotation='100 MB', retention=5, level="DEBUG")
logger.add(f'{path_to_logs}/info.log', rotation='50 MB', retention=20, level="INFO")
logger.add(f'{path_to_logs}/warning.log', rotation='30 MB', retention=16, level="WARNING")
logger.add(f'{path_to_logs}/errors.log', rotation='20 MB', retention=25, level="ERROR")
logger.add(f'{path_to_logs}/critical.log', rotation='10 MB', retention=50, level="CRITICAL")


load_dotenv()

params = {
    "token": TOKEN,
    "chat_id": LOG_GROUP,
}

# tg_handler = NotificationHandler(provider='telegram', defaults=params)
# logger.add(tg_handler, level='WARNING')

if __name__ == "__main__":
    logger.debug("Уровень Debug")
    logger.info("Уровень Info")
    logger.warning("Уровень Warning")
    logger.error("Уровень Error")
    logger.critical("Уровень Critical Error")

