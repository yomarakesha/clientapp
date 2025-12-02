"""
Виджет сетки для отображения нескольких камер
"""
from PyQt6.QtWidgets import QWidget, QGridLayout
from PyQt6.QtCore import pyqtSignal
from ui.video_widget import VideoWidget
from typing import Dict, List
from models.camera import Camera
import math


class GridWidget(QWidget):
    """Виджет сетки для отображения множества камер"""
    
    # Сигналы
    camera_clicked = pyqtSignal(str)  # camera_id
    camera_double_clicked = pyqtSignal(str)  # camera_id для полноэкранного режима
    
    # Поддерживаемые раскладки (количество ячеек)
    LAYOUTS = [1, 4, 9, 16, 25, 36, 64, 100]
    
    def __init__(self, layout_size: int = 4):
        """
        Инициализация сетки
        
        Args:
            layout_size: Количество ячеек в сетке (1, 4, 9, 16, 25, 36, 64, 100)
        """
        super().__init__()
        
        if layout_size not in self.LAYOUTS:
            layout_size = 4  # По умолчанию 2x2
            
        self.layout_size = layout_size
        self.video_widgets: List[VideoWidget] = []
        self.camera_widget_map: Dict[str, VideoWidget] = {}
        
        self._init_ui()
        
    def _init_ui(self):
        """Инициализация UI"""
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(self.grid_layout)
        self._create_grid()
        
    def _create_grid(self):
        """Создание сетки виджетов"""
        # Очищаем существующие виджеты
        self._clear_grid()
        
        # Вычисляем размеры сетки
        grid_size = int(math.sqrt(self.layout_size))
        
        # Создаем виджеты
        for i in range(self.layout_size):
            row = i // grid_size
            col = i % grid_size
            
            video_widget = VideoWidget()
            video_widget.clicked.connect(self._on_camera_clicked)
            video_widget.double_clicked.connect(self._on_camera_double_clicked)
            
            self.video_widgets.append(video_widget)
            self.grid_layout.addWidget(video_widget, row, col)
            
    def _clear_grid(self):
        """Очистка сетки"""
        # Удаляем все виджеты из layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        self.video_widgets.clear()
        self.camera_widget_map.clear()
        
    def set_layout(self, layout_size: int):
        """
        Установка размера сетки
        
        Args:
            layout_size: Новый размер сетки
        """
        if layout_size not in self.LAYOUTS:
            return
            
        if layout_size != self.layout_size:
            self.layout_size = layout_size
            self._create_grid()
            
    def add_camera_to_position(self, camera: Camera, position: int):
        """
        Добавление камеры на определенную позицию
        
        Args:
            camera: Объект камеры
            position: Позиция в сетке (0-based)
        """
        if position < 0 or position >= len(self.video_widgets):
            return
            
        video_widget = self.video_widgets[position]
        video_widget.set_camera(camera.id, camera.name)
        self.camera_widget_map[camera.id] = video_widget
        
    def remove_camera(self, camera_id: str):
        """
        Удаление камеры из сетки
        
        Args:
            camera_id: ID камеры
        """
        if camera_id in self.camera_widget_map:
            widget = self.camera_widget_map.pop(camera_id)
            widget.clear()
            
    def update_camera_frame(self, camera_id: str, frame):
        """
        Обновление кадра для камеры
        
        Args:
            camera_id: ID камеры
            frame: Кадр видео
        """
        if camera_id in self.camera_widget_map:
            self.camera_widget_map[camera_id].update_frame(frame)
            
    def update_camera_status(self, camera_id: str, status, error: str = ""):
        """
        Обновление статуса камеры
        
        Args:
            camera_id: ID камеры
            status: Статус подключения
            error: Сообщение об ошибке
        """
        if camera_id in self.camera_widget_map:
            self.camera_widget_map[camera_id].update_status(status, error)
            
    def load_cameras(self, cameras: List[Camera]):
        """
        Загрузка камер в сетку
        
        Args:
            cameras: Список камер
        """
        # Очищаем текущие камеры
        for widget in self.video_widgets:
            widget.clear()
        self.camera_widget_map.clear()
        
        # Добавляем камеры
        for i, camera in enumerate(cameras):
            if i >= len(self.video_widgets):
                break
                
            if camera.enabled:
                position = camera.position if camera.position is not None else i
                self.add_camera_to_position(camera, position)
                
    def get_available_positions(self) -> List[int]:
        """
        Получение списка свободных позиций
        
        Returns:
            Список индексов свободных позиций
        """
        available = []
        for i, widget in enumerate(self.video_widgets):
            if widget.camera_id is None:
                available.append(i)
        return available
        
    def get_camera_widget(self, camera_id: str) -> VideoWidget:
        """
        Получение виджета камеры
        
        Args:
            camera_id: ID камеры
            
        Returns:
            VideoWidget или None
        """
        return self.camera_widget_map.get(camera_id)
        
    def _on_camera_clicked(self, camera_id: str):
        """Обработка клика на камеру"""
        self.camera_clicked.emit(camera_id)
        
    def _on_camera_double_clicked(self, camera_id: str):
        """Обработка двойного клика на камеру"""
        self.camera_double_clicked.emit(camera_id)
        
    def clear_all(self):
        """Очистка всех камер"""
        for widget in self.video_widgets:
            widget.clear()
        self.camera_widget_map.clear()
