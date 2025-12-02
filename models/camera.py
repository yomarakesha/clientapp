"""
Модель камеры
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Camera:
    """Класс для представления камеры видеонаблюдения"""
    
    id: str
    name: str
    rtsp_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    group: Optional[str] = None
    position: Optional[int] = None
    enabled: bool = True
    
    def get_full_rtsp_url(self) -> str:
        """
        Получение полного RTSP URL с учетом логина и пароля
        
        Returns:
            Полный RTSP URL
        """
        if self.username and self.password:
            # Разбираем URL на части
            if "://" in self.rtsp_url:
                protocol, rest = self.rtsp_url.split("://", 1)
                return f"{protocol}://{self.username}:{self.password}@{rest}"
            else:
                return f"rtsp://{self.username}:{self.password}@{self.rtsp_url}"
        return self.rtsp_url
        
    def to_dict(self) -> dict:
        """
        Преобразование объекта в словарь
        
        Returns:
            Словарь с данными камеры
        """
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Camera':
        """
        Создание объекта Camera из словаря
        
        Args:
            data: Словарь с данными камеры
            
        Returns:
            Объект Camera
        """
        return cls(**data)
