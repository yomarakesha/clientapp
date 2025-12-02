"""
Менеджер камер
"""
from typing import List, Optional, Dict
from models.camera import Camera
from utils.logger import logger
from utils.config import ConfigManager


class CameraManager:
    """Класс для управления камерами"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Инициализация менеджера камер
        
        Args:
            config_manager: Менеджер конфигурации
        """
        self.config_manager = config_manager
        self.cameras: Dict[str, Camera] = {}
        self._load_cameras()
        
    def _load_cameras(self):
        """Загрузка камер из конфигурации"""
        cameras_data = self.config_manager.get("cameras", [])
        for camera_data in cameras_data:
            try:
                camera = Camera.from_dict(camera_data)
                self.cameras[camera.id] = camera
            except Exception as e:
                logger.error(f"Ошибка загрузки камеры: {e}")
                
        logger.info(f"Загружено камер: {len(self.cameras)}")
        
    def _save_cameras(self):
        """Сохранение камер в конфигурацию"""
        cameras_data = [camera.to_dict() for camera in self.cameras.values()]
        self.config_manager.set("cameras", cameras_data)
        logger.info(f"Сохранено камер: {len(self.cameras)}")
        
    def add_camera(self, camera: Camera) -> bool:
        """
        Добавление камеры
        
        Args:
            camera: Объект камеры
            
        Returns:
            True если успешно, False если камера с таким ID уже существует
        """
        if camera.id in self.cameras:
            logger.warning(f"Камера с ID {camera.id} уже существует")
            return False
            
        self.cameras[camera.id] = camera
        self._save_cameras()
        logger.info(f"Добавлена камера: {camera.name} (ID: {camera.id})")
        return True
        
    def remove_camera(self, camera_id: str) -> bool:
        """
        Удаление камеры
        
        Args:
            camera_id: ID камеры
            
        Returns:
            True если успешно, False если камера не найдена
        """
        if camera_id not in self.cameras:
            logger.warning(f"Камера с ID {camera_id} не найдена")
            return False
            
        camera = self.cameras.pop(camera_id)
        self._save_cameras()
        logger.info(f"Удалена камера: {camera.name} (ID: {camera_id})")
        return True
        
    def update_camera(self, camera: Camera) -> bool:
        """
        Обновление камеры
        
        Args:
            camera: Объект камеры с обновленными данными
            
        Returns:
            True если успешно, False если камера не найдена
        """
        if camera.id not in self.cameras:
            logger.warning(f"Камера с ID {camera.id} не найдена")
            return False
            
        self.cameras[camera.id] = camera
        self._save_cameras()
        logger.info(f"Обновлена камера: {camera.name} (ID: {camera.id})")
        return True
        
    def get_camera(self, camera_id: str) -> Optional[Camera]:
        """
        Получение камеры по ID
        
        Args:
            camera_id: ID камеры
            
        Returns:
            Объект Camera или None если не найдена
        """
        return self.cameras.get(camera_id)
        
    def get_all_cameras(self) -> List[Camera]:
        """
        Получение всех камер
        
        Returns:
            Список всех камер
        """
        return list(self.cameras.values())
        
    def get_enabled_cameras(self) -> List[Camera]:
        """
        Получение включенных камер
        
        Returns:
            Список включенных камер
        """
        return [camera for camera in self.cameras.values() if camera.enabled]
        
    def get_cameras_by_group(self, group: str) -> List[Camera]:
        """
        Получение камер по группе
        
        Args:
            group: Название группы
            
        Returns:
            Список камер в группе
        """
        return [camera for camera in self.cameras.values() if camera.group == group]
        
    def get_groups(self) -> List[str]:
        """
        Получение списка всех групп
        
        Returns:
            Список названий групп
        """
        groups = set()
        for camera in self.cameras.values():
            if camera.group:
                groups.add(camera.group)
        return sorted(list(groups))
