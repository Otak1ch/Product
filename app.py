import sys
import os
import json
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import uic
from PyQt6.QtCore import Qt, QTranslator, QLibraryInfo, QLocale

# Импорты твоих классов
from widgets.firstWidget import FirstWidget
from widgets.colorPicker import ColorPicker
from baseFunctions.mouse import mouseMove


class MainWindow(QWidget, mouseMove):
    def __init__(self):
        super().__init__()

        # 1. Настройка путей
        baseDir = os.path.dirname(__file__)
        uiPath = os.path.join(baseDir, 'data', 'ui', 'app.ui')
        self.config_path = os.path.join(baseDir, 'data', 'config.json')

        # Список для хранения ссылок на открытые виджеты
        self.widgets = []

        # 2. Загрузка интерфейса
        if not os.path.exists(uiPath):
            print(f"Критическая ошибка: Не найден {uiPath}")
            return
        uic.loadUi(uiPath, self)

        # 3. Настройка окна
        self.setObjectName("mainWindow")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.oldPos = None


        # 4. Привязка кнопок
        self.btnClose.clicked.connect(self.hide)

        # Используем универсальный спавн
        self.addFirstWidget.clicked.connect(lambda: self.spawn_widget(FirstWidget))
        self.addColorPicker.clicked.connect(lambda: self.spawn_widget(ColorPicker))

        self.delWidgetBtn.clicked.connect(self.clear_all_widgets)

        # 5. Восстановление сессии
        self.load_session()

    # --- УПРАВЛЕНИЕ ВИДЖЕТАМИ ---

    def spawn_widget(self, widget_class, x=None, y=None):
        """Универсальный метод создания любого виджета"""
        try:
            new_widget = widget_class()

            # Если переданы координаты (из сессии), двигаем виджет
            if x is not None and y is not None:
                new_widget.move(x, y)

            new_widget.show()
            self.widgets.append(new_widget)

            # Важно: передаем сам объект виджета в обработчик закрытия
            new_widget.deleteRequest.connect(self.on_widget_closed)

            self.save_session()
            return new_widget
        except Exception as e:
            print(f"Ошибка при создании виджета {widget_class}: {e}")

    def on_widget_closed(self, widget):
        if widget in self.widgets:
            self.widgets.remove(widget)
            self.save_session()
            print(f"Виджет закрыт. Осталось: {len(self.widgets)}")

    def clear_all_widgets(self):
        for widget in self.widgets[:]:
            widget.close()  # closeEvent сам вызовет удаление из списка
        print("Все виджеты очищены.")

    # --- ОТРИСОВКА ---
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().toRectF()
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), 20, 20)
        painter.fillPath(path, QtGui.QColor(30, 30, 30, 240))
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 30), 1)
        painter.setPen(pen)
        painter.drawPath(path)

    # --- СЕССИЯ ---
    def save_session(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        session_data = {"opened_widgets": []}
        for widget in self.widgets:
            pos = widget.pos()
            data = {
                "type": widget.__class__.__name__,
                "x": pos.x(),
                "y": pos.y()
            }
            if hasattr(widget, 'get_content'):
                data["content"] = widget.get_content()

            session_data["opened_widgets"].append(data)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4)

    def load_session(self):
        if not os.path.exists(self.config_path):
            return

        # Карта классов для восстановления
        widget_map = {
            "FirstWidget": FirstWidget,
            "ColorPicker": ColorPicker
        }

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data.get("opened_widgets", []):
                w_type = item.get("type")
                if w_type in widget_map:
                    new_w = self.spawn_widget(widget_map[w_type], item['x'], item['y'])
                    if "content" in item and hasattr(new_w, 'load_content'):
                        new_w.load_content(item['content'])
        except Exception as e:
            print(f"Ошибка загрузки сессии: {e}")

    def closeEvent(self, event):
        self.save_session()
        event.accept()


# --- ЗАПУСК ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    translator = QTranslator(app)
    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if translator.load(QLocale("ru_RU"), "qtbase", "_", path):
        app.installTranslator(translator)

    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())