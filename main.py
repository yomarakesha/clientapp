import sys
import cv2
from PyQt5 import QtWidgets, QtGui, QtCore


class VideoPlayer(QtWidgets.QLabel):
    def __init__(self, rtsp_url):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.cap = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.setText("Нажмите 'Старт', чтобы начать просмотр")

    def start(self):
        self.cap = cv2.VideoCapture(self.rtsp_url)
        self.timer.start(30)

    def stop(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.setText("Поток остановлен")

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                img = QtGui.QImage(rgb.data, w, h, ch*w, QtGui.QImage.Format_RGB888)
                self.setPixmap(QtGui.QPixmap.fromImage(img))
            else:
                self.setText("Поток недоступен")


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиент MediaMTX")
        self.setGeometry(200, 200, 960, 540)

        # --- интерфейс ---
        self.tabs = QtWidgets.QTabWidget()

        self.online_tab = QtWidgets.QWidget()
        self.archive_tab = QtWidgets.QWidget()

        self.tabs.addTab(self.online_tab, "Онлайн")
        self.tabs.addTab(self.archive_tab, "Записи")

        # --- онлайн камеры ---
        self.url_input = QtWidgets.QLineEdit("rtsp://192.168.1.10:8554/camera_sub0")
        self.play_btn = QtWidgets.QPushButton("▶ Старт")
        self.stop_btn = QtWidgets.QPushButton("⏹ Стоп")
        self.viewer = VideoPlayer(self.url_input.text())

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.url_input)
        hbox.addWidget(self.play_btn)
        hbox.addWidget(self.stop_btn)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.viewer)

        self.online_tab.setLayout(vbox)

        # --- вкладка записей ---
        self.archive_path = QtWidgets.QLineEdit("C:/videos/example.mp4")
        self.archive_viewer = VideoPlayer(self.archive_path.text())
        self.archive_play = QtWidgets.QPushButton("▶ Воспроизвести запись")
        self.archive_stop = QtWidgets.QPushButton("⏹ Стоп")

        arch_h = QtWidgets.QHBoxLayout()
        arch_h.addWidget(self.archive_path)
        arch_h.addWidget(self.archive_play)
        arch_h.addWidget(self.archive_stop)

        arch_v = QtWidgets.QVBoxLayout()
        arch_v.addLayout(arch_h)
        arch_v.addWidget(self.archive_viewer)
        self.archive_tab.setLayout(arch_v)

        # --- подключение кнопок ---
        self.play_btn.clicked.connect(self.start_stream)
        self.stop_btn.clicked.connect(self.stop_stream)
        self.archive_play.clicked.connect(self.play_archive)
        self.archive_stop.clicked.connect(self.stop_archive)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def start_stream(self):
        self.viewer.rtsp_url = self.url_input.text()
        self.viewer.start()

    def stop_stream(self):
        self.viewer.stop()

    def play_archive(self):
        self.archive_viewer.rtsp_url = self.archive_path.text()
        self.archive_viewer.start()

    def stop_archive(self):
        self.archive_viewer.stop()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
