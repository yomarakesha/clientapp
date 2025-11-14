"""
MediaMTX Client (Python + PyQt5 + OpenCV)

Single-file working client application.
Features:
- Grid view of cameras (configurable 1..16)
- Add / Remove cameras (saved in cameras.json)
- Start / Stop individual cameras and Start/Stop all
- Snapshot (save PNG) per camera
- Record stream to MP4 per camera (mp4v codec)
- Archive tab: open local video file or RTSP URL and play back
- Reconnect logic for unstable streams

Requirements:
    pip install opencv-python PyQt5 numpy

Run:
    python mediamtx_client.py

Build to exe (optional):
    pip install pyinstaller
    pyinstaller --onefile --add-data "cameras.json;." mediamtx_client.py

Notes / limitations:
- OpenCV's VideoCapture for RTSP is not as reliable as VLC/FFmpeg for some streams.
  If you see instability, consider switching to python-vlc or LibVLCSharp in a later version.
- Audio is not handled.

"""

import sys
import os
import json
import cv2
import time
import threading
from datetime import datetime
from queue import Queue

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

CAMERAS_FILE = "cameras.json"
RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Helper: load / save camera config
# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# Video worker thread: reads frames from a source and emits via signal
# -----------------------------------------------------------------------------

class VideoWorker(QtCore.QThread):
    frame_ready = QtCore.pyqtSignal(np.ndarray)
    status_changed = QtCore.pyqtSignal(str)

    def __init__(self, source, name="camera"):
        super().__init__()
        self.source = source
        self.name = name
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._pause.clear()
        self.cap = None
        self.reopen_delay = 2.0

    def run(self):
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

            ret, frame = self.cap.read()
            if not ret or frame is None:
                # try reconnect
                self.status_changed.emit("no_signal")
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None
                time.sleep(self.reopen_delay)
                continue

            # emit frame
            self.frame_ready.emit(frame)

            # small sleep to avoid CPU spin; framerate is controlled by capture
            if self._pause.is_set():
                time.sleep(0.1)

        # cleanup
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

# -----------------------------------------------------------------------------
# Camera widget: shows single camera, buttons for snapshot/record
# -----------------------------------------------------------------------------

class CameraWidget(QtWidgets.QFrame):
    def __init__(self, cam_cfg=None, parent=None):
        super().__init__(parent)
        self.cam_cfg = cam_cfg or {"name": "Camera", "url": ""}
        self.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        self.setStyleSheet("background: #000;")

        self.video_label = QtWidgets.QLabel("No stream")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.name_label = QtWidgets.QLabel(self.cam_cfg.get("name", "Camera"))
        self.status_label = QtWidgets.QLabel("stopped")

        self.play_btn = QtWidgets.QPushButton("▶")
        self.stop_btn = QtWidgets.QPushButton("⏹")
        self.snap_btn = QtWidgets.QPushButton("📸")
        self.rec_btn = QtWidgets.QPushButton("● Rec")

        self.rec_btn.setCheckable(True)
        self.play_btn.setToolTip("Start stream")
        self.stop_btn.setToolTip("Stop stream")
        self.snap_btn.setToolTip("Snapshot")
        self.rec_btn.setToolTip("Start/Stop recording")

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.snap_btn)
        btn_layout.addWidget(self.rec_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.name_label)
        vbox.addWidget(self.video_label)
        vbox.addWidget(self.status_label)
        vbox.addLayout(btn_layout)
        self.setLayout(vbox)

        # video worker and recording
        self.worker = None
        self.recording = False
        self.writer = None
        self.frame_size = None
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        # signals
        self.play_btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.snap_btn.clicked.connect(self.snapshot)
        self.rec_btn.clicked.connect(self.toggle_record)

    def start(self):
        if not self.cam_cfg.get("url"):
            QtWidgets.QMessageBox.warning(self, "No URL", "Camera URL is empty")
            return
        if self.worker is not None and self.worker.isRunning():
            return
        self.worker = VideoWorker(self.cam_cfg.get("url"), name=self.cam_cfg.get("name", "cam"))
        self.worker.frame_ready.connect(self.on_frame)
        self.worker.status_changed.connect(self.on_status)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        if self.recording:
            self._stop_recording()
        self.video_label.setText("Stopped")
        self.status_label.setText("stopped")

    def on_status(self, s):
        self.status_label.setText(s)

    def on_frame(self, frame: np.ndarray):
        # convert to QImage
        h, w = frame.shape[:2]
        self.frame_size = (w, h)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QtGui.QImage(rgb.data, w, h, 3*w, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(image)
        self.video_label.setPixmap(pix.scaled(self.video_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        # recording
        if self.recording and self.writer is not None:
            try:
                self.writer.write(frame)
            except Exception as e:
                print("Write error:", e)

    def snapshot(self):
        # save current pixmap
        pix = self.video_label.pixmap()
        if pix is None:
            QtWidgets.QMessageBox.information(self, "Snapshot", "No frame to save")
            return
        filename = os.path.join(RECORDINGS_DIR, f"snapshot_{self.cam_cfg.get('name','cam')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        pix.save(filename)
        QtWidgets.QMessageBox.information(self, "Snapshot", f"Saved to {filename}")

    def toggle_record(self, checked):
        if checked:
            self._start_recording()
            self.rec_btn.setText("■ Rec")
        else:
            self._stop_recording()
            self.rec_btn.setText("● Rec")

    def _start_recording(self):
        if self.frame_size is None:
            QtWidgets.QMessageBox.information(self, "Record", "No frames yet. Start the stream first.")
            self.rec_btn.setChecked(False)
            return
        fname = os.path.join(RECORDINGS_DIR, f"{self.cam_cfg.get('name','cam')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        w, h = self.frame_size
        try:
            self.writer = cv2.VideoWriter(fname, self.fourcc, 20.0, (w, h))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Record", f"Failed to start recording: {e}")
            self.rec_btn.setChecked(False)
            return
        self.recording = True
        QtWidgets.QMessageBox.information(self, "Record", f"Recording started: {fname}")

    def _stop_recording(self):
        self.recording = False
        if self.writer:
            try:
                self.writer.release()
            except Exception:
                pass
            self.writer = None
        QtWidgets.QMessageBox.information(self, "Record", "Recording stopped")

    def close(self):
        self.stop()

# -----------------------------------------------------------------------------
# Main application window
# -----------------------------------------------------------------------------

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediaMTX Client - Python")
        self.resize(1200, 800)

        self.cameras = load_cameras()

        central = QtWidgets.QWidget()
        main_v = QtWidgets.QVBoxLayout()

        # toolbar
        toolbar = QtWidgets.QHBoxLayout()
        self.add_cam_btn = QtWidgets.QPushButton("+ Add camera")
        self.remove_cam_btn = QtWidgets.QPushButton("- Remove selected")
        self.start_all_btn = QtWidgets.QPushButton("▶ Start all")
        self.stop_all_btn = QtWidgets.QPushButton("⏹ Stop all")
        self.grid_spin = QtWidgets.QSpinBox(); self.grid_spin.setRange(1,16); self.grid_spin.setValue(4)
        self.grid_label = QtWidgets.QLabel("Grid cells:")

        toolbar.addWidget(self.add_cam_btn)
        toolbar.addWidget(self.remove_cam_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.grid_label)
        toolbar.addWidget(self.grid_spin)
        toolbar.addWidget(self.start_all_btn)
        toolbar.addWidget(self.stop_all_btn)

        main_v.addLayout(toolbar)

        # tabs
        self.tabs = QtWidgets.QTabWidget()
        self.online_tab = QtWidgets.QWidget()
        self.archive_tab = QtWidgets.QWidget()
        self.tabs.addTab(self.online_tab, "Online")
        self.tabs.addTab(self.archive_tab, "Archive")

        main_v.addWidget(self.tabs)

        # online layout: left list + grid
        online_layout = QtWidgets.QHBoxLayout()

        # left: list of cameras
        left_v = QtWidgets.QVBoxLayout()
        self.cam_list = QtWidgets.QListWidget()
        left_v.addWidget(QtWidgets.QLabel("Cameras"))
        left_v.addWidget(self.cam_list)
        online_layout.addLayout(left_v, 1)

        # right: grid area
        self.grid_widget = QtWidgets.QWidget()
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        online_layout.addWidget(self.grid_widget, 4)

        self.online_tab.setLayout(online_layout)

        # archive tab
        archive_layout = QtWidgets.QVBoxLayout()
        arch_top = QtWidgets.QHBoxLayout()
        self.open_file_btn = QtWidgets.QPushButton("Open file or URL")
        self.play_file_btn = QtWidgets.QPushButton("▶ Play")
        self.stop_file_btn = QtWidgets.QPushButton("⏹ Stop")
        arch_top.addWidget(self.open_file_btn)
        arch_top.addWidget(self.play_file_btn)
        arch_top.addWidget(self.stop_file_btn)
        archive_layout.addLayout(arch_top)

        self.archive_player = CameraWidget({"name": "Archive", "url": ""})
        archive_layout.addWidget(self.archive_player)
        self.archive_tab.setLayout(archive_layout)

        central.setLayout(main_v)
        self.setCentralWidget(central)

        # camera widgets store
        self.cam_widgets = []

        # connections
        self.add_cam_btn.clicked.connect(self.add_camera_dialog)
        self.remove_cam_btn.clicked.connect(self.remove_selected_camera)
        self.start_all_btn.clicked.connect(self.start_all)
        self.stop_all_btn.clicked.connect(self.stop_all)
        self.grid_spin.valueChanged.connect(self.rebuild_grid)
        self.cam_list.itemSelectionChanged.connect(self.on_selection_changed)

        self.open_file_btn.clicked.connect(self.open_file_dialog)
        self.play_file_btn.clicked.connect(self.play_archive)
        self.stop_file_btn.clicked.connect(self.stop_archive)

        # populate
        self.populate_cam_list()
        self.rebuild_grid()

    # ---------------- cameras management ----------------
    def populate_cam_list(self):
        self.cam_list.clear()
        for c in self.cameras:
            item = QtWidgets.QListWidgetItem(f"{c.get('name')} — {c.get('url')}")
            item.setData(QtCore.Qt.UserRole, c)
            self.cam_list.addItem(item)

    def add_camera_dialog(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Add camera")
        v = QtWidgets.QFormLayout(dlg)
        name = QtWidgets.QLineEdit()
        url = QtWidgets.QLineEdit()
        name.setText(f"cam{len(self.cameras)+1}")
        v.addRow("Name:", name)
        v.addRow("RTSP/URL:", url)
        btns = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        box = QtWidgets.QDialogButtonBox(btns)
        v.addWidget(box)
        box.accepted.connect(dlg.accept)
        box.rejected.connect(dlg.reject)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            cam = {"name": name.text().strip(), "url": url.text().strip()}
            self.cameras.append(cam)
            save_cameras(self.cameras)
            self.populate_cam_list()
            self.rebuild_grid()

    def remove_selected_camera(self):
        sel = self.cam_list.currentItem()
        if not sel:
            return
        c = sel.data(QtCore.Qt.UserRole)
        self.cameras = [x for x in self.cameras if x != c]
        save_cameras(self.cameras)
        self.populate_cam_list()
        self.rebuild_grid()

    # ---------------- grid ----------------
    def rebuild_grid(self):
        # clear
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.cam_widgets = []

        cells = self.grid_spin.value()
        cols = int(np.ceil(np.sqrt(cells)))
        rows = int(np.ceil(cells / cols))

        # fill with camera widgets or placeholders
        for i in range(cells):
            if i < len(self.cameras):
                cfg = self.cameras[i]
                w = CameraWidget(cfg)
            else:
                w = CameraWidget({"name": f"Empty {i+1}", "url": ""})
            self.cam_widgets.append(w)
            r = i // cols
            c = i % cols
            self.grid_layout.addWidget(w, r, c)

    def on_selection_changed(self):
        # select camera in grid
        sel = self.cam_list.currentItem()
        if not sel:
            return
        c = sel.data(QtCore.Qt.UserRole)
        for w in self.cam_widgets:
            if w.cam_cfg.get('url') == c.get('url'):
                w.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
                w.setLineWidth(2)
            else:
                w.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
                w.setLineWidth(1)

    def start_all(self):
        for w in self.cam_widgets:
            if w.cam_cfg.get('url'):
                w.start()

    def stop_all(self):
        for w in self.cam_widgets:
            w.stop()

    # ---------------- archive ----------------
    def open_file_dialog(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open video or enter URL", "", "Videos (*.mp4 *.mkv *.avi);;All files (*)")
        if path:
            self.archive_player.cam_cfg['url'] = path
            self.archive_player.name_label.setText(os.path.basename(path))

    def play_archive(self):
        url = self.archive_player.cam_cfg.get('url')
        if not url:
            # maybe text in name_label
            QtWidgets.QMessageBox.information(self, "Archive", "Choose a file or set a URL first")
            return
        self.archive_player.stop()
        self.archive_player.cam_cfg['url'] = url
        self.archive_player.start()

    def stop_archive(self):
        self.archive_player.stop()

    # ---------------- cleanup ----------------
    def closeEvent(self, event):
        for w in self.cam_widgets:
            w.close()
        self.archive_player.close()
        event.accept()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
