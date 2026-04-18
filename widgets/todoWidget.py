from PyQt6 import QtWidgets, QtCore, QtGui
from baseFunctions.mouse import mouseMove


class TodoItem(QtWidgets.QWidget):
    def __init__(self, text, parent_list_item, parent_list_widget, is_done=False, main_app=None):
        super().__init__()
        self.parent_item = parent_list_item
        self.parent_list = parent_list_widget
        self.main_app = main_app

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.label = QtWidgets.QLabel(text)
        self.label.setStyleSheet("color: white; font-size: 13px; background: transparent;")

        self.btn_done = QtWidgets.QPushButton("✓")
        self.btn_done.setFixedSize(24, 24)
        self.btn_done.setStyleSheet("background: #2ecc71; color: white; border-radius: 12px; border: none;")
        self.btn_done.clicked.connect(self.mark_done)

        self.btn_delete = QtWidgets.QPushButton("✕")
        self.btn_delete.setFixedSize(24, 24)
        self.btn_delete.setStyleSheet("background: #e74c3c; color: white; border-radius: 12px; border: none;")
        self.btn_delete.clicked.connect(self.delete_item)

        layout.addWidget(self.btn_done)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.btn_delete)
        if is_done: self._apply_style(True)

    def _apply_style(self, is_done):
        font = self.label.font();
        font.setStrikeOut(is_done);
        self.label.setFont(font)
        self.label.setStyleSheet(f"color: rgba(255, 255, 255, {0.5 if is_done else 1.0}); background: transparent;")

    def mark_done(self):
        self._apply_style(not self.label.font().strikeOut())
        if self.main_app: self.main_app.save_session()

    def delete_item(self):
        self.parent_list.takeItem(self.parent_list.row(self.parent_item))
        if self.main_app: self.main_app.save_session()


class TodoWidget(QtWidgets.QWidget):
    def __init__(self, main_app=None):
        super().__init__()
        self.main_app = main_app
        self.mouse_move = mouseMove(self)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(300, 450)

        self.mainFrame = QtWidgets.QFrame(self)
        self.mainFrame.setObjectName("todoMainFrame")
        self.mainFrame.setStyleSheet(
            "#todoMainFrame { background-color: #1e1e1e; border-radius: 20px; border: 1px solid #333; }")

        layout = QtWidgets.QVBoxLayout(self.mainFrame)
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Задачи")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        btn_add = QtWidgets.QPushButton("+")
        btn_add.setFixedSize(28, 28)
        btn_add.clicked.connect(self.add_task_dialog)
        header.addWidget(title);
        header.addStretch();
        header.addWidget(btn_add)
        layout.addLayout(header)

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.listWidget)

    def mousePressEvent(self, event):
        if not self.mouse_move.handle_press(event): super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.mouse_move.handle_move(event): super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.mouse_move.handle_release()
        if self.main_app: self.main_app.save_session()
        super().mouseReleaseEvent(event)

    def add_task_dialog(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Todo', 'Что добавить?')
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

    def resizeEvent(self, event):
        self.mainFrame.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)