"""
Диалог добавления/редактирования камеры
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QLineEdit, QPushButton, QCheckBox, QComboBox,
                              QLabel, QSpinBox)
from PyQt6.QtCore import Qt
from models.camera import Camera
import uuid


class CameraDialog(QDialog):
    """Диалог для добавления или редактирования камеры"""
    
    def __init__(self, parent=None, camera: Camera = None, groups: list = None):
        """
        Инициализация диалога
        
        Args:
            parent: Родительский виджет
            camera: Объект камеры для редактирования (None для новой камеры)
            groups: Список существующих групп
        """
        super().__init__(parent)
        self.camera = camera
        self.groups = groups or []
        self.is_edit_mode = camera is not None
        
        self._init_ui()
        
        if self.is_edit_mode:
            self._load_camera_data()
            
    def _init_ui(self):
        """Инициализация UI"""
        title = "Редактировать камеру" if self.is_edit_mode else "Добавить камеру"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        # Применяем темную тему
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            QPushButton#cancelButton {
                background-color: #555555;
            }
            QPushButton#cancelButton:hover {
                background-color: #666666;
            }
            QLabel {
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
        """)
        
        # Основной layout
        main_layout = QVBoxLayout()
        
        # Форма
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Название
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название камеры")
        form_layout.addRow("Название:", self.name_input)
        
        # RTSP URL
        self.rtsp_input = QLineEdit()
        self.rtsp_input.setPlaceholderText("rtsp://server_ip:8554/stream_name")
        form_layout.addRow("RTSP URL:", self.rtsp_input)
        
        # Логин
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин (опционально)")
        form_layout.addRow("Логин:", self.username_input)
        
        # Пароль
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Пароль (опционально)")
        form_layout.addRow("Пароль:", self.password_input)
        
        # Группа
        self.group_combo = QComboBox()
        self.group_combo.setEditable(True)
        self.group_combo.addItem("")  # Пустая группа
        self.group_combo.addItems(self.groups)
        form_layout.addRow("Группа:", self.group_combo)
        
        # Позиция
        self.position_spin = QSpinBox()
        self.position_spin.setRange(0, 99)
        self.position_spin.setSpecialValueText("Автоматически")
        form_layout.addRow("Позиция:", self.position_spin)
        
        # Включена
        self.enabled_check = QCheckBox("Камера включена")
        self.enabled_check.setChecked(True)
        form_layout.addRow("", self.enabled_check)
        
        main_layout.addLayout(form_layout)
        
        # Пример URL
        example_label = QLabel(
            '<i style="color: #888888;">Пример: rtsp://192.168.1.100:8554/camera1</i>'
        )
        main_layout.addWidget(example_label)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
    def _load_camera_data(self):
        """Загрузка данных камеры для редактирования"""
        if not self.camera:
            return
            
        self.name_input.setText(self.camera.name)
        self.rtsp_input.setText(self.camera.rtsp_url)
        
        if self.camera.username:
            self.username_input.setText(self.camera.username)
        if self.camera.password:
            self.password_input.setText(self.camera.password)
        if self.camera.group:
            self.group_combo.setCurrentText(self.camera.group)
        if self.camera.position is not None:
            self.position_spin.setValue(self.camera.position)
            
        self.enabled_check.setChecked(self.camera.enabled)
        
    def get_camera(self) -> Camera:
        """
        Получение объекта камеры из формы
        
        Returns:
            Объект Camera с данными из формы
        """
        camera_id = self.camera.id if self.is_edit_mode else str(uuid.uuid4())
        
        # Получаем позицию (0 означает автоматически - None)
        position = self.position_spin.value()
        if position == 0:
            position = None
            
        return Camera(
            id=camera_id,
            name=self.name_input.text().strip(),
            rtsp_url=self.rtsp_input.text().strip(),
            username=self.username_input.text().strip() or None,
            password=self.password_input.text().strip() or None,
            group=self.group_combo.currentText().strip() or None,
            position=position,
            enabled=self.enabled_check.isChecked()
        )
        
    def accept(self):
        """Валидация перед сохранением"""
        # Проверяем обязательные поля
        if not self.name_input.text().strip():
            self.name_input.setFocus()
            return
            
        if not self.rtsp_input.text().strip():
            self.rtsp_input.setFocus()
            return
            
        super().accept()
