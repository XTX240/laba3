import sys
import os
import random
import math

from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QFileDialog, QTextBrowser,
    QRadioButton, QButtonGroup, QSlider, QInputDialog, QColorDialog
)
from PyQt5.QtCore import Qt, QPointF, QUrl
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


# =====================================================================
# Задание №1: Обработка чисел из файла (1 балл)
# =====================================================================
class Task1Widget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.btn_load = QPushButton("Загрузить файл (.txt)")
        self.btn_save = QPushButton("Сохранить результаты")

        self.lbl_min = QLabel("Минимум: -")
        self.lbl_max = QLabel("Максимум: -")
        self.lbl_avg = QLabel("Среднее: -")

        self.btn_load.clicked.connect(self.load_file)
        self.btn_save.clicked.connect(self.save_file)

        layout.addWidget(self.btn_load)
        layout.addWidget(self.lbl_min)
        layout.addWidget(self.lbl_max)
        layout.addWidget(self.lbl_avg)
        layout.addWidget(self.btn_save)
        self.setLayout(layout)

        self.min_val = None
        self.max_val = None
        self.avg_val = None

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл с числами", "",
                                                   "Text Files (*.txt);;All Files (*)")
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tokens = content.split()
            if not tokens:
                raise ValueError("Файл пуст.")

            numbers = [int(token) for token in tokens]

            self.min_val = min(numbers)
            self.max_val = max(numbers)
            self.avg_val = sum(numbers) / len(numbers)

            self.lbl_min.setText(f"Минимум: {self.min_val}")
            self.lbl_max.setText(f"Максимум: {self.max_val}")
            self.lbl_avg.setText(f"Среднее: {self.avg_val:.2f}")

        except ValueError:
            QMessageBox.critical(self, "Ошибка формата", "Файл содержит некорректные данные (не целые числа) или пуст!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл: {e}")

    def save_file(self):
        if self.min_val is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите файл с корректными числами!")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Text Files (*.txt);;All Files (*)")
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Минимальное значение: {self.min_val}\n")
                f.write(f"Максимальное значение: {self.max_val}\n")
                f.write(f"Среднее значение: {self.avg_val:.2f}\n")
            QMessageBox.information(self, "Успех", "Результаты вычислений успешно сохранены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")


# =====================================================================
# Задание №2: Простой текстовый редактор (1 балл)
# =====================================================================
class Task2Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("Создать новый")
        self.btn_open = QPushButton("Открыть")
        self.btn_save = QPushButton("Сохранить")

        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_save)

        self.text_browser = QTextBrowser()
        self.text_browser.setReadOnly(False)

        self.btn_new.clicked.connect(self.new_file)
        self.btn_open.clicked.connect(self.open_file)
        self.btn_save.clicked.connect(self.save_file)

        layout.addLayout(btn_layout)
        layout.addWidget(self.text_browser)
        self.setLayout(layout)

    def new_file(self):
        self.text_browser.clear()
        self.current_file = None

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.text_browser.setPlainText(f.read())
                self.current_file = file_path
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {e}")

    def save_file(self):
        if not self.current_file:
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Text Files (*.txt);;All Files (*)")
            if not file_path:
                return
            self.current_file = file_path

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.text_browser.toPlainText())
            QMessageBox.information(self, "Успех", "Файл успешно сохранен!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")


# =====================================================================
# Задание №3: Цветовые каналы и поворот (Без Pillow / Чистый PyQt)
# =====================================================================
class Task3Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.original_qimage = None
        self.current_qimage = None

        layout = QVBoxLayout()

        self.btn_open = QPushButton("Выбрать квадратную картинку")
        self.btn_open.clicked.connect(self.open_image_dialog)

        self.img_label = QLabel("Изображение не загружено")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setFixedHeight(300)

        channel_layout = QHBoxLayout()
        self.rb_all = QRadioButton("Все каналы")
        self.rb_r = QRadioButton("Красный (R)")
        self.rb_g = QRadioButton("Зеленый (G)")
        self.rb_b = QRadioButton("Синий (B)")
        self.rb_all.setChecked(True)

        self.channel_group = QButtonGroup()
        self.channel_group.addButton(self.rb_all)
        self.channel_group.addButton(self.rb_r)
        self.channel_group.addButton(self.rb_g)
        self.channel_group.addButton(self.rb_b)
        self.channel_group.buttonClicked.connect(self.update_image)

        channel_layout.addWidget(self.rb_all)
        channel_layout.addWidget(self.rb_r)
        channel_layout.addWidget(self.rb_g)
        channel_layout.addWidget(self.rb_b)

        rotate_layout = QHBoxLayout()
        self.btn_left = QPushButton("<- 90° влево")
        self.btn_right = QPushButton("90° вправо ->")
        self.btn_left.clicked.connect(lambda: self.rotate_image(-90))
        self.btn_right.clicked.connect(lambda: self.rotate_image(90))

        rotate_layout.addWidget(self.btn_left)
        rotate_layout.addWidget(self.btn_right)

        layout.addWidget(self.btn_open)
        layout.addWidget(self.img_label)
        layout.addLayout(channel_layout)
        layout.addLayout(rotate_layout)
        self.setLayout(layout)

    def open_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите квадратное изображение", "",
                                                   "Images (*.png *.jpg *.bmp)")
        if file_path:
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение.")
                return
            if img.width() != img.height():
                QMessageBox.warning(self, "Предупреждение",
                                    "Изображение не квадратное, но будет пропорционально обработано.")
            self.original_qimage = img.convertToFormat(QImage.Format_ARGB32)
            self.current_qimage = QImage(self.original_qimage)
            self.update_image()

    def rotate_image(self, angle):
        if self.current_qimage:
            from PyQt5.QtGui import QTransform
            transform = QTransform().rotate(angle)
            self.current_qimage = self.current_qimage.transformed(transform)
            self.update_image()

    def update_image(self):
        if not self.current_qimage:
            return

        img = QImage(self.current_qimage)

        # Выделение цвета вручную без Pillow
        if not self.rb_all.isChecked():
            for x in range(img.width()):
                for y in range(img.height()):
                    c = QColor(img.pixel(x, y))
                    if self.rb_r.isChecked():
                        img.setPixelColor(x, y, QColor(c.red(), 0, 0, c.alpha()))
                    elif self.rb_g.isChecked():
                        img.setPixelColor(x, y, QColor(0, c.green(), 0, c.alpha()))
                    elif self.rb_b.isChecked():
                        img.setPixelColor(x, y, QColor(0, 0, c.blue(), c.alpha()))

        pixmap = QPixmap.fromImage(img).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setPixmap(pixmap)


# =====================================================================
# Задание №4: Прозрачность (Alpha-канал) (Без Pillow / Чистый PyQt)
# =====================================================================
class Task4Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.original_qimage = None

        layout = QVBoxLayout()
        self.btn_open = QPushButton("Открыть изображение")
        self.btn_open.clicked.connect(self.open_image)

        self.img_label = QLabel("Изображение не загружено")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setFixedHeight(300)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 255)
        self.slider.setValue(255)
        self.slider.valueChanged.connect(self.update_alpha)

        layout.addWidget(self.btn_open)
        layout.addWidget(self.img_label)
        layout.addWidget(QLabel("Прозрачность (Alpha):"))
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение.")
                return
            self.original_qimage = img.convertToFormat(QImage.Format_ARGB32)
            self.update_alpha()

    def update_alpha(self):
        if not self.original_qimage:
            return

        alpha_val = self.slider.value()

        # Создаем прозрачное основание и рисуем исходное изображение с альфа-слоем
        result_image = QImage(self.original_qimage.size(), QImage.Format_ARGB32)
        result_image.fill(Qt.transparent)

        painter = QPainter(result_image)
        painter.setOpacity(alpha_val / 255.0)
        painter.drawImage(0, 0, self.original_qimage)
        painter.end()

        pixmap = QPixmap.fromImage(result_image).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setPixmap(pixmap)


# =====================================================================
# Задание №5: Полосатый флаг (1 балл)
# =====================================================================
class Task5Widget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.btn_generate = QPushButton("Сгенерировать флаг")
        self.btn_generate.clicked.connect(self.generate_flag)

        self.flag_label = QLabel()
        self.flag_label.setAlignment(Qt.AlignCenter)
        self.flag_label.setFixedHeight(300)

        layout.addWidget(self.btn_generate)
        layout.addWidget(self.flag_label)
        self.setLayout(layout)

    def generate_flag(self):
        count, ok = QInputDialog.getInt(self, "Количество полос", "Введите число полос (1-20):", 3, 1, 20)
        if not ok:
            return

        pixmap = QPixmap(400, 250)
        pixmap.fill(QColor("white"))

        painter = QPainter(pixmap)
        stripe_height = 250 / count

        for i in range(count):
            color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            painter.fillRect(0, int(i * stripe_height), 400, int(stripe_height) + 1, color)

        painter.end()
        self.flag_label.setPixmap(pixmap)


# =====================================================================
# Задание №6: Смайлик через QPainter (2 балла)
# =====================================================================
class SmileyCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.face_color = QColor("yellow")
        self.scale_factor = 1.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_x, center_y = width // 2, height // 2

        base_size = min(width, height) * 0.7 * self.scale_factor
        radius = base_size / 2

        # Голова
        painter.setBrush(QBrush(self.face_color))
        painter.setPen(QPen(Qt.black, 3))
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(base_size), int(base_size))

        # Глаза
        eye_w = base_size * 0.12
        eye_h = base_size * 0.18
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(int(center_x - radius * 0.4), int(center_y - radius * 0.3), int(eye_w), int(eye_h))
        painter.drawEllipse(int(center_x + radius * 0.4 - eye_w), int(center_y - radius * 0.3), int(eye_w), int(eye_h))

        # Улыбка
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(Qt.black, 4))
        smile_size = base_size * 0.5
        painter.drawArc(int(center_x - smile_size / 2), int(center_y - smile_size / 4),
                        int(smile_size), int(smile_size), 0 * 16, -180 * 16)


class Task6Widget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.canvas = SmileyCanvas()

        ctrl_layout = QHBoxLayout()
        self.btn_color = QPushButton("Выбрать цвет")
        self.btn_color.clicked.connect(self.choose_color)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(20, 100)
        self.slider.setValue(100)
        self.slider.valueChanged.connect(self.change_scale)

        ctrl_layout.addWidget(self.btn_color)
        ctrl_layout.addWidget(QLabel("Масштаб:"))
        ctrl_layout.addWidget(self.slider)

        layout.addWidget(self.canvas)
        layout.addLayout(ctrl_layout)
        self.setLayout(layout)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.face_color = color
            self.canvas.update()

    def change_scale(self, val):
        self.canvas.scale_factor = val / 100.0
        self.canvas.update()


# =====================================================================
# Задание №7: Фортепиано (2 балла)
# =====================================================================
import winsound

# =====================================================================
# Задание №7: Фортепиано (Системный звук / Без внешних файлов)
# =====================================================================
class Task7Widget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        # Ноты и соответствующая им частота в Герцах (Гц)
        self.notes = {
            'До': 261,
            'Ре': 294,
            'Ми': 329,
            'Фа': 349,
            'Соль': 392,
            'Ля': 440,
            'Си': 493
        }

        for note, freq in self.notes.items():
            btn = QPushButton(note)
            btn.setMinimumHeight(150)
            btn.clicked.connect(lambda checked, f=freq: self.play_sound(f))
            layout.addWidget(btn)

        self.setLayout(layout)

    def play_sound(self, freq):
        # Воспроизводит звук частотой freq Гц длительностью 400 миллисекунд
        winsound.Beep(freq, 400)
# =====================================================================
# Задание №8: L-системы (3 балла)
# =====================================================================
class LSystemCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.axiom = ""
        self.rule = ""
        self.angle_step = 0
        self.iterations = 1
        self.current_string = ""

    def set_system(self, axiom, rule, angle_div):
        self.axiom = axiom
        self.rule = rule
        self.angle_step = 360.0 / angle_div
        self.update_string()

    def set_iterations(self, iters):
        self.iterations = iters
        self.update_string()

    def update_string(self):
        s = self.axiom
        for _ in range(self.iterations):
            next_s = []
            for ch in s:
                if ch == 'F':
                    next_s.append(self.rule)
                else:
                    next_s.append(ch)
            s = "".join(next_s)
        self.current_string = s
        self.update()

    def paintEvent(self, event):
        if not self.current_string:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.darkGreen, 2))

        x, y = self.width() / 2, self.height() / 2
        angle = 0
        step = 8.0 / self.iterations

        stack = []

        for ch in self.current_string:
            if ch == 'F':
                rad = math.radians(angle)
                nx = x + step * math.cos(rad)
                ny = y + step * math.sin(rad)
                painter.drawLine(QPointF(x, y), QPointF(nx, ny))
                x, y = nx, ny
            elif ch == '+':
                angle += self.angle_step
            elif ch == '-':
                angle -= self.angle_step
            elif ch == '[':
                stack.append((x, y, angle))
            elif ch == ']':
                if stack:
                    x, y, angle = stack.pop()


class Task8Widget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.btn_load = QPushButton("Загрузить определение L-системы из файла")
        self.btn_load.clicked.connect(self.load_file)

        self.lbl_title = QLabel("Система не загружена")
        self.lbl_title.setAlignment(Qt.AlignCenter)

        self.canvas = LSystemCanvas()

        slider_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 5)
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self.on_slider_change)

        self.lbl_iter = QLabel("Шаг: 1")
        slider_layout.addWidget(QLabel("Шаги эволюции:"))
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.lbl_iter)

        layout.addWidget(self.btn_load)
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.canvas)
        layout.addLayout(slider_layout)
        self.setLayout(layout)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл L-системы", "",
                                                   "Text Files (*.txt);;All Files (*)")
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            title = lines[0]
            angle_div = int(lines[1])
            axiom = lines[2]
            rule = lines[3]

            self.lbl_title.setText(f"Система: {title}")
            self.canvas.set_system(axiom, rule, angle_div)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный формат файла: {e}")

    def on_slider_change(self, val):
        self.lbl_iter.setText(f"Шаг: {val}")
        self.canvas.set_iterations(val)


# =====================================================================
# Главное окно
# =====================================================================
class Lab3App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа 3")
        self.resize(700, 600)

        main_layout = QVBoxLayout()
        tabs = QTabWidget()

        tabs.addTab(Task1Widget(), "№1 Анализ чисел")
        tabs.addTab(Task2Widget(), "№2 Редактор")
        tabs.addTab(Task3Widget(), "№3 Каналы и Поворот")
        tabs.addTab(Task4Widget(), "№4 Прозрачность")
        tabs.addTab(Task5Widget(), "№5 Полосатый флаг")
        tabs.addTab(Task6Widget(), "№6 Смайлик")
        tabs.addTab(Task7Widget(), "№7 Фортепиано")
        tabs.addTab(Task8Widget(), "№8 L-системы")

        main_layout.addWidget(tabs)
        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Lab3App()
    window.show()
    sys.exit(app.exec_())