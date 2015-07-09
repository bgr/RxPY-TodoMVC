try:
    from PyQt4.QtGui import QLineEdit, QVBoxLayout, QLabel, QHBoxLayout, \
        QWidget, QCheckBox, QPushButton
except ImportError:
    from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QLabel, QHBoxLayout, \
        QWidget, QCheckBox, QPushButton
    from PyQt5.QtGui import QIcon

import rx


class MainPresenter:

    def __init__(self, view, model):
        self._item_presenters = []

        self.view = view
        self.view.textbox.returnPressed.connect(self._add_todo)
        self.model = model
        self.model.todo_stream.subscribe(self._update_view)
        self.model.uncompleted_stream\
            .map(lambda items: "{} item{} left".format(
                len(items), "s" if len(items) > 1 else ""))\
            .subscribe(self.view.count_label.setText)
        self.model.todo_stream\
            .map(lambda items: len(items) > 0)\
            .subscribe(self.view.footer.setVisible)

    def _add_todo(self):
        text = self.view.textbox.text().strip()
        if text:
            self.view.textbox.clear()
            self.model.add_todo(text)

    def _update_view(self, todos):
        # Clear layout
        for _ in range(self.view.todo_layout.count()):
            widget = self.view.todo_layout.takeAt(0).widget()
            widget.setParent(None)
            del widget
        self._item_presenters.clear()

        # Refresh todo widgets
        for todo in todos:
            presenter = TodoItemPresenter(todo)
            self.view.todo_layout.addWidget(presenter.view)
            self._item_presenters.append(presenter)


class MainView(QWidget):

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("RxPY TodoMVC")

        # Used to enter text for a new todo list item
        self.textbox = QLineEdit()

        # Holds individual widgets for each todo item
        self.todo_layout = QVBoxLayout()

        self.count_label = QLabel()

        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.count_label)
        footer_layout.addStretch(1)

        self.footer = QWidget()
        self.footer.setLayout(footer_layout)
        self.footer.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.textbox)
        layout.addLayout(self.todo_layout)
        layout.addWidget(self.footer)
        layout.addStretch(1)
        self.setLayout(layout)


class TodoItemPresenter:

    def __init__(self, model, view=None):
        self.view = view or TodoItemView()
        self.model = model
        self.model.text_stream.subscribe(self.view.label.setText)
        self.model.completed_stream.subscribe(self.view.check.setChecked)

        self.view.check.clicked.connect(self.model.completed_stream.on_next)
        self.view.is_hover_stream.subscribe(
            lambda is_hover: self.view.delete_button.setVisible(is_hover))

        self.view.delete_button.pressed.connect(self.model.delete)


class TodoItemView(QWidget):

    def __init__(self):
        super().__init__()
        self.check = QCheckBox()
        self.label = QLabel()
        self.delete_button = QPushButton(
            QIcon.fromTheme("edit-delete"), "Delete")

        layout = QHBoxLayout()
        layout.addWidget(self.check)
        layout.addWidget(self.label)
        layout.addStretch(1)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

        self.setMouseTracking(True)
        self.is_hover_stream = rx.subjects.BehaviorSubject(False)

    def enterEvent(self, event):
        self.is_hover_stream.on_next(True)

    def leaveEvent(self, event):
        self.is_hover_stream.on_next(False)
