from PyQt6 import QtWidgets, QtCore, QtGui
from baseFunctions.mouse import mouseMove


class TodoItem(QtWidgets.QWidget):
    def __init__(self, text, parent_item, parent_list, is_done=False, main_app=None):
        super().__init__()
        self.parent_item = parent_item
        self.parent_list = parent_list
        self.main_app = main_app
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)

        self.label = QtWidgets.QLabel(text)
        self.label.setStyleSheet("color: white; border: none; font-size: 13px;")

        self.btn_done = QtWidgets.QPushButton("✓")
        self.btn_done.setFixedSize(22, 22)
        self.btn_done.setStyleSheet("background: #2ecc71; color: white; border-radius: 11px;")
        self.btn_done.clicked.connect(self.mark_done)

        self.btn_del = QtWidgets.QPushButton("✕")
        self.btn_del.setFixedSize(22, 22)
        self.btn_del.setStyleSheet("background: #e74c3c; color: white; border-radius: 11px;")
        self.btn_del.clicked.connect(self.delete_item)

        layout.addWidget(self.btn_done)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.btn_del)

        if is_done: self._apply_style(True)

    def _apply_style(self, is_done):
        f = self.label.font()
        f.setStrikeOut(is_done)
        self.label.setFont(f)
        self.label.setStyleSheet(f"color: {'#888' if is_done else 'white'}; border: none;")

    def mark_done(self):
        is_done = not self.label.font().strikeOut()
        self._apply_style(is_done)
        if self.main_app: self.main_app.save_session()

    def delete_item(self):
        self.parent_list.takeItem(self.parent_list.row(self.parent_item))
        if self.main_app: self.main_app.save_session()


class TodoWidget(QtWidgets.QWidget):
    def __init__(self, main_app=None):
        super().__init__()
        self.main_app = main_app
        self.mouse_move = mouseMove(self)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnBottomHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.resize(300, 400)
        self.mainFrame = QtWidgets.QFrame(self)
        self.mainFrame.setMouseTracking(True)
        self.mainFrame.setStyleSheet("background-color: #1e1e1e; border-radius: 15px; border: 1px solid #333;")

        layout = QtWidgets.QVBoxLayout(self.mainFrame)

        # ЗАГОЛОВОК
        header_layout = QtWidgets.QHBoxLayout()
        self.titleLabel = QtWidgets.QLabel("ЗАДАЧИ:")
        self.titleLabel.setStyleSheet(
            "color: #555; font-weight: bold; font-size: 11px; letter-spacing: 1px; border: none;")

        self.btnAdd = QtWidgets.QPushButton("+")
        self.btnAdd.setFixedSize(24, 24)
        self.btnAdd.setStyleSheet("background: #3498db; color: white; border-radius: 12px; font-weight: bold;")
        self.btnAdd.clicked.connect(self.add_task_dialog)

        header_layout.addWidget(self.titleLabel)
        header_layout.addStretch()
        header_layout.addWidget(self.btnAdd)
        layout.addLayout(header_layout)

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setStyleSheet("background: transparent; border: none; outline: none;")
        layout.addWidget(self.listWidget)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.mouse_move.show_context_menu)

    def add_custom_actions(self, menu):
        add_act = menu.addAction("Добавить задачу")
        add_act.triggered.connect(self.add_task_dialog)

    def add_task_dialog(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Новая задача', 'Что нужно сделать?')
        if ok and text:
            self.add_task(text)
            if self.main_app: self.main_app.save_session()

    def add_task(self, text, is_done=False):
        item = QtWidgets.QListWidgetItem(self.listWidget)
        w = TodoItem(text, item, self.listWidget, is_done, self.main_app)
        item.setSizeHint(w.sizeHint())
        self.listWidget.setItemWidget(item, w)

    def get_content(self):
        tasks = []
        for i in range(self.listWidget.count()):
            w = self.listWidget.itemWidget(self.listWidget.item(i))
            if w: tasks.append({"text": w.label.text(), "done": w.label.font().strikeOut()})
        return tasks

    def load_content(self, data):
        for task in (data or []): self.add_task(task["text"], task.get("done", False))

    def mousePressEvent(self, e):
        if not self.mouse_move.handle_press(e): super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if not self.mouse_move.handle_move(e): super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self.mouse_move.handle_release()
        if self.main_app: self.main_app.save_session()

    def resizeEvent(self, e):
        self.mainFrame.setGeometry(0, 0, self.width(), self.height())