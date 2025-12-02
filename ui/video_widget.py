"""
Виджет для отображения видео с камеры
"""
import cv2
import numpy as np
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from models.stream import StreamStatus
from datetime import datetime


class VideoWidget(QWidget):
    """Виджет для отображения видео с одной камеры"""
    
    # Сигнал при клике на виджет
    clicked = pyqtSignal(str)  # camera_id
    double_clicked = pyqtSignal(str)  # camera_id для полноэкранного режима
    
    def __init__(self, camera_id: str = None, camera_name: str = "Камера"):
        """
        Инициализация виджета видео
        
        Args:
            camera_id: ID камеры
            camera_name: Название камеры
        """
        super().__init__()
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.current_frame = None
        self.status = StreamStatus.DISCONNECTED
        self.error_message = ""
        
        self._init_ui()
        
    def _init_ui(self):
        """Инициализация UI"""
        self.setMinimumSize(160, 90)  # 16:9 минимальный размер
        
        # Устанавливаем стиль
        self.setStyleSheet("""
            VideoWidget {
                background-color: #1e1e1e;
                border: 2px solid #3d3d3d;
            }
            VideoWidget:hover {
                border: 2px solid #0078d4;
            }
        """)
        
        # Label для отображения видео
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #1e1e1e;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_label)
        self.setLayout(layout)
        
        # Показываем начальное состояние
        self._show_status()
        
    def update_frame(self, frame: np.ndarray):
        """
        Обновление кадра видео
        
        Args:
            frame: Кадр в формате numpy array (BGR)
        """
        if frame is None:
            return
            
        self.current_frame = frame
        self.status = StreamStatus.CONNECTED
        
        # Конвертируем BGR в RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Создаем QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Добавляем overlay информацию
        qt_image = self._add_overlay(qt_image)
        
        # Масштабируем до размера виджета с сохранением пропорций
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.video_label.setPixmap(scaled_pixmap)
        
    def update_status(self, status: StreamStatus, error: str = ""):
        """
        Обновление статуса подключения
        
        Args:
            status: Статус подключения
            error: Сообщение об ошибке
        """
        self.status = status
        self.error_message = error
        
        if status != StreamStatus.CONNECTED:
            self._show_status()
            
    def _show_status(self):
        """Отображение статуса подключения"""
        status_text = {
            StreamStatus.DISCONNECTED: "Отключено",
            StreamStatus.CONNECTING: "Подключение...",
            StreamStatus.CONNECTED: "Подключено",
            StreamStatus.ERROR: f"Ошибка: {self.error_message}",
            StreamStatus.RECONNECTING: "Переподключение..."
        }
        
        status_color = {
            StreamStatus.DISCONNECTED: "#808080",
            StreamStatus.CONNECTING: "#ffa500",
            StreamStatus.CONNECTED: "#00ff00",
            StreamStatus.ERROR: "#ff0000",
            StreamStatus.RECONNECTING: "#ffff00"
        }
        
        text = f"{self.camera_name}\n\n{status_text.get(self.status, 'Неизвестно')}"
        color = status_color.get(self.status, "#808080")
        
        self.video_label.setText(f'<div style="color: {color};">{text}</div>')
        
    def _add_overlay(self, image: QImage) -> QImage:
        """
        Добавление overlay информации на изображение
        
        Args:
            image: Исходное изображение
            
        Returns:
            Изображение с overlay
        """
        # Создаем копию для рисования
        result = QImage(image)
        painter = QPainter(result)
        
        # Настройки шрифта
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Полупрозрачный фон для текста
        painter.fillRect(0, 0, result.width(), 30, QColor(0, 0, 0, 128))
        
        # Рисуем название камеры
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(10, 20, self.camera_name)
        
        # Рисуем время
        current_time = datetime.now().strftime("%H:%M:%S")
        time_width = painter.fontMetrics().horizontalAdvance(current_time)
        painter.drawText(result.width() - time_width - 10, 20, current_time)
        
        # Индикатор статуса
        status_color = QColor(0, 255, 0) if self.status == StreamStatus.CONNECTED else QColor(128, 128, 128)
        painter.setBrush(status_color)
        painter.drawEllipse(result.width() - 30, 8, 14, 14)
        
        painter.end()
        return result
        
    def get_screenshot(self) -> np.ndarray:
        """
        Получение скриншота текущего кадра
        
        Returns:
            Текущий кадр или None
        """
        return self.current_frame
        
    def set_camera(self, camera_id: str, camera_name: str):
        """
        Установка камеры для виджета
        
        Args:
            camera_id: ID камеры
            camera_name: Название камеры
        """
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.current_frame = None
        self.status = StreamStatus.DISCONNECTED
        self._show_status()
        
    def clear(self):
        """Очистка виджета"""
        self.camera_id = None
        self.camera_name = "Камера"
        self.current_frame = None
        self.status = StreamStatus.DISCONNECTED
        self.video_label.clear()
        self._show_status()
        
    def mousePressEvent(self, event):
        """Обработка клика мыши"""
        if self.camera_id:
            self.clicked.emit(self.camera_id)
            
    def mouseDoubleClickEvent(self, event):
        """Обработка двойного клика"""
        if self.camera_id:
            self.double_clicked.emit(self.camera_id)
