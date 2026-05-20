import os
from PyQt6 import QtWidgets, QtCore, QtGui
from baseFunctions.mouse import mouseMove


class LinkWidget(QtWidgets.QWidget):
    def __init__(self, main_app=None):
        super().__init__()
        self.main_app = main_app
        self.mouse_move = mouseMove(self)

        # Настройки окна: без рамки + всегда внизу
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnBottomHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # Включаем отслеживание мыши
        self.setMouseTracking(True)
        self.resize(250, 400)

        self.mainFrame = QtWidgets.QFrame(self)
        self.mainFrame.setMouseTracking(True)
        self.mainFrame.setObjectName("linkMainFrame")
        self.mainFrame.setStyleSheet(
            "#linkMainFrame { background-color: #1e1e1e; border-radius: 15px; border: 1px solid #333; }")

        layout = QtWidgets.QVBoxLayout(self.mainFrame)
        label = QtWidgets.QLabel("Мои ссылки")
        label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background: transparent;")
        layout.addWidget(label)

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setStyleSheet("background: transparent; color: #ddd; border: none; outline: none;")
        self.listWidget.itemClicked.connect(self.open_link)
        layout.addWidget(self.listWidget)

        # Контекстное меню через mouse_move
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.mouse_move.show_context_menu)


    def add_custom_actions(self, menu):
        add_act = menu.addAction("Добавить ссылку")
        add_act.triggered.connect(self.add_link_dialog)

    # --- ОБРАБОТКА МЫШИ ---
    def mousePressEvent(self, event):
        if not self.mouse_move.handle_press(event):
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.mouse_move.handle_move(event):
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouse_move.handle_release()
        if self.main_app: self.main_app.save_session()
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        self.mainFrame.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    # --- ЛОГИКА ССЫЛОК ---
    def open_link(self, item):
        url = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if url:
            if not url.startswith(('http://', 'https://')): url = 'https://' + url
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def add_link_dialog(self):
        title, ok1 = QtWidgets.QInputDialog.getText(self, 'Новая ссылка', 'Название:')
        if ok1 and title:
            url, ok2 = QtWidgets.QInputDialog.getText(self, 'Новая ссылка', 'URL:')
            if ok2 and url:
                item = QtWidgets.QListWidgetItem(title)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, url)
                self.listWidget.addItem(item)
                if self.main_app: self.main_app.save_session()

    def get_content(self):
        links = []
        for i in range(self.listWidget.count()):
            it = self.listWidget.item(i)
            links.append({"title": it.text(), "url": it.data(QtCore.Qt.ItemDataRole.UserRole)})
        return links

    def load_content(self, data):
        if not data: return
        for l in data:
            it = QtWidgets.QListWidgetItem(l["title"])
            it.setData(QtCore.Qt.ItemDataRole.UserRole, l["url"])
            self.listWidget.addItem(it)