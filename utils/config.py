"""
Менеджер конфигурации приложения
"""
import json
import os
from typing import Any, Dict
from utils.logger import logger


class ConfigManager:
    """Класс для управления конфигурацией приложения"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Инициализация менеджера конфигурации
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """
        Загрузка конфигурации из файла
        
        Returns:
            Словарь с настройками
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Конфигурация загружена из {self.config_file}")
            else:
                logger.warning(f"Файл конфигурации {self.config_file} не найден, используются значения по умолчанию")
                self.config = self._get_default_config()
                self.save_config()
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации: {e}")
            self.config = self._get_default_config()
            
        return self.config
        
    def save_config(self) -> bool:
        """
        Сохранение конфигурации в файл
        
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"Конфигурация сохранена в {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении конфигурации: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получение значения из конфигурации
        
        Args:
            key: Ключ параметра
            default: Значение по умолчанию
            
        Returns:
            Значение параметра
        """
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """
        Установка значения в конфигурации
        
        Args:
            key: Ключ параметра
            value: Новое значение
        """
        self.config[key] = value
        self.save_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Получение конфигурации по умолчанию
        
        Returns:
            Словарь с настройками по умолчанию
        """
        return {
            "cameras": [],
            "layout": 4,
            "theme": "dark",
            "language": "ru",
            "fps_limit": 15,
            "auto_reconnect": True,
            "reconnect_interval": 5
        }
