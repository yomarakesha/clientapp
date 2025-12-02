"""
Модель потока видео
"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class StreamStatus(Enum):
    """Статусы потока видео"""
    DISCONNECTED = "disconnected"  # Отключено
    CONNECTING = "connecting"      # Подключение
    CONNECTED = "connected"        # Подключено
    ERROR = "error"                # Ошибка
    RECONNECTING = "reconnecting"  # Переподключение


@dataclass
class Stream:
    """Класс для представления видеопотока"""
    
    camera_id: str
    status: StreamStatus = StreamStatus.DISCONNECTED
    error_message: Optional[str] = None
    last_frame_time: Optional[datetime] = None
    reconnect_attempts: int = 0
    fps: float = 0.0
    
    def update_status(self, status: StreamStatus, error: Optional[str] = None) -> None:
        """
        Обновление статуса потока
        
        Args:
            status: Новый статус
            error: Сообщение об ошибке (опционально)
        """
        self.status = status
        self.error_message = error
        
        if status == StreamStatus.CONNECTED:
            self.reconnect_attempts = 0
            self.error_message = None
        elif status == StreamStatus.RECONNECTING:
            self.reconnect_attempts += 1
            
    def update_frame_time(self) -> None:
        """Обновление времени последнего кадра"""
        self.last_frame_time = datetime.now()
        
    def is_active(self) -> bool:
        """
        Проверка активности потока
        
        Returns:
            True если поток подключен, False в противном случае
        """
        return self.status == StreamStatus.CONNECTED
