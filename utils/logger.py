"""
Утилита для логирования приложения видеонаблюдения
"""
import logging
import os
from datetime import datetime


def setup_logger(name: str = "VideoClient") -> logging.Logger:
    """
    Настройка логгера приложения
    
    Args:
        name: Имя логгера
        
    Returns:
        Настроенный объект Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Создаем директорию для логов если её нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для записи в файл
    log_file = os.path.join(log_dir, f"video_client_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Глобальный логгер
logger = setup_logger()
