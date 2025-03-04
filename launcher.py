import sys
import os
import requests
import hashlib
import json
from urllib.parse import urljoin
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QProgressBar, QHBoxLayout, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, 
                          pyqtProperty, QThread, pyqtSignal, QPoint)
from PyQt6.QtGui import (QColor, QPainter, QBrush, QLinearGradient, QFont,
                         QGuiApplication, QCursor)
from pialn_handler import PialnHandler

API_URL = "https://futureminds.pixeltoo.ru/api"

class UpdateThread(QThread):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, token, version):
        super().__init__()
        self.token = token
        self.version = version

    def run(self):
        try:
            self.status_updated.emit("Загрузка обновления...")
            download_url = urljoin(API_URL + "/", "get_code.php")
            data = {'token': self.token, 'version': self.version}
            
            with requests.post(download_url, json=data, timeout=30, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                code_content = []

                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        downloaded += len(chunk)
                        code_content.append(chunk.decode('utf-8'))
                        if total_size:
                            progress = int((downloaded / total_size) * 100)
                        else:
                            progress = 100
                        self.progress_updated.emit(progress)

                raw_data = ''.join(code_content)
                self.status_updated.emit("Проверка целостности...")

                data_json = json.loads(raw_data)
                code = data_json.get("code", "")

                PialnHandler.save_update(code)
                self.finished.emit(True, "Обновление успешно установлено!")

        except Exception as e:
            self.finished.emit(False, f"Ошибка: {str(e)}")

class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    @pyqtProperty(int)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.setValue(value)

    def setAnimatedValue(self, value):
        self.animation.stop()
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()

class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.current_version = PialnHandler.get_current_version()
        self.token = None
        self.dragging = False
        self.drag_position = QPoint()
        self.initUI()
        self.setupAnimations()
        QTimer.singleShot(100, self.check_updates)

    def initUI(self):
        self.setWindowTitle("pixeltoo Lab - Обновление")
        self.setFixedSize(600, 400)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.container = QFrame(self)
        self.container.setGeometry(20, 20, 560, 360)
        self.container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1e2e, stop:1 #2d2d44);
                border-radius: 20px;
                border: 2px solid #3d3d5f;
            }
        """)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        header = QHBoxLayout()
        self.title = QLabel("PIXELTOO LAB - ОБНОВЛЕНИЕ")
        self.title.setStyleSheet("""
            QLabel {
                color: #a0a0f0;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 2px;
            }
        """)
        
        self.close_btn = QLabel("✕")
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.setStyleSheet("""
            QLabel {
                color: #707090;
                font-size: 24px;
                padding: 5px;
                width: 40px;
                height: 40px;
            }
            QLabel:hover {
                color: #ff7070;
                background: #ffffff10;
                border-radius: 20px;
            }
        """)
        self.close_btn.mousePressEvent = lambda e: sys.exit()

        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.close_btn)

        self.status = QLabel("Инициализация системы обновлений...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #c0c0ff;
                font-size: 16px;
                min-height: 60px;
            }
        """)

        self.progress = AnimatedProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                height: 25px;
                background: #2d2d4d;
                border-radius: 12px;
                border: 1px solid #4d4d7f;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6a5af9, stop:1 #fc6c8f);
                border-radius: 12px;
            }
        """)

        self.version_label = QLabel(f"Текущая версия: {self.current_version}")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setStyleSheet("""
            QLabel {
                color: #9090c0;
                font-size: 14px;
            }
        """)

        layout.addLayout(header)
        layout.addStretch()
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        layout.addWidget(self.version_label)
        layout.addStretch()

    def setupAnimations(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(800)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.opacity_anim.start()

        self.gradient_anim = QPropertyAnimation(self, b"gradient_pos")
        self.gradient_anim.setDuration(3000)
        self.gradient_anim.setLoopCount(-1)
        self.gradient_anim.setStartValue(0)
        self.gradient_anim.setEndValue(1)
        self.gradient_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.gradient_anim.start()

    def check_updates(self):
        try:
            self.status.setText("Подключение к серверу обновлений...")
            QApplication.processEvents()

            token_url = urljoin(API_URL + "/", "get_token.php")
            response = requests.get(token_url, timeout=10)
            response.raise_for_status()
            
            self.token = response.json()['token']

            check_url = urljoin(API_URL + "/", "check_version.php")
            data = {'token': self.token, 'current_version': self.current_version}
            response = requests.post(check_url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('update_available'):
                self.status.setText(f"Доступна новая версия: {result['latest_version']}")
                self.version_label.setText(f"Текущая версия: {self.current_version} → Новая версия: {result['latest_version']}")
                QTimer.singleShot(1500, lambda: self.start_download(result['latest_version']))
            else:
                self.launch_app()
                
        except Exception as e:
            self.status.setText(f"Ошибка подключения: {str(e)}")
            QTimer.singleShot(3000, self.launch_app)

    def start_download(self, version):
        self.thread = UpdateThread(self.token, version)
        self.thread.progress_updated.connect(self.progress.setAnimatedValue)
        self.thread.status_updated.connect(self.status.setText)
        self.thread.finished.connect(self.on_download_finished)
        self.thread.start()

    def on_download_finished(self, success, message):
        if success:
            self.status.setText(message)
            self.progress.setAnimatedValue(100)
            QTimer.singleShot(3000, self.launch_app)
        else:
            self.status.setText(message)
            self.progress.setValue(0)
            QTimer.singleShot(3000, self.launch_app)


    def launch_app(self):
        self.status.setText("Запуск приложения...")
        QApplication.processEvents()
        
        self.close_launcher()
        try:
            PialnHandler.execute_pialn()
        except Exception as e:
            with open("error.txt", "w", encoding="utf-8") as f:
                f.write(f"Ошибка: {str(e)}")
            if os.name == "nt":
                os.startfile("error.txt")
            else:
                subprocess.Popen(["xdg-open", "error.txt"])

    def close_launcher(self):
        self.opacity_anim.setDirection(QPropertyAnimation.Direction.Backward)
        self.opacity_anim.start()
        self.opacity_anim.finished.connect(self.close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.container.geometry().adjusted(-10, -10, 10, 10), 25, 25)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(110, 90, 249, 30))
        gradient.setColorAt(1, QColor(252, 108, 143, 30))
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(self.rect(), 25, 25)

if __name__ == "__main__":
    from PyQt6.QtCore import Qt
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    screen = QGuiApplication.primaryScreen().geometry()
    window = Launcher()
    window.move(screen.center() - window.rect().center())
    
    window.show()
    sys.exit(app.exec())
