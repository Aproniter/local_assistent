from loguru import logger

logger.add(
    'logs/debug.log',
    format='{time} {level} {message}',
    level='DEBUG',
    rotation='12:00',
    compression='zip'
)