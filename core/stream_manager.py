"""
Менеджер видеопотоков с многопоточной обработкой
"""
import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal
from models.stream import Stream, StreamStatus
from utils.logger import logger


class VideoStreamThread(QThread):
    """Поток для обработки RTSP видеопотока"""
    
    # Сигналы для передачи данных в UI поток
    frame_ready = pyqtSignal(str, object)  # (camera_id, frame)
    status_changed = pyqtSignal(str, StreamStatus, str)  # (camera_id, status, error_message)
    
    def __init__(self, camera_id: str, rtsp_url: str, fps_limit: int = 15, 
                 auto_reconnect: bool = True, reconnect_interval: int = 5):
        """
        Инициализация потока видео
        
        Args:
            camera_id: ID камеры
            rtsp_url: RTSP URL потока
            fps_limit: Ограничение FPS
            auto_reconnect: Автоматическое переподключение
            reconnect_interval: Интервал переподключения (сек)
        """
        super().__init__()
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.fps_limit = fps_limit
        self.auto_reconnect = auto_reconnect
        self.reconnect_interval = reconnect_interval
        
        self.stream = Stream(camera_id=camera_id)
        self.running = False
        self.capture = None
        
    def run(self):
        """Основной цикл потока"""
        self.running = True
        frame_delay = 1.0 / self.fps_limit if self.fps_limit > 0 else 0
        
        while self.running:
            try:
                # Подключение к потоку
                if not self.capture or not self.capture.isOpened():
                    self._connect()
                    
                if self.capture and self.capture.isOpened():
                    ret, frame = self.capture.read()
                    
                    if ret and frame is not None:
                        # Обновляем статус на подключено
                        if self.stream.status != StreamStatus.CONNECTED:
                            self.stream.update_status(StreamStatus.CONNECTED)
                            self.status_changed.emit(self.camera_id, StreamStatus.CONNECTED, "")
                            logger.info(f"Камера {self.camera_id} успешно подключена")
                        
                        # Отправляем кадр
                        self.stream.update_frame_time()
                        self.frame_ready.emit(self.camera_id, frame)
                        
                        # Ограничение FPS
                        if frame_delay > 0:
                            time.sleep(frame_delay)
                    else:
                        # Ошибка чтения кадра
                        self._handle_error("Не удалось прочитать кадр")
                        
                else:
                    time.sleep(1)  # Ждем перед повторной попыткой
                    
            except Exception as e:
                self._handle_error(f"Ошибка потока: {str(e)}")
                
        # Очистка ресурсов
        self._cleanup()
        
    def _connect(self):
        """Подключение к RTSP потоку"""
        try:
            self.stream.update_status(StreamStatus.CONNECTING)
            self.status_changed.emit(self.camera_id, StreamStatus.CONNECTING, "")
            logger.info(f"Подключение к камере {self.camera_id}: {self.rtsp_url}")
            
            self.capture = cv2.VideoCapture(self.rtsp_url)
            
            # Настройки для оптимизации
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Минимальный буфер
            self.capture.set(cv2.CAP_PROP_FPS, self.fps_limit)
            
            if not self.capture.isOpened():
                raise Exception("Не удалось открыть поток")
                
        except Exception as e:
            self._handle_error(f"Ошибка подключения: {str(e)}")
            
    def _handle_error(self, error_message: str):
        """
        Обработка ошибки
        
        Args:
            error_message: Сообщение об ошибке
        """
        logger.error(f"Камера {self.camera_id}: {error_message}")
        
        if self.auto_reconnect:
            self.stream.update_status(StreamStatus.RECONNECTING, error_message)
            self.status_changed.emit(self.camera_id, StreamStatus.RECONNECTING, error_message)
            
            # Очищаем старое подключение
            if self.capture:
                self.capture.release()
                self.capture = None
                
            # Ждем перед переподключением
            time.sleep(self.reconnect_interval)
        else:
            self.stream.update_status(StreamStatus.ERROR, error_message)
            self.status_changed.emit(self.camera_id, StreamStatus.ERROR, error_message)
            self.running = False
            
    def _cleanup(self):
        """Очистка ресурсов"""
        if self.capture:
            self.capture.release()
            self.capture = None
        logger.info(f"Поток камеры {self.camera_id} остановлен")
        
    def stop(self):
        """Остановка потока"""
        self.running = False
        self.stream.update_status(StreamStatus.DISCONNECTED)
        self.status_changed.emit(self.camera_id, StreamStatus.DISCONNECTED, "")
