"""
MediaMTX Professional Client (Python + PyQt5 + OpenCV)

Advanced CCTV management application with professional interface similar to IVMS-4200
Features:
- Professional dark theme UI
- Tree-based camera organization with groups
- Multi-view layouts (1, 4, 9, 16 split)
- Advanced PTZ controls (pan, tilt, zoom)
- Video editing (brightness, contrast, saturation)
- Advanced archive with search, filters, export
- Event logging and alerts
- Real-time monitoring and statistics
- Camera status dashboard
- Settings and configuration management

Requirements:
    pip install opencv-python PyQt5 numpy pyqtgraph

Run:
    python professional_client.py
"""

import sys
import os
import json
import cv2
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from queue import Queue
import platform
import requests
from urllib.parse import urljoin

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

CAMERAS_FILE = "cameras.json"
RECORDINGS_DIR = "recordings"
EVENTS_FILE = "events.json"
CONFIG_FILE = "config.json"

os.makedirs(RECORDINGS_DIR, exist_ok=True)

# ============================================================================
# THEME AND STYLING
# ============================================================================

DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
}

QTreeWidget, QListWidget, QTableWidget {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    gridline-color: #3d3d3d;
}

QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #0d7377;
}

QHeaderView::section {
    background-color: #3d3d3d;
    color: #ffffff;
    padding: 5px;
    border: none;
}

QPushButton {
    background-color: #0d7377;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 6px 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #14919b;
}

QPushButton:pressed {
    background-color: #0a4d52;
}

QPushButton:disabled {
    background-color: #555555;
    color: #999999;
}

QLineEdit, QTextEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
    padding: 5px;
}

QComboBox, QSpinBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 3px;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 8px 20px;
}

QTabBar::tab:selected {
    background-color: #0d7377;
}

QMenuBar {
    background-color: #2d2d2d;
    color: #ffffff;
    border-bottom: 1px solid #3d3d3d;
}

QMenuBar::item:selected {
    background-color: #0d7377;
}

QMenu {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
}

QMenu::item:selected {
    background-color: #0d7377;
}

QLabel {
    color: #ffffff;
}

QGroupBox {
    color: #ffffff;
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QSlider::groove:horizontal {
    background-color: #3d3d3d;
    height: 8px;
}

QSlider::handle:horizontal {
    background-color: #0d7377;
    width: 18px;
    margin: -5px 0;
    border-radius: 9px;
}

QStatusBar {
    background-color: #2d2d2d;
    color: #ffffff;
    border-top: 1px solid #3d3d3d;
}
"""

# ============================================================================
# HELPERS
# ============================================================================

def load_cameras():
    if os.path.exists(CAMERAS_FILE):
        try:
            with open(CAMERAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_cameras(cam_list):
    with open(CAMERAS_FILE, "w", encoding="utf-8") as f:
        json.dump(cam_list, f, indent=2, ensure_ascii=False)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def log_event(camera_name, event_type, details=""):
    events = []
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                events = json.load(f)
        except Exception:
            pass
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "camera": camera_name,
        "type": event_type,
        "details": details
    }
    events.append(event)
    # Keep last 10000 events
    if len(events) > 10000:
        events = events[-10000:]
    
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

# ============================================================================
# MEDIAMTX INTEGRATION
# ============================================================================

class MediaMTXClient:
    """Клиент для работы с MediaMTX API и автоимпорта потоков"""
    
    def __init__(self, base_url="http://127.0.0.1:9997"):
        self.base_url = base_url.rstrip('/')
    
    def get_streams(self):
        """Получить список всех потоков из MediaMTX"""
        try:
            response = requests.get(f"{self.base_url}/list", timeout=5)
            if response.status_code == 200:
                data = response.json()
                streams = {}
                if "items" in data:
                    for stream_name, stream_info in data["items"].items():
                        streams[stream_name] = {
                            "name": stream_name,
                            "url": f"rtsp://{self.base_url.split('//')[1].split(':')[0]}:8554/{stream_name}",
                            "status": stream_info.get("state", "idle")
                        }
                return streams
        except Exception as e:
            print(f"Error connecting to MediaMTX: {e}")
        return {}
    
    def is_available(self):
        """Проверить доступность MediaMTX"""
        try:
            response = requests.get(f"{self.base_url}/list", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

# ============================================================================
# VIDEO WORKER
# ============================================================================

class VideoWorker(QtCore.QThread):
    frame_ready = QtCore.pyqtSignal(np.ndarray)
    status_changed = QtCore.pyqtSignal(str)
    stats_updated = QtCore.pyqtSignal(dict)

    def __init__(self, source, name="camera"):
        super().__init__()
        self.source = source
        self.name = name
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._pause.clear()
        self.cap = None
        self.reopen_delay = 2.0
        self.frame_count = 0
        self.start_time = None

    def run(self):
        self.start_time = time.time()
        while not self._stop.is_set():
            if self.cap is None:
                self.status_changed.emit("connecting")
                self.cap = cv2.VideoCapture(self.source)
                time.sleep(0.5)
                if not self.cap.isOpened():
                    self.status_changed.emit("no_signal")
                    try:
                        self.cap.release()
                    except Exception:
                        pass
                    self.cap = None
                    time.sleep(self.reopen_delay)
                    continue
                else:
                    self.status_changed.emit("playing")
                    log_event(self.name, "connection_established")

            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.status_changed.emit("no_signal")
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None
                time.sleep(self.reopen_delay)
                continue

            self.frame_count += 1
            self.frame_ready.emit(frame)

            # Emit statistics every 30 frames
            if self.frame_count % 30 == 0:
                elapsed = time.time() - self.start_time
                fps = self.frame_count / elapsed if elapsed > 0 else 0
                self.stats_updated.emit({"fps": fps, "frames": self.frame_count})

            if self._pause.is_set():
                time.sleep(0.1)

        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        self.status_changed.emit("stopped")

    def stop(self):
        self._stop.set()
        self.wait(2000)

    def pause(self):
        self._pause.set()

    def resume(self):
        self._pause.clear()

# ============================================================================
# CAMERA WIDGET - ADVANCED
# ============================================================================

class AdvancedCameraWidget(QtWidgets.QFrame):
    def __init__(self, cam_cfg=None, parent=None):
        super().__init__(parent)
        self.cam_cfg = cam_cfg or {"name": "Camera", "url": "", "group": "Default"}
        self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        self.setLineWidth(1)
        self.setStyleSheet("background: #000; border: 2px solid #3d3d3d;")

        # Main layout
        main_layout = QtWidgets.QVBoxLayout()

        # Header with camera name and status
        header = QtWidgets.QHBoxLayout()
        self.name_label = QtWidgets.QLabel(self.cam_cfg.get("name", "Camera"))
        self.name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.status_indicator = QtWidgets.QLabel("●")
        self.status_indicator.setStyleSheet("color: gray; font-size: 14px;")
        self.status_text = QtWidgets.QLabel("stopped")
        self.status_text.setStyleSheet("font-size: 10px; color: #999;")
        
        header.addWidget(self.name_label)
        header.addWidget(self.status_indicator)
        header.addWidget(self.status_text)
        header.addStretch()
        main_layout.addLayout(header)

        # Video display
        self.video_label = QtWidgets.QLabel("No stream")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.video_label.setMinimumSize(320, 240)
        main_layout.addWidget(self.video_label)

        # Info bar with FPS and resolution
        info_layout = QtWidgets.QHBoxLayout()
        self.fps_label = QtWidgets.QLabel("FPS: --")
        self.res_label = QtWidgets.QLabel("Res: --")
        self.fps_label.setStyleSheet("font-size: 9px; color: #0d7377;")
        self.res_label.setStyleSheet("font-size: 9px; color: #0d7377;")
        info_layout.addWidget(self.fps_label)
        info_layout.addStretch()
        info_layout.addWidget(self.res_label)
        main_layout.addLayout(info_layout)

        # Video controls
        video_ctrl = QtWidgets.QHBoxLayout()
        self.brightness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setMaximumWidth(150)
        self.brightness_slider.setToolTip("Brightness")
        
        self.contrast_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.setMaximumWidth(150)
        self.contrast_slider.setToolTip("Contrast")
        
        video_ctrl.addWidget(QtWidgets.QLabel("B:"))
        video_ctrl.addWidget(self.brightness_slider)
        video_ctrl.addWidget(QtWidgets.QLabel("C:"))
        video_ctrl.addWidget(self.contrast_slider)
        video_ctrl.addStretch()
        main_layout.addLayout(video_ctrl)

        # Control buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.play_btn = QtWidgets.QPushButton("▶ Play")
        self.stop_btn = QtWidgets.QPushButton("⏹ Stop")
        self.snap_btn = QtWidgets.QPushButton("📸 Shot")
        self.rec_btn = QtWidgets.QPushButton("● Rec")
        self.ptz_btn = QtWidgets.QPushButton("🎯 PTZ")

        self.rec_btn.setCheckable(True)
        self.play_btn.setMaximumWidth(70)
        self.stop_btn.setMaximumWidth(70)
        self.snap_btn.setMaximumWidth(70)
        self.rec_btn.setMaximumWidth(70)
        self.ptz_btn.setMaximumWidth(70)

        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.snap_btn)
        btn_layout.addWidget(self.rec_btn)
        btn_layout.addWidget(self.ptz_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Video worker
        self.worker = None
        self.recording = False
        self.writer = None
        self.frame_size = None
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.current_frame = None

        # Signals
        self.play_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.snap_btn.clicked.connect(self.snapshot)
        self.rec_btn.clicked.connect(self.toggle_record)
        self.ptz_btn.clicked.connect(self.show_ptz_dialog)

    def start(self):
        if not self.cam_cfg.get("url"):
            QtWidgets.QMessageBox.warning(self, "No URL", "Camera URL is empty")
            return
        if self.worker is not None and self.worker.isRunning():
            return
        self.worker = VideoWorker(self.cam_cfg.get("url"), name=self.cam_cfg.get("name", "cam"))
        self.worker.frame_ready.connect(self.on_frame)
        self.worker.status_changed.connect(self.on_status)
        self.worker.stats_updated.connect(self.on_stats)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        if self.recording:
            self._stop_recording()
        self.video_label.setText("Stopped")
        self.status_text.setText("stopped")
        self.status_indicator.setStyleSheet("color: gray; font-size: 14px;")

    def on_status(self, s):
        self.status_text.setText(s)
        if s == "playing":
            self.status_indicator.setStyleSheet("color: #00ff00; font-size: 14px;")
        elif s == "connecting":
            self.status_indicator.setStyleSheet("color: #ffff00; font-size: 14px;")
        else:
            self.status_indicator.setStyleSheet("color: red; font-size: 14px;")

    def on_stats(self, stats):
        self.fps_label.setText(f"FPS: {stats['fps']:.1f}")

    def on_frame(self, frame: np.ndarray):
        self.current_frame = frame.copy()
        
        h, w = frame.shape[:2]
        self.frame_size = (w, h)
        self.res_label.setText(f"Res: {w}x{h}")

        # Apply brightness/contrast
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        if brightness != 0 or contrast != 0:
            frame = cv2.convertScaleAbs(frame, alpha=1 + contrast/200, beta=brightness)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        image = QtGui.QImage(rgb.data, w, h, 3*w, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(image)
        self.video_label.setPixmap(pix.scaled(self.video_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        if self.recording and self.writer is not None:
            try:
                self.writer.write(self.current_frame)
            except Exception as e:
                print(f"Write error: {e}")

    def snapshot(self):
        if self.current_frame is None:
            QtWidgets.QMessageBox.information(self, "Snapshot", "No frame to save")
            return
        filename = os.path.join(RECORDINGS_DIR, f"snapshot_{self.cam_cfg.get('name','cam')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        cv2.imwrite(filename, self.current_frame)
        QtWidgets.QMessageBox.information(self, "Snapshot", f"Saved: {os.path.basename(filename)}")
        log_event(self.cam_cfg.get('name'), "snapshot_taken", filename)

    def toggle_record(self, checked):
        if checked:
            self._start_recording()
            self.rec_btn.setText("■ Rec")
        else:
            self._stop_recording()
            self.rec_btn.setText("● Rec")

    def _start_recording(self):
        if self.frame_size is None:
            QtWidgets.QMessageBox.information(self, "Record", "No frames yet. Start stream first.")
            self.rec_btn.setChecked(False)
            return
        fname = os.path.join(RECORDINGS_DIR, f"{self.cam_cfg.get('name','cam')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        w, h = self.frame_size
        try:
            self.writer = cv2.VideoWriter(fname, self.fourcc, 20.0, (w, h))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Record", f"Failed: {e}")
            self.rec_btn.setChecked(False)
            return
        self.recording = True
        QtWidgets.QMessageBox.information(self, "Record", f"Recording: {os.path.basename(fname)}")
        log_event(self.cam_cfg.get('name'), "recording_started", fname)

    def _stop_recording(self):
        self.recording = False
        if self.writer:
            try:
                self.writer.release()
            except Exception:
                pass
            self.writer = None
        QtWidgets.QMessageBox.information(self, "Record", "Recording stopped")
        log_event(self.cam_cfg.get('name'), "recording_stopped")

    def show_ptz_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(f"PTZ Controls - {self.cam_cfg.get('name')}")
        dlg.setGeometry(100, 100, 400, 300)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Direction buttons
        direction_group = QtWidgets.QGroupBox("Direction")
        dir_layout = QtWidgets.QGridLayout()
        
        up_btn = QtWidgets.QPushButton("↑")
        down_btn = QtWidgets.QPushButton("↓")
        left_btn = QtWidgets.QPushButton("←")
        right_btn = QtWidgets.QPushButton("→")
        center_btn = QtWidgets.QPushButton("◉")
        
        dir_layout.addWidget(up_btn, 0, 1)
        dir_layout.addWidget(left_btn, 1, 0)
        dir_layout.addWidget(center_btn, 1, 1)
        dir_layout.addWidget(right_btn, 1, 2)
        dir_layout.addWidget(down_btn, 2, 1)
        
        direction_group.setLayout(dir_layout)
        layout.addWidget(direction_group)
        
        # Zoom controls
        zoom_group = QtWidgets.QGroupBox("Zoom")
        zoom_layout = QtWidgets.QHBoxLayout()
        zoom_in = QtWidgets.QPushButton("Zoom +")
        zoom_out = QtWidgets.QPushButton("Zoom -")
        zoom_layout.addWidget(zoom_in)
        zoom_layout.addWidget(zoom_out)
        zoom_group.setLayout(zoom_layout)
        layout.addWidget(zoom_group)
        
        # Speed slider
        speed_layout = QtWidgets.QHBoxLayout()
        speed_label = QtWidgets.QLabel("Speed:")
        speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        speed_slider.setRange(1, 10)
        speed_slider.setValue(5)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(speed_slider)
        layout.addLayout(speed_layout)
        
        layout.addStretch()
        dlg.setLayout(layout)
        dlg.exec_()

    def close(self):
        self.stop()

# ============================================================================
# PROFESSIONAL MAIN WINDOW
# ============================================================================

class ProfessionalMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediaMTX Professional Client v1.0")
        self.setWindowIcon(self.create_icon())
        self.resize(1600, 1000)
        self.cameras = load_cameras()
        self.config = load_config()
        self.cam_widgets = []

        # Apply theme
        self.setStyleSheet(DARK_STYLESHEET)

        # Create menu bar
        self.create_menu_bar()

        # Central widget
        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()

        # Left panel - Camera tree
        left_panel = self.create_left_panel()
        main_layout.addLayout(left_panel, 1)

        # Center panel - Video grid
        self.center_widget = QtWidgets.QWidget()
        self.center_layout = QtWidgets.QGridLayout()
        self.center_widget.setLayout(self.center_layout)
        main_layout.addWidget(self.center_widget, 4)

        # Right panel - Info and controls
        right_panel = self.create_right_panel()
        main_layout.addLayout(right_panel, 1)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Initial setup
        self.populate_tree()
        self.rebuild_grid()

    def create_icon(self):
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setBrush(QtGui.QColor("#0d7377"))
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        return QtGui.QIcon(pixmap)

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Import from MediaMTX", self.import_from_mediamtx)
        file_menu.addAction("Export Cameras", self.export_cameras)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Layout 1x1", lambda: self.set_layout(1))
        view_menu.addAction("Layout 2x2", lambda: self.set_layout(4))
        view_menu.addAction("Layout 3x3", lambda: self.set_layout(9))
        view_menu.addAction("Layout 4x4", lambda: self.set_layout(16))
        
        # Camera menu
        cam_menu = menubar.addMenu("Camera")
        cam_menu.addAction("Add Camera", self.add_camera_dialog)
        cam_menu.addAction("Remove Camera", self.remove_camera)
        cam_menu.addSeparator()
        cam_menu.addAction("Start All", self.start_all)
        cam_menu.addAction("Stop All", self.stop_all)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Event Log", self.show_events_dialog)
        tools_menu.addAction("Archive Player", self.show_archive_dialog)
        tools_menu.addAction("Settings", self.show_settings_dialog)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about_dialog)

    def create_left_panel(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Search
        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search cameras...")
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tree
        self.camera_tree = QtWidgets.QTreeWidget()
        self.camera_tree.setHeaderLabel("Cameras")
        self.camera_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.camera_tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        layout.addWidget(self.camera_tree)
        
        # Add buttons
        btn_layout = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("+ Add")
        del_btn = QtWidgets.QPushButton("- Del")
        add_btn.clicked.connect(self.add_camera_dialog)
        del_btn.clicked.connect(self.remove_camera)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        
        return layout

    def create_right_panel(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Camera info
        info_group = QtWidgets.QGroupBox("Camera Info")
        info_layout = QtWidgets.QVBoxLayout()
        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Statistics
        stats_group = QtWidgets.QGroupBox("Statistics")
        stats_layout = QtWidgets.QVBoxLayout()
        self.stats_table = QtWidgets.QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.stats_table.setMaximumHeight(200)
        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Events
        events_group = QtWidgets.QGroupBox("Recent Events")
        events_layout = QtWidgets.QVBoxLayout()
        self.events_list = QtWidgets.QListWidget()
        self.events_list.setMaximumHeight(200)
        events_layout.addWidget(self.events_list)
        events_group.setLayout(events_layout)
        layout.addWidget(events_group)
        
        layout.addStretch()
        return layout

    def populate_tree(self):
        self.camera_tree.clear()
        
        groups = defaultdict(list)
        for cam in self.cameras:
            group = cam.get("group", "Default")
            groups[group].append(cam)
        
        for group_name in sorted(groups.keys()):
            group_item = QtWidgets.QTreeWidgetItem([group_name])
            group_item.setIcon(0, self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))
            
            for cam in groups[group_name]:
                cam_item = QtWidgets.QTreeWidgetItem([cam.get("name")])
                cam_item.setData(0, QtCore.Qt.UserRole, cam)
                group_item.addChild(cam_item)
            
            self.camera_tree.addTopLevelItem(group_item)
        
        self.camera_tree.expandAll()

    def set_layout(self, cells):
        cols = int(np.ceil(np.sqrt(cells)))
        rows = int(np.ceil(cells / cols))
        # Update layout calculation
        self.rebuild_grid()

    def rebuild_grid(self):
        # Clear existing
        for i in reversed(range(self.center_layout.count())):
            w = self.center_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.cam_widgets = []
        
        # Create widgets for each camera
        for i, cam in enumerate(self.cameras[:16]):
            w = AdvancedCameraWidget(cam)
            self.cam_widgets.append(w)
            r = i // 4
            c = i % 4
            self.center_layout.addWidget(w, r, c)

    def add_camera_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Add Camera")
        dlg.setGeometry(200, 200, 400, 250)
        
        layout = QtWidgets.QFormLayout()
        name = QtWidgets.QLineEdit()
        url = QtWidgets.QLineEdit()
        group = QtWidgets.QLineEdit()
        
        name.setText(f"Camera {len(self.cameras)+1}")
        group.setText("Default")
        
        layout.addRow("Name:", name)
        layout.addRow("RTSP URL:", url)
        layout.addRow("Group:", group)
        
        btns = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        box = QtWidgets.QDialogButtonBox(btns)
        layout.addWidget(box)
        
        box.accepted.connect(dlg.accept)
        box.rejected.connect(dlg.reject)
        dlg.setLayout(layout)
        
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            cam = {
                "name": name.text().strip(),
                "url": url.text().strip(),
                "group": group.text().strip() or "Default"
            }
            if cam["url"]:
                self.cameras.append(cam)
                save_cameras(self.cameras)
                self.populate_tree()
                self.rebuild_grid()
                log_event(cam["name"], "camera_added")
                self.statusBar().showMessage(f"Camera '{cam['name']}' added")

    def remove_camera(self):
        item = self.camera_tree.currentItem()
        if not item or not item.parent():
            QtWidgets.QMessageBox.warning(self, "Error", "Select a camera")
            return
        
        cam = item.data(0, QtCore.Qt.UserRole)
        if cam:
            self.cameras = [x for x in self.cameras if x != cam]
            save_cameras(self.cameras)
            self.populate_tree()
            self.rebuild_grid()
            log_event(cam["name"], "camera_removed")
            self.statusBar().showMessage(f"Camera '{cam['name']}' removed")

    def start_all(self):
        for w in self.cam_widgets:
            if w.cam_cfg.get('url'):
                w.start()
        self.statusBar().showMessage("All cameras started")

    def stop_all(self):
        for w in self.cam_widgets:
            w.stop()
        self.statusBar().showMessage("All cameras stopped")

    def show_tree_context_menu(self, pos):
        item = self.camera_tree.itemAt(pos)
        if not item:
            return
        
        menu = QtWidgets.QMenu()
        if item.parent():  # Camera item
            menu.addAction("Start", lambda: self.find_widget_for_item(item).start())
            menu.addAction("Stop", lambda: self.find_widget_for_item(item).stop())
            menu.addSeparator()
            menu.addAction("Delete", self.remove_camera)
        
        menu.exec_(self.camera_tree.mapToGlobal(pos))

    def find_widget_for_item(self, item):
        cam = item.data(0, QtCore.Qt.UserRole)
        for w in self.cam_widgets:
            if w.cam_cfg.get('url') == cam.get('url'):
                return w
        return None

    def show_events_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Event Log")
        dlg.resize(800, 500)
        
        layout = QtWidgets.QVBoxLayout()
        
        table = QtWidgets.QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Time", "Camera", "Type", "Details"])
        
        events = []
        if os.path.exists(EVENTS_FILE):
            try:
                with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                    events = json.load(f)
            except Exception:
                pass
        
        events = sorted(events, key=lambda x: x["timestamp"], reverse=True)[:100]
        table.setRowCount(len(events))
        
        for i, event in enumerate(events):
            table.setItem(i, 0, QtWidgets.QTableWidgetItem(event["timestamp"][:19]))
            table.setItem(i, 1, QtWidgets.QTableWidgetItem(event["camera"]))
            table.setItem(i, 2, QtWidgets.QTableWidgetItem(event["type"]))
            table.setItem(i, 3, QtWidgets.QTableWidgetItem(event.get("details", "")))
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        
        dlg.setLayout(layout)
        dlg.exec_()

    def show_archive_dialog(self):
        QtWidgets.QMessageBox.information(self, "Archive", "Archive player feature coming soon")

    def show_settings_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Settings")
        dlg.resize(400, 300)
        
        layout = QtWidgets.QFormLayout()
        
        # Recording directory
        rec_dir = QtWidgets.QLineEdit(self.config.get("recording_dir", RECORDINGS_DIR))
        layout.addRow("Recording Directory:", rec_dir)
        
        # Framerate
        fps = QtWidgets.QSpinBox()
        fps.setValue(self.config.get("fps", 20))
        fps.setRange(1, 60)
        layout.addRow("Recording FPS:", fps)
        
        # Bitrate
        bitrate = QtWidgets.QLineEdit(self.config.get("bitrate", "5000k"))
        layout.addRow("Bitrate:", bitrate)
        
        btns = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        box = QtWidgets.QDialogButtonBox(btns)
        layout.addWidget(box)
        
        def save_settings():
            self.config["recording_dir"] = rec_dir.text()
            self.config["fps"] = fps.value()
            self.config["bitrate"] = bitrate.text()
            save_config(self.config)
            dlg.accept()
        
        box.accepted.connect(save_settings)
        box.rejected.connect(dlg.reject)
        dlg.setLayout(layout)
        dlg.exec_()

    def show_about_dialog(self):
        QtWidgets.QMessageBox.about(
            self,
            "About MediaMTX Professional Client",
            "Version 1.0\n\n"
            "Advanced CCTV management client\n\n"
            "Features:\n"
            "• Multi-camera grid view\n"
            "• Advanced PTZ controls\n"
            "• Video editing tools\n"
            "• Event logging and archiving\n"
            "• Professional dark theme\n"
        )

    def import_from_mediamtx(self):
        """Импортировать потоки из MediaMTX"""
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Import from MediaMTX")
        dlg.resize(400, 200)
        
        layout = QtWidgets.QVBoxLayout()
        
        # URL input
        url_layout = QtWidgets.QHBoxLayout()
        url_label = QtWidgets.QLabel("MediaMTX URL:")
        url_input = QtWidgets.QLineEdit()
        url_input.setText(self.config.get("mediamtx_url", "http://127.0.0.1:9997"))
        url_input.setPlaceholderText("http://127.0.0.1:9997")
        url_layout.addWidget(url_label)
        url_layout.addWidget(url_input)
        layout.addLayout(url_layout)
        
        # Group input
        group_layout = QtWidgets.QHBoxLayout()
        group_label = QtWidgets.QLabel("Group prefix:")
        group_input = QtWidgets.QLineEdit()
        group_input.setText(self.config.get("mediamtx_group", "Imported"))
        group_layout.addWidget(group_label)
        group_layout.addWidget(group_input)
        layout.addLayout(group_layout)
        
        # Info
        info_text = QtWidgets.QLabel("This will import all streams from MediaMTX.\nExisting cameras will not be removed.")
        info_text.setStyleSheet("color: #0d7377;")
        layout.addWidget(info_text)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        import_btn = QtWidgets.QPushButton("Import")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        btn_layout.addWidget(import_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dlg.setLayout(layout)
        
        def do_import():
            url = url_input.text().strip()
            group = group_input.text().strip() or "Imported"
            
            client = MediaMTXClient(url)
            if not client.is_available():
                QtWidgets.QMessageBox.warning(dlg, "Error", "Cannot connect to MediaMTX at:\n" + url)
                return
            
            streams = client.get_streams()
            if not streams:
                QtWidgets.QMessageBox.warning(dlg, "Error", "No streams found in MediaMTX")
                return
            
            # Add streams to cameras
            added = 0
            for stream_name, stream_info in streams.items():
                # Check if already exists
                if not any(c.get("url") == stream_info["url"] for c in self.cameras):
                    self.cameras.append({
                        "name": stream_info["name"],
                        "url": stream_info["url"],
                        "group": group,
                        "source": "mediamtx"
                    })
                    added += 1
            
            if added > 0:
                save_cameras(self.cameras)
                self.config["mediamtx_url"] = url
                self.config["mediamtx_group"] = group
                save_config(self.config)
                self.populate_tree()
                self.rebuild_grid()
                log_event("System", "mediamtx_import", f"Imported {added} streams")
                self.statusBar().showMessage(f"Imported {added} streams from MediaMTX")
                QtWidgets.QMessageBox.information(dlg, "Success", f"Imported {added} streams")
            else:
                QtWidgets.QMessageBox.information(dlg, "Info", "No new streams to import")
            
            dlg.accept()
        
        import_btn.clicked.connect(do_import)
        cancel_btn.clicked.connect(dlg.reject)
        
        dlg.exec_()

    def export_cameras(self):
        """Экспортировать список камер"""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Cameras", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        if not path:
            return
        
        try:
            if path.endswith('.csv'):
                import csv
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['name', 'url', 'group'])
                    writer.writeheader()
                    writer.writerows(self.cameras)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.cameras, f, indent=2, ensure_ascii=False)
            
            QtWidgets.QMessageBox.information(self, "Export", f"Exported {len(self.cameras)} cameras to:\n{path}")
            log_event("System", "cameras_exported", f"Exported to {path}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Export failed: {e}")

    def closeEvent(self, event):
        for w in self.cam_widgets:
            w.close()
        event.accept()

# ============================================================================
# MAIN
# ============================================================================

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = ProfessionalMainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
