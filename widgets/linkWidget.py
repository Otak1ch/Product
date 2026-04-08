import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from baseFunctions.mouse import mouseMove


class LinkWidget(QtWidgets.QWidget, mouseMove):
    def __init__(self, main_app=None):
        super().__init__()
        # Ссылка на главное окно для вызова меню
        self.main_app = main_app

        # 1. Настройки безрамочного прозрачного окна
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Window)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(200, 150)
        self.resize(250, 400)

        # 2. Создаем "Корпус" (MainFrame)
        self.mainFrame = QtWidgets.QFrame(self)
        self.mainFrame.setObjectName("mainFrame")
        self.mainFrame.setStyleSheet("""
            #mainFrame { 
                background-color: #1e1e1e; 
                border-radius: 15px; 
                border: 1px solid #333; 
            }
        """)

        # 3. Настройка адаптивного Layout внутри фрейма
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainFrame)
        self.mainLayout.setContentsMargins(15, 15, 15, 15)
        self.mainLayout.setSpacing(10)

        # Заголовок
        self.label = QtWidgets.QLabel("Мои ссылки")
        self.label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; background: transparent;")
        self.mainLayout.addWidget(self.label)

        # Список ссылок
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setStyleSheet("""
            QListWidget {
                background: transparent; 
                color: #ddd; 
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2a2a2a;
            }
            QListWidget::item:selected {
                background-color: #333;
                border-radius: 5px;
            }
        """)
        # Чтобы список рос вместе с окном
        self.listWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                      QtWidgets.QSizePolicy.Policy.Expanding)
        self.mainLayout.addWidget(self.listWidget)

        # 4. Подключение сигналов
        # Одиночный клик для открытия ссылки
        self.listWidget.itemClicked.connect(self.open_link)

        # Кастомное контекстное меню (ПКМ)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def resizeEvent(self, event):
        """Обеспечивает адаптивность: растягивает фрейм на всё окно."""
        if hasattr(self, 'mainFrame'):
            self.mainFrame.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def open_link(self, item):
        """Открывает URL в браузере по одиночному клику."""
        url = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def add_link_dialog(self):
        """Диалоговые окна для добавления новой ссылки."""
        title, ok1 = QtWidgets.QInputDialog.getText(self, 'Добавить', 'Название ссылки:')
        if ok1 and title:
            url, ok2 = QtWidgets.QInputDialog.getText(self, 'Добавить', 'Вставьте URL:')
            if ok2 and url:
                item = QtWidgets.QListWidgetItem(title)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, url)
                self.listWidget.addItem(item)

    def delete_widget(self):
        """Удаление виджета через главное приложение."""
        if hasattr(self, 'main_app') and self.main_app:
            self.main_app.on_widget_closed(self)
        self.close()

    def show_context_menu(self, pos):
        """Контекстное меню виджета."""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("background-color: #2a2a2a; color: white;")

        add_action = menu.addAction("Добавить ссылку")
        show_main = menu.addAction("Открыть меню")
        remove_widget = menu.addAction("Удалить виджет")

        action = menu.exec(self.mapToGlobal(pos))

        if action == add_action:
            self.add_link_dialog()
        elif action == show_main:
            if self.main_app:
                self.main_app.show()
                self.main_app.raise_()
                self.main_app.activateWindow()
        elif action == remove_widget:
            self.delete_widget()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    test_widget = LinkWidget()
    test_widget.show()
    sys.exit(app.exec())