import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QTextEdit, QSpinBox, QCheckBox, QGroupBox, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
import pyautogui
from python_imagesearch.imagesearch import imagesearch
from PyQt5.QtGui import QIcon

class ImageSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.searching = False
        self.image_path = None
        self.search_thread = None
        self.delay_before_start = 0
        self.search_interval = 1
        self.search_area = None

    def initUI(self):
        self.setWindowTitle('Компьютерное зрение | AI')
        self.setGeometry(100, 100, 600, 500)
        self.setWindowIcon(QIcon('D:/Projects/BotyPython/AI/icon.ico'))  # Убедитесь, что путь к вашей иконке правильный

        # Основные элементы управления
        self.label = QLabel('Выберите изображение для поиска:', self)
        self.label.setGeometry(20, 20, 350, 20)
        
        self.selectButton = QPushButton('Выбрать изображение', self)
        self.selectButton.setGeometry(20, 60, 160, 30)
        self.selectButton.clicked.connect(self.openFileDialog)
        
        self.startButton = QPushButton('Запустить', self)
        self.startButton.setGeometry(20, 110, 120, 30)
        self.startButton.clicked.connect(self.start_search)
        
        self.stopButton = QPushButton('Остановить', self)
        self.stopButton.setGeometry(150, 110, 120, 30)
        self.stopButton.clicked.connect(self.stop_search)
        self.stopButton.setEnabled(False)

        self.statusLabel = QLabel('Статус: Ожидание', self)
        self.statusLabel.setGeometry(20, 160, 550, 20)

        # Логирование
        self.logBox = QTextEdit(self)
        self.logBox.setGeometry(20, 200, 550, 120)
        self.logBox.setReadOnly(True)

        # Таймер и задержка запуска
        self.delayGroupBox = QGroupBox('Настройки таймера и интервала', self)
        self.delayGroupBox.setGeometry(300, 20, 270, 100)

        self.delayLabel = QLabel('Задержка перед запуском (сек):', self.delayGroupBox)
        self.delaySpinBox = QSpinBox(self.delayGroupBox)
        self.delaySpinBox.setRange(0, 60)
        self.delaySpinBox.setValue(0)
        self.delaySpinBox.valueChanged.connect(self.update_delay)

        self.intervalLabel = QLabel('Интервал между попытками поиска (сек):', self.delayGroupBox)
        self.intervalSpinBox = QSpinBox(self.delayGroupBox)
        self.intervalSpinBox.setRange(1, 10)
        self.intervalSpinBox.setValue(1)
        self.intervalSpinBox.valueChanged.connect(self.update_interval)

        delayLayout = QVBoxLayout()
        delayLayout.addWidget(self.delayLabel)
        delayLayout.addWidget(self.delaySpinBox)
        delayLayout.addWidget(self.intervalLabel)
        delayLayout.addWidget(self.intervalSpinBox)
        self.delayGroupBox.setLayout(delayLayout)

        # Выбор области поиска
        self.areaGroupBox = QGroupBox('Настройки области поиска', self)
        self.areaGroupBox.setGeometry(20, 330, 270, 120)

        self.selectAreaButton = QPushButton('Установить область поиска', self.areaGroupBox)
        self.selectAreaButton.clicked.connect(self.set_search_area)
        self.clearAreaButton = QPushButton('Очистить область поиска', self.areaGroupBox)
        self.clearAreaButton.clicked.connect(self.clear_search_area)
        self.clearAreaButton.setEnabled(False)

        areaLayout = QVBoxLayout()
        areaLayout.addWidget(self.selectAreaButton)
        areaLayout.addWidget(self.clearAreaButton)
        self.areaGroupBox.setLayout(areaLayout)

        # Опция отображения найденного изображения
        self.showThumbnailCheckBox = QCheckBox('Отобразить миниатюру выбранного изображения', self)
        self.showThumbnailCheckBox.setGeometry(300, 130, 300, 20)

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filePath, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Изображения (*.png *.jpg *.bmp);;Все файлы (*)", options=options)
        if filePath:
            self.image_path = filePath
            self.label.setText(f'Выбрано изображение: {filePath}')
            self.log(f'Изображение выбрано: {filePath}')
            if self.showThumbnailCheckBox.isChecked():
                self.show_thumbnail(filePath)

    def show_thumbnail(self, filePath):
        from PyQt5.QtGui import QPixmap
        thumbnail = QLabel(self)
        pixmap = QPixmap(filePath)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        thumbnail.setPixmap(pixmap)
        thumbnail.setGeometry(200, 60, 100, 100)
        thumbnail.show()

    def start_search(self):
        if self.image_path:
            self.searching = True
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(True)
            self.statusLabel.setText('Статус: Задержка перед запуском...')
            self.log('Задержка перед запуском...')
            QTimer.singleShot(self.delay_before_start * 1000, self.start_search_thread)
        else:
            self.statusLabel.setText('Статус: Пожалуйста, сначала выберите изображение.')

    def start_search_thread(self):
        self.statusLabel.setText('Статус: Поиск изображения...')
        self.log('Поиск изображения начался...')
        self.search_thread = threading.Thread(target=self.search_image)
        self.search_thread.start()

    def stop_search(self):
        self.searching = False
        if self.search_thread:
            self.search_thread.join()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.statusLabel.setText('Статус: Остановлено')
        self.log('Поиск остановлен.')

    def search_image(self):
        while self.searching:
            if self.search_area:
                x, y, width, height = self.search_area
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
                screenshot.save('search_area.png')
                position = imagesearch('search_area.png', im=self.image_path)
            else:
                position = imagesearch(self.image_path)
            if position[0] != -1:
                pyautogui.click(position)
                self.statusLabel.setText('Статус: Изображение найдено и кликнуто')
                self.log('Изображение найдено и кликнуто')
                time.sleep(self.search_interval)  # Пауза на момент, чтобы обеспечить один клик
            else:
                self.statusLabel.setText('Статус: Изображение не найдено')
                self.log('Изображение не найдено')
            time.sleep(self.search_interval)  # Подождите перед повторным поиском

    def update_delay(self, value):
        self.delay_before_start = value

    def update_interval(self, value):
        self.search_interval = value

    def log(self, message):
        self.logBox.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def set_search_area(self):
        self.statusLabel.setText('Статус: Нажмите и перетащите, чтобы выбрать область поиска...')
        self.log('Нажмите и перетащите, чтобы выбрать область поиска...')
        self.hide()
        
        import pynput
        from pynput import mouse

        def on_click(x, y, button, pressed):
            if pressed:
                self.search_area = (x, y)
                self.statusLabel.setText(f'Статус: Область начала: ({x}, {y})')
                self.log(f'Область начала: ({x}, {y})')
            else:
                x2, y2 = pyautogui.position()
                self.search_area = (self.search_area[0], self.search_area[1], x2 - self.search_area[0], y2 - self.search_area[1])
                self.statusLabel.setText(f'Статус: Область поиска установлена: ({self.search_area})')
                self.log(f'Область поиска установлена: {self.search_area}')
                return False  # Stop listener

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

        self.show()
        self.clearAreaButton.setEnabled(True)

    def clear_search_area(self):
        self.search_area = None
        self.statusLabel.setText('Статус: Область поиска очищена')
        self.log('Область поиска очищена')
        self.clearAreaButton.setEnabled(False)

    def closeEvent(self, event):
        self.stop_search()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageSearchApp()
    window.show()
    sys.exit(app.exec_())
