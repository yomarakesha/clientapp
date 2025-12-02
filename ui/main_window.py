"""
Главное окно приложения
"""
from PyQt6.QtWidgets import (QMainWindow, QToolBar, QStatusBar, QMessageBox,
                              QFileDialog, QMenu)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from ui.grid_widget import GridWidget
from ui.camera_dialog import CameraDialog
from ui.video_widget import VideoWidget
from core.camera_manager import CameraManager
from core.stream_manager import VideoStreamThread
from models.camera import Camera
from models.stream import StreamStatus
from utils.config import ConfigManager
from utils.logger import logger
from typing import Dict
import cv2
from datetime import datetime
import os


class MainWindow(QMainWindow):
    """Главное окно приложения видеонаблюдения"""
    
    def __init__(self):
        """Инициализация главного окна"""
        super().__init__()
        
        # Менеджеры
        self.config_manager = ConfigManager()
        self.camera_manager = CameraManager(self.config_manager)
        
        # Словарь активных потоков {camera_id: VideoStreamThread}
        self.active_streams: Dict[str, VideoStreamThread] = {}
        
        # Текущая раскладка
        self.current_layout = self.config_manager.get("layout", 4)
        
        # Полноэкранный режим
        self.fullscreen_widget = None
        self.is_fullscreen = False
        
        self._init_ui()
        self._load_cameras()
        
    def _init_ui(self):
        """Инициализация UI"""
        self.setWindowTitle("Клиент видеонаблюдения - MediaMTX")
        self.setMinimumSize(1280, 720)
        
        # Применяем темную тему
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QToolBar {
                background-color: #2d2d2d;
                border-bottom: 1px solid #3d3d3d;
                spacing: 3px;
                padding: 3px;
            }
            QToolButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #3d3d3d;
            }
            QToolButton:pressed {
                background-color: #0078d4;
            }
            QStatusBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-top: 1px solid #3d3d3d;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #0078d4;
            }
        """)
        
        # Создаем главный виджет - сетку
        self.grid_widget = GridWidget(self.current_layout)
        self.grid_widget.camera_clicked.connect(self._on_camera_clicked)
        self.grid_widget.camera_double_clicked.connect(self._on_camera_double_clicked)
        self.setCentralWidget(self.grid_widget)
        
        # Создаем toolbar
        self._create_toolbar()
        
        # Создаем status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()
        
    def _create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Главная панель")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Добавить камеру
        add_action = QAction("➕ Добавить камеру", self)
        add_action.setShortcut(QKeySequence("Ctrl+N"))
        add_action.triggered.connect(self._add_camera)
        toolbar.addAction(add_action)
        
        toolbar.addSeparator()
        
        # Раскладки
        layout_menu = QMenu("Раскладка", self)
        for layout_size in GridWidget.LAYOUTS:
            grid_size = int(layout_size ** 0.5)
            action = QAction(f"{grid_size}x{grid_size} ({layout_size})", self)
            action.triggered.connect(lambda checked, size=layout_size: self._change_layout(size))
            layout_menu.addAction(action)
            
        layout_action = QAction("📐 Раскладка", self)
        layout_action.setMenu(layout_menu)
        toolbar.addAction(layout_action)
        
        toolbar.addSeparator()
        
        # Запустить все потоки
        start_all_action = QAction("▶️ Запустить все", self)
        start_all_action.triggered.connect(self._start_all_streams)
        toolbar.addAction(start_all_action)
        
        # Остановить все потоки
        stop_all_action = QAction("⏹️ Остановить все", self)
        stop_all_action.triggered.connect(self._stop_all_streams)
        toolbar.addAction(stop_all_action)
        
        toolbar.addSeparator()
        
        # Скриншот
        screenshot_action = QAction("📷 Скриншот", self)
        screenshot_action.setShortcut(QKeySequence("Ctrl+S"))
        screenshot_action.triggered.connect(self._take_screenshot)
        toolbar.addAction(screenshot_action)
        
        toolbar.addSeparator()
        
        # О программе
        about_action = QAction("ℹ️ О программе", self)
        about_action.triggered.connect(self._show_about)
        toolbar.addAction(about_action)
        
    def _load_cameras(self):
        """Загрузка камер из конфигурации"""
        cameras = self.camera_manager.get_enabled_cameras()
        self.grid_widget.load_cameras(cameras)
        logger.info(f"Загружено активных камер: {len(cameras)}")
        
    def _add_camera(self):
        """Добавление новой камеры"""
        groups = self.camera_manager.get_groups()
        dialog = CameraDialog(self, groups=groups)
        
        if dialog.exec():
            camera = dialog.get_camera()
            if self.camera_manager.add_camera(camera):
                # Добавляем в сетку
                available_positions = self.grid_widget.get_available_positions()
                if available_positions:
                    position = available_positions[0] if camera.position is None else camera.position
                    self.grid_widget.add_camera_to_position(camera, position)
                    
                    # Запускаем поток
                    if camera.enabled:
                        self._start_stream(camera)
                        
                    self._update_status_bar()
                    logger.info(f"Камера '{camera.name}' добавлена")
                else:
                    QMessageBox.warning(self, "Предупреждение",
                                      "Нет свободных позиций в текущей раскладке")
            else:
                QMessageBox.warning(self, "Ошибка", 
                                  "Не удалось добавить камеру")
                
    def _change_layout(self, layout_size: int):
        """
        Изменение раскладки
        
        Args:
            layout_size: Новый размер раскладки
        """
        self.current_layout = layout_size
        self.config_manager.set("layout", layout_size)
        
        # Останавливаем все потоки
        self._stop_all_streams()
        
        # Меняем раскладку
        self.grid_widget.set_layout(layout_size)
        
        # Загружаем камеры заново
        self._load_cameras()
        
        # Запускаем потоки
        self._start_all_streams()
        
        self._update_status_bar()
        logger.info(f"Раскладка изменена на {layout_size}")
        
    def _start_stream(self, camera: Camera):
        """
        Запуск потока для камеры
        
        Args:
            camera: Объект камеры
        """
        if camera.id in self.active_streams:
            logger.warning(f"Поток для камеры {camera.id} уже запущен")
            return
            
        # Создаем поток
        fps_limit = self.config_manager.get("fps_limit", 15)
        auto_reconnect = self.config_manager.get("auto_reconnect", True)
        reconnect_interval = self.config_manager.get("reconnect_interval", 5)
        
        stream_thread = VideoStreamThread(
            camera_id=camera.id,
            rtsp_url=camera.get_full_rtsp_url(),
            fps_limit=fps_limit,
            auto_reconnect=auto_reconnect,
            reconnect_interval=reconnect_interval
        )
        
        # Подключаем сигналы
        stream_thread.frame_ready.connect(self._on_frame_ready)
        stream_thread.status_changed.connect(self._on_status_changed)
        
        # Запускаем поток
        stream_thread.start()
        self.active_streams[camera.id] = stream_thread
        
        logger.info(f"Запущен поток для камеры: {camera.name}")
        
    def _stop_stream(self, camera_id: str):
        """
        Остановка потока камеры
        
        Args:
            camera_id: ID камеры
        """
        if camera_id in self.active_streams:
            stream_thread = self.active_streams.pop(camera_id)
            stream_thread.stop()
            stream_thread.wait()  # Ждем завершения потока
            logger.info(f"Остановлен поток для камеры: {camera_id}")
            
    def _start_all_streams(self):
        """Запуск всех потоков"""
        cameras = self.camera_manager.get_enabled_cameras()
        for camera in cameras:
            if camera.id not in self.active_streams:
                self._start_stream(camera)
        self._update_status_bar()
        
    def _stop_all_streams(self):
        """Остановка всех потоков"""
        camera_ids = list(self.active_streams.keys())
        for camera_id in camera_ids:
            self._stop_stream(camera_id)
        self._update_status_bar()
        
    def _on_frame_ready(self, camera_id: str, frame):
        """
        Обработка нового кадра
        
        Args:
            camera_id: ID камеры
            frame: Кадр видео
        """
        self.grid_widget.update_camera_frame(camera_id, frame)
        
    def _on_status_changed(self, camera_id: str, status: StreamStatus, error: str):
        """
        Обработка изменения статуса
        
        Args:
            camera_id: ID камеры
            status: Новый статус
            error: Сообщение об ошибке
        """
        self.grid_widget.update_camera_status(camera_id, status, error)
        
    def _on_camera_clicked(self, camera_id: str):
        """Обработка клика на камеру"""
        logger.debug(f"Клик на камеру: {camera_id}")
        
    def _on_camera_double_clicked(self, camera_id: str):
        """Обработка двойного клика - полноэкранный режим"""
        if not self.is_fullscreen:
            self._enter_fullscreen(camera_id)
        else:
            self._exit_fullscreen()
            
    def _enter_fullscreen(self, camera_id: str):
        """
        Вход в полноэкранный режим
        
        Args:
            camera_id: ID камеры для полноэкранного отображения
        """
        camera = self.camera_manager.get_camera(camera_id)
        if not camera:
            return
            
        # Создаем новый виджет для полноэкранного режима
        self.fullscreen_widget = VideoWidget(camera_id, camera.name)
        
        # Подключаем к существующему потоку
        if camera_id in self.active_streams:
            stream = self.active_streams[camera_id]
            stream.frame_ready.connect(
                lambda cid, frame: self.fullscreen_widget.update_frame(frame) if cid == camera_id else None
            )
            stream.status_changed.connect(
                lambda cid, status, error: self.fullscreen_widget.update_status(status, error) if cid == camera_id else None
            )
            
        # Устанавливаем как центральный виджет
        self.setCentralWidget(self.fullscreen_widget)
        self.is_fullscreen = True
        
        logger.info(f"Полноэкранный режим для камеры: {camera.name}")
        
    def _exit_fullscreen(self):
        """Выход из полноэкранного режима"""
        if self.fullscreen_widget:
            self.fullscreen_widget.deleteLater()
            self.fullscreen_widget = None
            
        self.setCentralWidget(self.grid_widget)
        self.is_fullscreen = False
        logger.info("Выход из полноэкранного режима")
        
    def _take_screenshot(self):
        """Создание скриншота"""
        # Создаем директорию для скриншотов
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Если полноэкранный режим - скриншот одной камеры
        if self.is_fullscreen and self.fullscreen_widget:
            frame = self.fullscreen_widget.get_screenshot()
            if frame is not None:
                filename = os.path.join(screenshot_dir, f"screenshot_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                self.status_bar.showMessage(f"Скриншот сохранен: {filename}", 3000)
        else:
            # Скриншоты всех активных камер
            count = 0
            for camera_id in self.active_streams.keys():
                widget = self.grid_widget.get_camera_widget(camera_id)
                if widget:
                    frame = widget.get_screenshot()
                    if frame is not None:
                        camera = self.camera_manager.get_camera(camera_id)
                        camera_name = camera.name.replace(" ", "_") if camera else camera_id
                        filename = os.path.join(screenshot_dir, 
                                              f"screenshot_{camera_name}_{timestamp}.jpg")
                        cv2.imwrite(filename, frame)
                        count += 1
                        
            if count > 0:
                self.status_bar.showMessage(f"Сохранено скриншотов: {count}", 3000)
                logger.info(f"Сохранено скриншотов: {count}")
                
    def _update_status_bar(self):
        """Обновление статус бара"""
        total_cameras = len(self.camera_manager.get_all_cameras())
        active_cameras = len(self.active_streams)
        layout_size = int(self.current_layout ** 0.5)
        
        status_text = (f"Камер: {total_cameras} | "
                      f"Активных потоков: {active_cameras} | "
                      f"Раскладка: {layout_size}x{layout_size}")
        
        self.status_bar.showMessage(status_text)
        
    def _show_about(self):
        """Показать информацию о программе"""
        QMessageBox.about(self, "О программе",
                         "<h2>Клиент видеонаблюдения</h2>"
                         "<p>Версия 1.0</p>"
                         "<p>Приложение для просмотра RTSP потоков с MediaMTX сервера.</p>"
                         "<p>Поддержка до 100 камер одновременно.</p>"
                         "<hr>"
                         "<p><b>Горячие клавиши:</b></p>"
                         "<ul>"
                         "<li>Ctrl+N - Добавить камеру</li>"
                         "<li>Ctrl+S - Скриншот</li>"
                         "<li>Двойной клик - Полноэкранный режим</li>"
                         "</ul>")
        
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self._exit_fullscreen()
        else:
            super().keyPressEvent(event)
            
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        # Останавливаем все потоки
        self._stop_all_streams()
        logger.info("Приложение закрыто")
        event.accept()
